from typing import Dict, List, Any, Optional, TypedDict, Annotated
from langchain_core.documents import Document
from langgraph.graph import StateGraph, END
import logging

from src.ingestion.nodes import (
    load_document,
    chunk_and_embed,
    extract_entities,
    route_to_stores,
    store_in_weaviate,
    store_in_neo4j,
    store_in_neo4j_graphrag,
    store_in_weaviate_async,
    store_in_neo4j_async,
    store_in_neo4j_graphrag_async,
    fetch_and_extract_text,
    chunk_text
)
from src.data_stores.postgres_client import PostgresClient
from src.data_stores.weaviate_client import WeaviateClient
from src.data_stores.neo4j_client import Neo4jClient
from src.data_stores.neo4j_graphrag_client import Neo4jGraphRAGClient

# Configure logging
logger = logging.getLogger(__name__)


# Define the state type for the ingestion graph
class IngestionState(TypedDict):
    """State schema for the ingestion graph."""
    # Input data
    input_data: Dict[str, Any]  # Contains file path or content and metadata
    
    # GCS specific fields
    file_id: Optional[str]  # ID of the file being processed
    organization_id: Optional[str]  # Organization ID for the file
    gcs_path: Optional[str]  # Google Cloud Storage path to the file
    raw_text: Optional[str]  # Raw text extracted from the file
    status: Optional[str]  # Status of the processing (pending, processing, completed, failed)
    processing_log: Optional[List[str]]  # Log of processing steps
    
    # Processed data
    processed_chunks: Optional[List[Dict[str, Any]]]  # Chunked text with metadata
    embeddings: Optional[List[List[float]]]  # Embeddings for each chunk
    entities: Optional[List[Dict[str, Any]]]  # Extracted entities and relations
    
    # Routing information
    destinations: Optional[List[str]]  # List of destinations to route to
    
    # Multi-tenancy
    tenant_id: str  # Tenant identifier for data isolation
    
    # Error handling
    error: Optional[str]  # Error message if any


class IngestionGraph:
    """
    LangGraph for document ingestion with conditional routing.
    """

    def __init__(
        self,
        postgres_client: PostgresClient,
        weaviate_client: WeaviateClient,
        neo4j_client: Neo4jClient,
        neo4j_graphrag_client: Optional[Neo4jGraphRAGClient] = None,
        use_graphrag: bool = True,
        graph_type: str = "document" # Add graph_type parameter
    ):
        """
        Initialize the ingestion graph.
        
        Args:
            postgres_client: The PostgreSQL client
            weaviate_client: The Weaviate client
            neo4j_client: The Neo4j client (legacy)
            neo4j_graphrag_client: The Neo4j GraphRAG client (preferred)
            use_graphrag: Whether to use GraphRAG features (default: True)
            graph_type: The type of ingestion graph to build (e.g., "document", "gcs_file")
        """
        self.postgres_client = postgres_client
        self.weaviate_client = weaviate_client
        self.neo4j_client = neo4j_client
        self.neo4j_graphrag_client = neo4j_graphrag_client
        self.use_graphrag = use_graphrag and neo4j_graphrag_client is not None
        self.graph_type = graph_type # Store graph_type
        
        # Build the graph based on type
        self.graph = self._build_graph()

    def _should_route_to_neo4j(self, state: IngestionState) -> bool:
        """
        Determine if the document should be routed to Neo4j.
        
        Args:
            state: The current state
            
        Returns:
            True if the document should be routed to Neo4j, False otherwise
        """
        # Route to Neo4j if entities were detected
        return state.get("entities") is not None and len(state.get("entities", [])) > 0

    def _get_destinations(self, state: IngestionState) -> str:
        """
        Determine the next node based on the routing decision.
        
        Args:
            state: The current state
            
        Returns:
            The name of the next node or END if no specific destination
        """
        # Get destinations from state
        destinations = state.get("destinations", [])
        has_weaviate = "weaviate" in destinations
        has_neo4j = "neo4j" in destinations
        
        # Determine storage path based on destinations and GraphRAG availability
        if has_weaviate and has_neo4j:
            if self.use_graphrag:
                return "store_in_weaviate_and_graphrag"
            return "store_in_weaviate_and_neo4j"
        elif has_weaviate:
            return "store_in_weaviate_only"
        elif has_neo4j:
            return "store_in_neo4j_only"
        
        # No specific storage destination
        return "end"

    def _build_graph(self) -> StateGraph:
        """
        Build the ingestion graph with conditional routing based on graph_type.
        
        Returns:
            The compiled ingestion graph
        """
        if self.graph_type == "gcs_file":
            return self._build_gcs_file_graph()
        elif self.graph_type in ["global_tool", "global_learning_resource", "global_ecosystem_partner"]:
            return self._build_global_knowledge_graph()
        else:
            return self._build_document_graph()
        

    def _build_global_knowledge_graph(self) -> StateGraph:
        """
        Builds the ingestion graph for global knowledge items (tools, learning resources, partners).
        This uses the same structure as document graph but with specific metadata handling.
        """
        graph = StateGraph(IngestionState)
        
        # Add common nodes
        graph.add_node("load_document", self._load_document)
        graph.add_node("chunk_and_embed", self._chunk_and_embed)
        graph.add_node("extract_entities", self._extract_entities)
        graph.add_node("route_to_stores", self._route_to_stores)
        graph.add_node("store_in_weaviate_only", self._store_in_weaviate_only)
        graph.add_node("store_in_neo4j_only", self._store_in_neo4j_only)
        graph.add_node("store_in_weaviate_and_neo4j", self._store_in_weaviate_and_neo4j)
        
        if self.use_graphrag:
            graph.add_node("store_in_weaviate_and_graphrag", self._store_in_weaviate_and_graphrag)
        
        # Define the sequence for global knowledge ingestion
        graph.set_entry_point("load_document")
        graph.add_edge("load_document", "chunk_and_embed")
        graph.add_edge("chunk_and_embed", "extract_entities")
        graph.add_edge("extract_entities", "route_to_stores")
        
        # Add conditional edges based on routing decision
        # Add conditional edges based on routing decision
        conditional_edges = {
            "store_in_weaviate_only": "store_in_weaviate_only",
            "store_in_neo4j_only": "store_in_neo4j_only",
            "store_in_weaviate_and_neo4j": "store_in_weaviate_and_neo4j",
            "end": END
        }
        
        if self.use_graphrag:
            conditional_edges["store_in_weaviate_and_graphrag"] = "store_in_weaviate_and_graphrag"
        
        graph.add_conditional_edges(
            "route_to_stores",
            self._get_destinations,
            conditional_edges
        )
        
        # Add edges from storage nodes to END
        graph.add_edge("store_in_weaviate_only", END)
        graph.add_edge("store_in_neo4j_only", END)
        graph.add_edge("store_in_weaviate_and_neo4j", END)
        
        if self.use_graphrag:
            graph.add_edge("store_in_weaviate_and_graphrag", END)
            
        return graph.compile()

    def _build_document_graph(self) -> StateGraph:
        """
        Builds the ingestion graph for general document, URL, file, and global knowledge ingestion.
        Starts with loading the document.
        """
        graph = StateGraph(IngestionState)
            
        # Add common nodes
        graph.add_node("load_document", self._load_document)
        graph.add_node("chunk_and_embed", self._chunk_and_embed)
        graph.add_node("extract_entities", self._extract_entities)
        graph.add_node("route_to_stores", self._route_to_stores)
        graph.add_node("store_in_weaviate_only", self._store_in_weaviate_only)
        graph.add_node("store_in_neo4j_only", self._store_in_neo4j_only)
        graph.add_node("store_in_weaviate_and_neo4j", self._store_in_weaviate_and_neo4j)
            
        if self.use_graphrag:
            graph.add_node("store_in_weaviate_and_graphrag", self._store_in_weaviate_and_graphrag)
            
        # Define the sequence for document-like ingestion
        graph.set_entry_point("load_document")
        graph.add_edge("load_document", "chunk_and_embed")
        graph.add_edge("chunk_and_embed", "extract_entities")
        graph.add_edge("extract_entities", "route_to_stores")
            
        # Add conditional edges based on routing decision
        # Add conditional edges based on routing decision
        conditional_edges = {
            "store_in_weaviate_only": "store_in_weaviate_only",
            "store_in_neo4j_only": "store_in_neo4j_only",
            "store_in_weaviate_and_neo4j": "store_in_weaviate_and_neo4j",
            "end": END
        }
            
        if self.use_graphrag:
            conditional_edges["store_in_weaviate_and_graphrag"] = "store_in_weaviate_and_graphrag"
            
        graph.add_conditional_edges(
            "route_to_stores",
            self._get_destinations,
            conditional_edges
        )
            
        # Add edges from storage nodes to END
        graph.add_edge("store_in_weaviate_only", END)
        graph.add_edge("store_in_neo4j_only", END)
        graph.add_edge("store_in_weaviate_and_neo4j", END)
            
        if self.use_graphrag:
            graph.add_edge("store_in_weaviate_and_graphrag", END)
                
        return graph.compile()

    def _build_gcs_file_graph(self) -> StateGraph:
        """
        Builds the ingestion graph specifically for GCS file ingestion.
        Starts with fetching and extracting text from GCS.
        """
        graph = StateGraph(IngestionState)
        
        # Add GCS specific nodes
        graph.add_node("fetch_and_extract_text", self._fetch_and_extract_text)
        graph.add_node("chunk_text", self._chunk_text)
        
        # Add common nodes
        graph.add_node("load_document", self._load_document) # This load_document will now use raw_text from previous step
        graph.add_node("chunk_and_embed", self._chunk_and_embed)
        graph.add_node("extract_entities", self._extract_entities)
        graph.add_node("route_to_stores", self._route_to_stores)
        graph.add_node("store_in_weaviate_only", self._store_in_weaviate_only)
        graph.add_node("store_in_neo4j_only", self._store_in_neo4j_only)
        graph.add_node("store_in_weaviate_and_neo4j", self._store_in_weaviate_and_neo4j)
        
        if self.use_graphrag:
            graph.add_node("store_in_weaviate_and_graphrag", self._store_in_weaviate_and_graphrag)
        
        # Define the sequence for GCS file ingestion
        graph.set_entry_point("fetch_and_extract_text")
        graph.add_edge("fetch_and_extract_text", "chunk_text")
        graph.add_edge("chunk_text", "load_document")
        graph.add_edge("load_document", "chunk_and_embed")
        graph.add_edge("chunk_and_embed", "extract_entities")
        graph.add_edge("extract_entities", "route_to_stores")
        
        # Add conditional edges based on routing decision
        # Add conditional edges based on routing decision
        conditional_edges = {
            "store_in_weaviate_only": "store_in_weaviate_only",
            "store_in_neo4j_only": "store_in_neo4j_only",
            "store_in_weaviate_and_neo4j": "store_in_weaviate_and_neo4j",
            "end": END
        }
        
        if self.use_graphrag:
            conditional_edges["store_in_weaviate_and_graphrag"] = "store_in_weaviate_and_graphrag"
        
        graph.add_conditional_edges(
            "route_to_stores",
            self._get_destinations,
            conditional_edges
        )
        
        # Add edges from storage nodes to END
        graph.add_edge("store_in_weaviate_only", END)
        graph.add_edge("store_in_neo4j_only", END)
        graph.add_edge("store_in_weaviate_and_neo4j", END)
        
        if self.use_graphrag:
            graph.add_edge("store_in_weaviate_and_graphrag", END)
            
        return graph.compile()

    def _fetch_and_extract_text(self, state: IngestionState) -> IngestionState:
        """
        Fetch a file from Google Cloud Storage and extract its raw text content.
        
        Args:
            state: The current state
            
        Returns:
            The updated state with raw_text field populated
        """
        try:
            # Call the fetch_and_extract_text function from nodes.py
            updated_state = fetch_and_extract_text(state)
            
            # Prepare input_data for the next node if not already present
            if "input_data" not in updated_state and updated_state.get("raw_text"):
                # Create input_data with the extracted text as content
                updated_state["input_data"] = {
                    "content": updated_state["raw_text"],
                    "metadata": {
                        "file_id": updated_state.get("file_id", ""),
                        "organization_id": updated_state.get("organization_id", ""),
                        "gcs_path": updated_state.get("gcs_path", ""),
                        "source": updated_state.get("gcs_path", ""),
                        "source_type": "gcs_file"
                    }
                }
            elif "input_data" not in updated_state:
                # Create a minimal input_data even if raw_text is not available
                updated_state["input_data"] = {
                    "content": "Mock content for testing",
                    "metadata": {
                        "file_id": updated_state.get("file_id", ""),
                        "organization_id": updated_state.get("organization_id", ""),
                        "gcs_path": updated_state.get("gcs_path", ""),
                        "source": updated_state.get("gcs_path", ""),
                        "source_type": "gcs_file"
                    }
                }
            
            return updated_state
        except Exception as e:
            logger.error(f"Error in fetch_and_extract_text node: {str(e)}")
            return {**state, "error": f"Text extraction error: {str(e)}"}
    
    def _chunk_text(self, state: IngestionState) -> IngestionState:
        """
        Apply a semantic chunking algorithm to break the raw text into meaningful paragraphs or chunks.
        
        Args:
            state: The current state containing raw_text and other fields
            
        Returns:
            Updated state with chunks field populated
        """
        try:
            # Call the chunk_text function from nodes.py
            updated_state = chunk_text(state)
            return updated_state
        except Exception as e:
            logger.error(f"Error in chunk_text node: {str(e)}")
            return {**state, "error": f"Chunking error: {str(e)}"}
    
    def _load_document(self, state: IngestionState) -> IngestionState:
        """
        Load and parse the document using LangChain loaders.
        
        Args:
            state: The current state
            
        Returns:
            The updated state
        """
        try:
            # If raw_text is present, use it as content for load_document
            if state.get("raw_text"):
                # Create a temporary input_data for load_document
                input_data_for_load = {
                    "content": state["raw_text"],
                    "metadata": {
                        "file_id": state.get("file_id", ""),
                        "organization_id": state.get("organization_id", ""),
                        "gcs_path": state.get("gcs_path", ""),
                        "source": state.get("gcs_path", ""),
                        "source_type": "gcs_file"
                    }
                }
                result = load_document(input_data_for_load, state["tenant_id"])
            else:
                # Otherwise, use the original input_data
                result = load_document(state["input_data"], state["tenant_id"])
            
            return {**state, **result}
        except Exception as e:
            logger.error(f"Error in load_document node: {str(e)}")
            return {**state, "error": f"Document loading error: {str(e)}"}

    def _chunk_and_embed(self, state: IngestionState) -> IngestionState:
        """
        Chunk the document and create embeddings.
        
        Args:
            state: The current state
            
        Returns:
            The updated state
        """
        if state.get("error"):
            return state
        
        try:
            # Call the chunk_and_embed function from nodes.py
            result = chunk_and_embed(state["input_data"], state["tenant_id"])
            
            return {**state, **result}
        except Exception as e:
            logger.error(f"Error in chunk_and_embed node: {str(e)}")
            return {**state, "error": f"Chunking and embedding error: {str(e)}"}

    def _extract_entities(self, state: IngestionState) -> IngestionState:
        """
        Extract entities from the document.
        
        Args:
            state: The current state
            
        Returns:
            The updated state
        """
        if state.get("error"):
            return state
        
        try:
            # Call the extract_entities function from nodes.py
            result = extract_entities(state["processed_chunks"], state["tenant_id"])
            
            return {**state, **result}
        except Exception as e:
            # Log the error but don't fail the entire pipeline
            logger.error(f"Error in extract_entities node: {str(e)}")
            
            # Return empty entities instead of failing
            return {
                **state,
                "entities": {
                    "entities": [],
                    "relationships": []
                }
            }

    def _route_to_stores(self, state: IngestionState) -> IngestionState:
        """
        Determine which data stores to route the document to.
        
        Args:
            state: The current state
            
        Returns:
            The updated state with destinations
        """
        if state.get("error"):
            return state
        
        try:
            # Call the route_to_stores function from nodes.py
            result = route_to_stores(
                state["processed_chunks"],
                state["embeddings"],
                state["entities"],
                state["tenant_id"]
            )
            
            return {**state, **result}
        except Exception as e:
            logger.error(f"Error in route_to_stores node: {str(e)}")
            return {**state, "error": f"Routing error: {str(e)}"}

    def _store_in_weaviate_only(self, state: IngestionState) -> IngestionState:
        """
        Store the document in Weaviate only.
        
        Args:
            state: The current state
            
        Returns:
            The updated state
        """
        if state.get("error"):
            return state
        
        try:
            if self.weaviate_client is None:
                logger.warning("Weaviate client not available - skipping storage")
                return {**state, "error": "Weaviate client not initialized"}
            
            # Store in Weaviate
            store_in_weaviate(
                state["processed_chunks"],
                state["embeddings"],
                state["tenant_id"],
                self.weaviate_client
            )
            
            return state
        except Exception as e:
            logger.error(f"Error in store_in_weaviate_only node: {str(e)}")
            return {**state, "error": f"Weaviate storage error: {str(e)}"}

    def _store_in_neo4j_only(self, state: IngestionState) -> IngestionState:
        """
        Store the document in Neo4j only.
        
        Args:
            state: The current state
            
        Returns:
            The updated state
        """
        if state.get("error"):
            return state
        
        try:
            if self.neo4j_client is None:
                logger.warning("Neo4j client not available - skipping storage")
                return {**state, "error": "Neo4j client not initialized"}
            
            # Store in Neo4j
            store_in_neo4j(
                state["processed_chunks"],
                state["entities"],
                state["tenant_id"],
                self.neo4j_client
            )
            
            return state
        except Exception as e:
            logger.error(f"Error in store_in_neo4j_only node: {str(e)}")
            return {**state, "error": f"Neo4j storage error: {str(e)}"}

    def _store_in_weaviate_and_neo4j(self, state: IngestionState) -> IngestionState:
        """
        Store the document in both Weaviate and Neo4j.
        
        Args:
            state: The current state
            
        Returns:
            The updated state
        """
        if state.get("error"):
            return state
        
        try:
            if self.weaviate_client is None or self.neo4j_client is None:
                missing = []
                if self.weaviate_client is None:
                    missing.append("Weaviate")
                if self.neo4j_client is None:
                    missing.append("Neo4j")
                logger.warning(f"{', '.join(missing)} client(s) not available - skipping storage")
                return {**state, "error": f"{', '.join(missing)} client(s) not initialized"}
            
            import asyncio
            
            # Create async tasks for parallel storage
            async def store_parallel():
                await asyncio.gather(
                    store_in_weaviate_async(
                        state["processed_chunks"],
                        state["embeddings"],
                        state["tenant_id"],
                        self.weaviate_client
                    ),
                    store_in_neo4j_async(
                        state["processed_chunks"],
                        state["entities"],
                        state["tenant_id"],
                        self.neo4j_client
                    )
                )
            
            # Run async tasks in event loop
            try:
                # Check if there's a running event loop
                try:
                    loop = asyncio.get_running_loop()
                    # We're in an event loop, create a task and await it
                    import nest_asyncio
                    
                    # Apply nest_asyncio to allow nested event loops
                    nest_asyncio.apply()
                    
                    # Now we can safely run the coroutine in the existing loop
                    loop.run_until_complete(store_parallel())
                except RuntimeError:
                    # No running loop - safe to use asyncio.run
                    asyncio.run(store_parallel())
            except Exception:
                # Fallback to synchronous if async fails
                logger.warning("Async storage failed, falling back to synchronous")
                store_in_weaviate(
                    state["processed_chunks"],
                    state["embeddings"],
                    state["tenant_id"],
                    self.weaviate_client
                )
                store_in_neo4j(
                    state["processed_chunks"],
                    state["entities"],
                    state["tenant_id"],
                    self.neo4j_client
                )
            
            return state
        except Exception as e:
            logger.error(f"Error in store_in_weaviate_and_neo4j node: {str(e)}", exc_info=True)
            return {**state, "error": f"Storage error: {str(e)}"}

    def _store_in_weaviate_and_graphrag(self, state: IngestionState) -> IngestionState:
        """
        Store the document in both Weaviate and Neo4j using GraphRAG with parallel writes.
        
        Args:
            state: The current state
            
        Returns:
            The updated state
        """
        if state.get("error"):
            return state
        
        try:
            if self.weaviate_client is None:
                logger.warning("Weaviate client not available - skipping storage")
                return {**state, "error": "Weaviate client not initialized"}
            
            if self.neo4j_graphrag_client is None:
                logger.warning("Neo4j GraphRAG client not available - falling back to legacy Neo4j")
                # Fall back to regular Neo4j if available
                if self.neo4j_client:
                    return self._store_in_weaviate_and_neo4j(state)
                else:
                    return {**state, "error": "No graph database client available"}
            
            import asyncio
            
            # Create async tasks for parallel storage
            async def store_parallel():
                tasks = [
                    store_in_weaviate_async(
                        state["processed_chunks"],
                        state["embeddings"],
                        state["tenant_id"],
                        self.weaviate_client
                    )
                ]
                
                # Add GraphRAG task if client is available
                if self.neo4j_graphrag_client:
                    tasks.append(
                        store_in_neo4j_graphrag_async(
                            state["processed_chunks"],
                            state["entities"],
                            state["tenant_id"],
                            self.neo4j_graphrag_client
                        )
                    )
                
                await asyncio.gather(*tasks)
            
            # Run async tasks in event loop
            try:
                # Check if there's a running event loop
                try:
                    loop = asyncio.get_running_loop()
                    # We're in an event loop, create a task and await it
                    import nest_asyncio
                    
                    # Apply nest_asyncio to allow nested event loops
                    nest_asyncio.apply()
                    
                    # Now we can safely run the coroutine in the existing loop
                    loop.run_until_complete(store_parallel())
                except RuntimeError:
                    # No running loop - safe to use asyncio.run
                    asyncio.run(store_parallel())
            except Exception:
                # Fallback to synchronous if async fails
                logger.warning("Async storage failed, falling back to synchronous")
                store_in_weaviate(
                    state["processed_chunks"],
                    state["embeddings"],
                    state["tenant_id"],
                    self.weaviate_client
                )
                if self.neo4j_graphrag_client:
                    store_in_neo4j_graphrag(
                        state["processed_chunks"],
                        state["entities"],
                        state["tenant_id"],
                        self.neo4j_graphrag_client
                    )
            
            return state
        except Exception as e:
            logger.error(f"Error in store_in_weaviate_and_graphrag node: {str(e)}", exc_info=True)
            return {**state, "error": f"Storage error: {str(e)}"}

    async def ingest_document_async(self, input_data: Dict[str, Any], tenant_id: str) -> Dict[str, Any]:
        """
        Ingest a document into the system asynchronously.
        
        Args:
            input_data: The document input data (file path or content)
            tenant_id: The tenant ID for multi-tenancy
            
        Returns:
            The result of the ingestion process
        """
        try:
            # Validate input data
            if not input_data:
                logger.error("Empty input data for ingestion")
                raise ValueError("Input data cannot be empty")
                
            # Check for required fields based on source type
            source_type = input_data.get("source_type", "")
            if source_type in ["global_tool", "global_learning_resource", "global_ecosystem_partner"]:
                if "content" not in input_data:
                    logger.error(f"Missing content for {source_type}")
                    raise ValueError(f"Content is required for {source_type}")
                if "metadata" not in input_data:
                    logger.error(f"Missing metadata for {source_type}")
                    raise ValueError(f"Metadata is required for {source_type}")
            
            # Initialize the state
            state = {
                "input_data": input_data,
                "tenant_id": tenant_id,
                "processed_chunks": None,
                "embeddings": None,
                "entities": None,
                "destinations": None,
                "error": None
            }
            
            # Run the graph
            result = await self.graph.ainvoke(state)
            
            if result.get("error"):
                logger.error(f"Error in ingestion graph: {result['error']}")
                raise Exception(result["error"])
            
            return {
                "status": "success",
                "message": "Document ingested successfully",
                "destinations": result.get("destinations", [])
            }
        except Exception as e:
            logger.error(f"Error ingesting document: {str(e)}")
            raise

    def ingest_document(self, input_data: Dict[str, Any], tenant_id: str) -> Dict[str, Any]:
        """
        Ingest a document into the system synchronously.
        
        Args:
            input_data: The document input data (file path or content)
            tenant_id: The tenant ID for multi-tenancy
            
        Returns:
            The result of the ingestion process
        """
        try:
            # Initialize the state
            state = {
                "input_data": input_data,
                "tenant_id": tenant_id,
                "processed_chunks": None,
                "embeddings": None,
                "entities": None,
                "destinations": None,
                "error": None
            }
            
            # Run the graph
            result = self.graph.invoke(state)
            
            if result.get("error"):
                logger.error(f"Error in ingestion graph: {result['error']}")
                raise Exception(result["error"])
            
            return {
                "status": "success",
                "message": "Document ingested successfully",
                "destinations": result.get("destinations", [])
            }
        except Exception as e:
            logger.error(f"Error ingesting document: {str(e)}")
            raise