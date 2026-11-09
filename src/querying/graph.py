from typing import Dict, List, Any, Optional, TypedDict, Annotated
from langgraph.graph import StateGraph, END
import logging
from openai import OpenAI

from src.core.config import settings
from src.data_stores.postgres_client import PostgresClient
from src.data_stores.weaviate_client import WeaviateClient
from src.data_stores.neo4j_client import Neo4jClient
from src.data_stores.neo4j_graphrag_client import Neo4jGraphRAGClient
from src.querying.tools.vector_search import VectorSearchTool
from src.querying.tools.graph_retrieval import GraphRetrievalTool

# Configure logging
logger = logging.getLogger(__name__)


# Define the state type for the query graph
class QueryState(TypedDict):
    """State schema for the query graph."""
    # Input data
    query: str  # User query
    filters: Optional[Dict[str, Any]]  # Optional filters
    top_k: int  # Number of results to return
    
    # Processing state
    vector_results: Optional[List[Dict[str, Any]]]  # Results from vector search
    graph_results: Optional[List[Dict[str, Any]]]  # Results from graph search
    combined_results: Optional[List[Dict[str, Any]]]  # Combined results
    
    # Multi-tenancy
    tenant_id: str  # Tenant identifier for data isolation
    
    # Output
    answer: Optional[str]  # Final answer
    citations: Optional[List[Dict[str, Any]]]  # Citations for the answer
    
    # Error handling
    error: Optional[str]  # Error message if any


class QueryGraph:
    """
    LangGraph for query processing with multiple retrieval methods.
    """

    def __init__(
        self,
        postgres_client: PostgresClient,
        weaviate_client: WeaviateClient,
        neo4j_client: Neo4jClient,
        neo4j_graphrag_client: Optional[Neo4jGraphRAGClient] = None,
        use_graphrag: bool = True
    ):
        """
        Initialize the query graph.
        
        Args:
            postgres_client: The PostgreSQL client
            weaviate_client: The Weaviate client
            neo4j_client: The Neo4j client (legacy)
            neo4j_graphrag_client: The Neo4j GraphRAG client (preferred)
            use_graphrag: Whether to use GraphRAG features (default: True)
        """
        self.postgres_client = postgres_client
        self.weaviate_client = weaviate_client
        self.neo4j_client = neo4j_client
        self.neo4j_graphrag_client = neo4j_graphrag_client
        self.use_graphrag = use_graphrag and neo4j_graphrag_client is not None
        
        # Initialize tools
        self.vector_search_tool = VectorSearchTool(weaviate_client)
        self.graph_retrieval_tool = GraphRetrievalTool(neo4j_client)
        
        # Build the graph
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """
        Build the query graph with conditional routing.
        
        Returns:
            The compiled query graph
        """
        # Create a new graph
        graph = StateGraph(QueryState)
        
        # Add nodes to the graph
        graph.add_node("process_query", self._process_query)
        graph.add_node("vector_search", self._vector_search)
        graph.add_node("graph_search", self._graph_search)
        graph.add_node("combine_results", self._combine_results)
        graph.add_node("generate_answer", self._generate_answer)
        
        # Add edges to the graph
        graph.add_edge("process_query", "vector_search")
        graph.add_edge("vector_search", "graph_search")
        graph.add_edge("graph_search", "combine_results")
        graph.add_edge("combine_results", "generate_answer")
        graph.add_edge("generate_answer", END)
        
        # Set the entry point
        graph.set_entry_point("process_query")
        
        return graph.compile()

    def _process_query(self, state: QueryState) -> QueryState:
        """
        Process the query and prepare for retrieval.
        
        Args:
            state: The current state
            
        Returns:
            The updated state
        """
        try:
            query = state["query"]
            logger.info(f"Processing query: {query}")
            
            # Initialize the state with default values
            return {
                **state,
                "vector_results": None,
                "graph_results": None,
                "combined_results": None,
                "answer": None,
                "citations": None,
                "error": None
            }
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            return {**state, "error": f"Query processing error: {str(e)}"}

    async def _vector_search(self, state: QueryState) -> QueryState:
        """
        Perform vector search using the Weaviate client.
        
        Args:
            state: The current state
            
        Returns:
            The updated state with vector search results
        """
        if state.get("error"):
            return state
        
        try:
            query = state["query"]
            top_k = state.get("top_k", 5)
            tenant_id = state.get("tenant_id", "default_tenant")
            
            # Skip if Weaviate client is not available
            if self.weaviate_client is None:
                logger.warning("Weaviate client not available - skipping vector search")
                return {**state, "vector_results": []}
            
            # Perform vector search
            results = self.weaviate_client.query_documents(
                query=query,
                filters={"tenant_id": tenant_id} if tenant_id else None,
                limit=top_k,
                class_name="Global_Tools"
            )
            
            logger.info(f"Vector search returned {len(results)} results")
            
            return {**state, "vector_results": results}
        except Exception as e:
            logger.error(f"Error in vector search: {str(e)}")
            return {**state, "error": f"Vector search error: {str(e)}"}

    async def _graph_search(self, state: QueryState) -> QueryState:
        """
        Perform graph search using the Neo4j client.
        
        Args:
            state: The current state
            
        Returns:
            The updated state with graph search results
        """
        if state.get("error"):
            return state
        
        try:
            query = state["query"]
            tenant_id = state.get("tenant_id", "default_tenant")
            
            # Skip if Neo4j client is not available
            if self.neo4j_client is None and self.neo4j_graphrag_client is None:
                logger.warning("Neo4j clients not available - skipping graph search")
                return {**state, "graph_results": []}
            
            # Prefer GraphRAG client if available
            if self.use_graphrag and self.neo4j_graphrag_client is not None:
                # Use GraphRAG for graph search
                # This is a placeholder - implement actual GraphRAG search
                results = []
                logger.info("Using GraphRAG for graph search")
            else:
                # Use legacy Neo4j client
                results = await self.graph_retrieval_tool.traverse_relations(
                    query=query,
                    tenant_id=tenant_id
                )
            
            logger.info(f"Graph search returned {len(results)} results")
            
            return {**state, "graph_results": results}
        except Exception as e:
            logger.error(f"Error in graph search: {str(e)}")
            return {**state, "error": f"Graph search error: {str(e)}"}

    def _combine_results(self, state: QueryState) -> QueryState:
        """
        Combine results from vector and graph search.
        
        Args:
            state: The current state
            
        Returns:
            The updated state with combined results
        """
        if state.get("error"):
            return state
        
        try:
            vector_results = state.get("vector_results", [])
            graph_results = state.get("graph_results", [])
            
            # Combine results with deduplication
            combined_results = []
            seen_ids = set()
            
            # Add vector results first
            for result in vector_results:
                result_id = result.get("id")
                if result_id and result_id not in seen_ids:
                    seen_ids.add(result_id)
                    enriched_result = result.copy()
                    tenant_id = state.get("tenant_id", "default_tenant")
                    if "tool_id" in result:
                        tool_id = result["tool_id"]
                        tools = self.postgres_client.get_tools_by_ids([tool_id], tenant_id)
                        if tools:
                            tool = tools[0]
                            enriched_content = f"Tool: {tool['name']}\nDescription: {tool['description']}\nUse Case: {tool['use_case']}\nReviews: {tool['reviews']}\nURL: {tool['url']}\nPricing: {tool['pricing']}"
                            enriched_result["content"] = enriched_content
                            enriched_result["metadata"] = tool
                    combined_results.append(enriched_result)
            
            # Add graph results
            for result in graph_results:
                result_id = result.get("id")
                if result_id and result_id not in seen_ids:
                    seen_ids.add(result_id)
                    enriched_result = result.copy()
                    # Similar enrichment if graph results have tool_id
                    if "tool_id" in result:
                        # Repeat the enrichment logic above
                        pass  # Add if needed
                    combined_results.append(enriched_result)
            
            logger.info(f"Combined {len(combined_results)} results")
            
            return {**state, "combined_results": combined_results}
        except Exception as e:
            logger.error(f"Error combining results: {str(e)}")
            return {**state, "error": f"Result combination error: {str(e)}"}

    def _generate_answer(self, state: QueryState) -> QueryState:
        """
        Generate an answer based on the combined results using OpenAI.
        
        Args:
            state: The current state
            
        Returns:
            The updated state with the answer
        """
        if state.get("error"):
            return state
        
        try:
            query = state["query"]
            combined_results = state.get("combined_results", [])
            
            # Generate citations
            citations = []
            context_text = ""
            
            for i, result in enumerate(combined_results):
                citation_id = result.get("id", f"result-{i}")
                source = result.get("source", "unknown")
                content = result.get("content", "")
                
                # Add to context text
                context_text += f"\nDocument {i+1} (Source: {source}):\n{content}\n"
                
                citations.append({
                    "id": citation_id,
                    "source": source,
                    "content": content,
                    "metadata": result.get("metadata", {})
                })
            
            # If we have no results, return a simple answer
            if not combined_results:
                logger.info("No results found, returning simple answer")
                return {
                    **state,
                    "answer": "I don't have enough information to answer that question.",
                    "citations": [],
                    "reasoning": "No relevant documents were found in the knowledge base.",
                    "synthesis": "No information available."
                }
            
            # Initialize OpenAI client
            client = OpenAI(api_key=settings.OPENAI_API_KEY)
            
            # Create a prompt for the LLM
            prompt = f"""
            You are an AI assistant tasked with answering questions based on the provided documents.
            
            Question: {query}
            
            Context Documents:
            {context_text}
            
            Please provide your response in the following structured format:
            
            ANSWER: A direct answer to the question based only on the provided documents
            
            REASONING: Your detailed reasoning process, explaining how you arrived at the answer
            
            SYNTHESIS: A synthesis of the key information from the documents relevant to the question
            
            If the documents don't contain enough information to answer the question, say so in the ANSWER section, but still provide REASONING explaining why you couldn't answer and SYNTHESIS of any relevant information you did find.
            """
            
            # Call OpenAI API
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that answers questions based on provided documents."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2
            )
            
            # Extract the response
            answer_text = response.choices[0].message.content
            
            # Parse the response to extract answer, reasoning, and synthesis
            # Look for the structured format we requested
            answer = "No answer generated."
            reasoning = "No reasoning provided."
            synthesis = "No synthesis provided."
            
            # Split by section headers
            if "ANSWER:" in answer_text:
                sections = answer_text.split("ANSWER:")[1].split("REASONING:")
                if len(sections) > 0:
                    answer = sections[0].strip()
                
                if len(sections) > 1:
                    remaining = sections[1].split("SYNTHESIS:")
                    if len(remaining) > 0:
                        reasoning = remaining[0].strip()
                    
                    if len(remaining) > 1:
                        synthesis = remaining[1].strip()
            else:
                # Fallback to paragraph-based parsing if structured format not found
                parts = answer_text.split("\n\n")
                
                # Try to identify sections by keywords
                for part in parts:
                    lower_part = part.lower()
                    if lower_part.startswith("answer:") or lower_part.startswith("direct answer:"):
                        answer = part
                    elif lower_part.startswith("reasoning:") or "reasoning" in lower_part[:20]:
                        reasoning = part
                    elif lower_part.startswith("synthesis:") or "synthesis" in lower_part[:20]:
                        synthesis = part
                
                # If we still couldn't identify specific sections, use simple paragraph approach
                if answer == "No answer generated." and len(parts) > 0:
                    answer = parts[0]
                if reasoning == "No reasoning provided." and len(parts) > 1:
                    reasoning = parts[1]
                if synthesis == "No synthesis provided." and len(parts) > 2:
                    synthesis = parts[2]
            
            logger.info("Generated answer using OpenAI")
            
            return {
                **state,
                "answer": answer,
                "citations": citations,
                "reasoning": reasoning,
                "synthesis": synthesis
            }
        except Exception as e:
            logger.error(f"Error generating answer: {str(e)}")
            return {**state, "error": f"Answer generation error: {str(e)}"}

    async def query_async(self, query: str, filters: Optional[Dict[str, Any]] = None, tenant_id: str = "default_tenant", top_k: int = 5) -> Dict[str, Any]:
        """
        Query the system asynchronously.
        
        Args:
            query: The query string
            filters: Optional filters to apply
            tenant_id: The tenant ID for multi-tenancy
            top_k: Maximum number of results to return
            
        Returns:
            The query result
        """
        try:
            # Initialize the state
            state = {
                "query": query,
                "filters": filters,
                "top_k": top_k,
                "tenant_id": tenant_id,
                "vector_results": None,
                "graph_results": None,
                "combined_results": None,
                "answer": None,
                "citations": None,
                "error": None
            }
            
            # Run the graph
            result = await self.graph.ainvoke(state)
            
            if result.get("error"):
                logger.error(f"Error in query graph: {result['error']}")
                raise Exception(result["error"])
            
            return {
                "query": query,
                "answer": result.get("answer", ""),
                "citations": result.get("citations", []),
                "reasoning": result.get("reasoning", ""),
                "synthesis": result.get("synthesis", "")
            }
        except Exception as e:
            logger.error(f"Error querying system: {str(e)}")
            raise

    def query(self, query: str, filters: Optional[Dict[str, Any]] = None, tenant_id: str = "default_tenant", top_k: int = 5) -> Dict[str, Any]:
        """
        Query the system synchronously.
        
        Args:
            query: The query string
            filters: Optional filters to apply
            tenant_id: The tenant ID for multi-tenancy
            top_k: Maximum number of results to return
            
        Returns:
            The query result
        """
        try:
            import asyncio
            
            try:
                loop = asyncio.get_running_loop()
                import nest_asyncio
                
                nest_asyncio.apply()
                
                return loop.run_until_complete(self.query_async(query, filters, tenant_id, top_k))
            except RuntimeError:
                return asyncio.run(self.query_async(query, filters, tenant_id, top_k))
        except Exception as e:
            logger.error(f"Error querying system: {str(e)}")
            # Return a structured error response instead of raising
            return {
                "error": str(e),
                "query": query,
                "answer": f"Error processing query: {str(e)}",
                "citations": [],
                "reasoning": "Error occurred during processing.",
                "synthesis": "Error occurred during processing."
            }