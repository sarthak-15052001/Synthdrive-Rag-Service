"""
Planner module for SynthDrive's LangGraph querying system.

This module contains the implementation of the Planner node that analyzes
user queries and generates retrieval strategies.
"""
from typing import Dict, List, Any, Optional, TypedDict
import logging
import json
from openai import OpenAI

from src.core.config import settings
from src.data_stores.weaviate_client import WeaviateClient
from src.data_stores.neo4j_client import Neo4jClient

# Configure logging
logger = logging.getLogger(__name__)


class PlannerState(TypedDict):
    """
    State object for the Planner node.
    
    This state object tracks the progress of the planning process and stores
    the generated plan for retrieval, including which collections to search.
    """
    original_query: str
    organization_id: str
    plan: Optional[str]
    collections_to_search: List[str]
    retrieved_docs: List[Dict[str, Any]]
    graph_insights: List[Dict[str, Any]]
    final_answer: Optional[str]
    error_log: List[str]


class PlannerNode:
    """
    Planner node for SynthDrive's LangGraph querying system.
    
    This node analyzes user queries and generates retrieval strategies,
    determining the sequence of searches using Weaviate collections or Neo4j.
    It considers the specific data sources available in the system and recommends
    the most appropriate retrieval methods based on the query content.
    """
    
    def __init__(self, weaviate_client: Optional[WeaviateClient] = None, neo4j_client: Optional[Neo4jClient] = None):
        """
        Initialize the Planner node.
        
        Args:
            weaviate_client: Optional Weaviate client for vector searches
            neo4j_client: Optional Neo4j client for graph queries
        """
        # Initialize OpenAI client for planning
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
        
        # Store the clients
        self.weaviate_client = weaviate_client
        self.neo4j_client = neo4j_client
        
        # Define available collections and their capabilities
        self.collections = {
            "Tenant_UploadedFiles": {
                "description": "Organization-specific documents uploaded by users",
                "use_cases": ["company documents", "internal knowledge", "private data"],
                "requires_organization_id": True,
                "search_method": self.search_tenant_files
            },
            "Global_Tools": {
                "description": "Information about AI tools and their capabilities",
                "use_cases": ["tool recommendations", "software comparisons", "AI solutions"],
                "requires_organization_id": False,
                "search_method": self.search_global_tools
            },
            "Global_Ecosystem": {
                "description": "Information about ecosystem partners and their expertise",
                "use_cases": ["partner recommendations", "expertise lookup", "service providers"],
                "requires_organization_id": False,
                "search_method": self.search_ecosystem_partners
            },
            "Global_LearningResources": {
                "description": "Educational content and learning materials",
                "use_cases": ["tutorials", "guides", "learning materials", "documentation"],
                "requires_organization_id": False,
                "search_method": self.search_learning_resources
            }
        }
        
        # Define retrieval methods
        self.retrieval_methods = {
            "vector_search": {
                "description": "Semantic similarity search in Weaviate",
                "best_for": ["finding similar content", "semantic matching", "concept search"]
            },
            "graph_traversal": {
                "description": "Relationship traversal in Neo4j",
                "best_for": ["finding connections", "relationship discovery", "network analysis"]
            },
            "hybrid_search": {
                "description": "Combining vector and keyword search",
                "best_for": ["precise matching", "combining semantic and exact matches"]
            },
            "multi_query": {
                "description": "Using multiple query variations",
                "best_for": ["improving recall", "covering different phrasings", "complex queries"]
            },
            "kernel_of_truth": {
                "description": "Multi-hop graph queries",
                "best_for": ["complex relationships", "indirect connections", "deep insights"]
            }
        }
    
    async def search_tenant_files(self, query: str, organization_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search for tenant uploaded files using the Weaviate client.
        
        Args:
            query: The search query
            organization_id: The organization ID to filter by
            limit: Maximum number of results to return
            
        Returns:
            List of matching documents
        """
        if not self.weaviate_client:
            logger.warning("Weaviate client not available for tenant files search")
            return []
        
        try:
            # Search for tenant uploaded files
            results = self.weaviate_client.search_tenant_files(
                query=query,
                organization_id=organization_id,
                filters={},
                limit=limit
            )
            
            # Format the results
            formatted_results = []
            for i, result in enumerate(results):
                formatted_results.append({
                    "content": result.get("content_chunk", ""),
                    "metadata": {
                        "file_id": result.get("file_id", f"file-{i}"),
                        "file_name": result.get("file_name", "Unknown File"),
                        "organization_id": organization_id
                    },
                    "source": "Tenant_UploadedFiles",
                    "relevance_score": result.get("relevance_score", 0.0),
                    "citation_id": f"tenant-file-{i}"
                })
            
            return formatted_results
        
        except Exception as e:
            logger.error(f"Error searching tenant files: {str(e)}")
            return []
    
    async def search_global_tools(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search for AI tools using the Weaviate client.
        
        Args:
            query: The search query
            limit: Maximum number of results to return
            
        Returns:
            List of matching tools
        """
        if not self.weaviate_client:
            logger.warning("Weaviate client not available for global tools search")
            return []
        
        try:
            # Search for AI tools
            results = self.weaviate_client.search_ai_tools(
                query=query,
                filters={},
                limit=limit
            )
            
            # Format the results
            formatted_results = []
            for i, result in enumerate(results):
                formatted_results.append({
                    "content": f"{result.get('name', 'Unknown Tool')}: {result.get('description', '')}",
                    "metadata": {
                        "tool_id": result.get("tool_id", f"tool-{i}"),
                        "name": result.get("name", "Unknown Tool"),
                        "url": result.get("url", ""),
                        "category": result.get("category", "")
                    },
                    "source": "Global_Tools",
                    "relevance_score": result.get("relevance_score", 0.0),
                    "citation_id": f"global-tool-{i}"
                })
            
            return formatted_results
        
        except Exception as e:
            logger.error(f"Error searching global tools: {str(e)}")
            return []
    
    async def search_ecosystem_partners(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search for ecosystem partners using the Weaviate client.
        
        Args:
            query: The search query
            limit: Maximum number of results to return
            
        Returns:
            List of matching partners
        """
        if not self.weaviate_client:
            logger.warning("Weaviate client not available for ecosystem partners search")
            return []
        
        try:
            # Search for ecosystem partners
            results = self.weaviate_client.search_ecosystem_partners(
                query=query,
                filters={},
                limit=limit
            )
            
            # Format the results
            formatted_results = []
            for i, result in enumerate(results):
                formatted_results.append({
                    "content": f"{result.get('name', 'Unknown Partner')}: {result.get('bio', '')}",
                    "metadata": {
                        "partner_id": result.get("partner_id", f"partner-{i}"),
                        "name": result.get("name", "Unknown Partner"),
                        "expertise": result.get("expertise", []),
                        "website": result.get("website", "")
                    },
                    "source": "Global_Ecosystem",
                    "relevance_score": result.get("relevance_score", 0.0),
                    "citation_id": f"ecosystem-partner-{i}"
                })
            
            return formatted_results
        
        except Exception as e:
            logger.error(f"Error searching ecosystem partners: {str(e)}")
            return []
    
    async def search_learning_resources(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search for learning resources using the Weaviate client.
        
        Args:
            query: The search query
            limit: Maximum number of results to return
            
        Returns:
            List of matching resources
        """
        if not self.weaviate_client:
            logger.warning("Weaviate client not available for learning resources search")
            return []
        
        try:
            # Search for learning resources
            results = self.weaviate_client.search_learning_resources(
                query=query,
                filters={},
                limit=limit
            )
            
            # Format the results
            formatted_results = []
            for i, result in enumerate(results):
                formatted_results.append({
                    "content": f"{result.get('title', 'Unknown Resource')}: {result.get('content', '')}",
                    "metadata": {
                        "resource_id": result.get("resource_id", f"resource-{i}"),
                        "title": result.get("title", "Unknown Resource"),
                        "url": result.get("url", ""),
                        "resource_type": result.get("resource_type", "")
                    },
                    "source": "Global_LearningResources",
                    "relevance_score": result.get("relevance_score", 0.0),
                    "citation_id": f"learning-resource-{i}"
                })
            
            return formatted_results
        
        except Exception as e:
            logger.error(f"Error searching learning resources: {str(e)}")
            return []
    
    async def _ensure_serializable(self, obj):
        """
        Recursively convert objects to serializable types.
        
        Args:
            obj: The object to convert
            
        Returns:
            A serializable version of the object
        """
        if isinstance(obj, dict):
            return {k: await self._ensure_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [await self._ensure_serializable(item) for item in obj]
        elif hasattr(obj, '__dict__'):
            # Convert custom objects to dictionaries
            return await self._ensure_serializable(obj.__dict__)
        elif hasattr(obj, 'to_dict') and callable(getattr(obj, 'to_dict')):
            # Use to_dict method if available
            return await self._ensure_serializable(obj.to_dict())
        else:
            # Try to return the object as is, or convert to string if not serializable
            try:
                json.dumps(obj)
                return obj
            except (TypeError, OverflowError):
                return str(obj)

    async def query_graph_relationships(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Query Neo4j for relationships related to the query.
        
        Args:
            query: The search query
            limit: Maximum number of results to return
            
        Returns:
            List of relationship insights
        """
        if not self.neo4j_client:
            logger.warning("Neo4j client not available for graph relationship queries")
            return []
        
        try:
            # Extract entities from the query
            entities = await self._extract_entities(query)
            
            if not entities:
                logger.warning("No entities extracted from query for graph search")
                return []
            
            # Use tenant_id "default" for global knowledge
            tenant_id = "default"
            
            # Query Neo4j for relationships using different methods
            insights = []
            
            # Try multiple approaches to find relationships
            for entity in entities:
                # 1. First try: Use traverse_relations with a Cypher query
                try:
                    cypher_query = f"""
                    MATCH (n)-[r]-(m)
                    WHERE n.name CONTAINS '{entity}' OR m.name CONTAINS '{entity}'
                    RETURN n, r, m
                    LIMIT {limit}
                    """
                    
                    results = self.neo4j_client.traverse_relations(cypher_query, tenant_id, limit)
                    
                    for i, record in enumerate(results):
                        # Process the results
                        if isinstance(record, dict):
                            # Handle direct node/relationship results and ensure they're serializable
                            source_node = await self._ensure_serializable(record.get("n", {}))
                            relationship = await self._ensure_serializable(record.get("r", {}))
                            target_node = await self._ensure_serializable(record.get("m", {}))
                            
                            # Format the insight
                            insight = {
                                "content": f"{source_node.get('name', 'Unknown')} {relationship.get('type', 'is related to')} {target_node.get('name', 'Unknown')}",
                                "metadata": {
                                    "source_node": source_node,
                                    "relationship_type": relationship.get("type", ""),
                                    "target_node": target_node
                                },
                                "source": "Neo4j",
                                "relevance_score": 0.8,  # Default relevance score
                                "citation_id": f"graph-insight-{i}"
                            }
                            
                            insights.append(insight)
                except Exception as e:
                    logger.warning(f"Error using traverse_relations with Cypher: {str(e)}")
                
                # 2. Second try: Use search_documents to find related documents
                if not insights:
                    try:
                        docs = self.neo4j_client.search_documents(entity, tenant_id, limit)
                        
                        for i, doc in enumerate(docs):
                            # Create an insight from the document
                            doc_serializable = await self._ensure_serializable(doc)
                            insight = {
                                "content": f"Document about {entity}: {doc_serializable.get('content', '')[:100]}...",
                                "metadata": {
                                    "document_id": doc_serializable.get("id", ""),
                                    "source": doc_serializable.get("source", ""),
                                    "score": doc_serializable.get("score", 0.0)
                                },
                                "source": "Neo4j",
                                "relevance_score": doc_serializable.get("score", 0.7),
                                "citation_id": f"graph-doc-{i}"
                            }
                            
                            insights.append(insight)
                    except Exception as e:
                        logger.warning(f"Error using search_documents: {str(e)}")
                
                # 3. Third try: Use get_related_documents if we have a document ID
                if not insights and hasattr(self.neo4j_client, 'get_related_documents'):
                    try:
                        # This is a fallback that would only work if we had a document ID
                        # In a real implementation, you'd need to get a document ID first
                        dummy_doc_id = f"doc-{entity.replace(' ', '-')}"
                        related_docs = self.neo4j_client.get_related_documents(dummy_doc_id, tenant_id, 2, limit)
                        
                        for i, doc in enumerate(related_docs):
                            # Create an insight from the related document
                            doc_serializable = await self._ensure_serializable(doc)
                            insight = {
                                "content": f"Related document: {doc_serializable.get('content', '')[:100]}...",
                                "metadata": {
                                    "document_id": doc_serializable.get("id", ""),
                                    "shared_entities": doc_serializable.get("shared_entities", 0)
                                },
                                "source": "Neo4j",
                                "relevance_score": 0.6,  # Lower score for this fallback method
                                "citation_id": f"graph-related-{i}"
                            }
                            
                            insights.append(insight)
                    except Exception as e:
                        logger.warning(f"Error using get_related_documents: {str(e)}")
            
            # If we still have no insights, create a synthetic one to show the system is working
            if not insights and entities:
                logger.info("No real graph insights found, creating a synthetic one for demonstration")
                insights.append({
                    "content": f"Entity '{entities[0]}' was found in the query, but no relationships were found in the graph database.",
                    "metadata": {
                        "entity": entities[0],
                        "query": query
                    },
                    "source": "Neo4j",
                    "relevance_score": 0.5,  # Lower score for synthetic insight
                    "citation_id": "graph-synthetic-0"
                })
            
            return insights
        
        except Exception as e:
            logger.error(f"Error querying graph relationships: {str(e)}")
            return []
    
    async def _extract_entities(self, query: str) -> List[str]:
        """
        Extract entities from the query using the LLM.
        
        Args:
            query: The search query
            
        Returns:
            List of extracted entities
        """
        try:
            # Use OpenAI to extract entities
            prompt = f"""
            Extract the main entities (people, organizations, concepts, technologies) from this query:
            
            Query: {query}
            
            Return only a list of entities, one per line.
            """
            
            response = self.openai_client.chat.completions.create(
                model=settings.LLM_MODEL,
                messages=[
                    {"role": "system", "content": "You are an expert in entity extraction."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            # Get the response content
            response_content = response.choices[0].message.content.strip()
            
            # Split by newlines and clean up
            entities = [entity.strip() for entity in response_content.split("\n") if entity.strip()]
            
            return entities
        
        except Exception as e:
            logger.error(f"Error extracting entities: {str(e)}")
            return []
    
    async def generate_final_answer(self, query: str, retrieved_docs: List[Dict[str, Any]], graph_insights: List[Dict[str, Any]]) -> str:
        """
        Generate a final answer based on the retrieved documents and graph insights.
        
        Args:
            query: The original query
            retrieved_docs: List of retrieved documents
            graph_insights: List of graph insights
            
        Returns:
            The generated final answer
        """
        try:
            # Prepare the context from retrieved documents
            docs_context = ""
            for i, doc in enumerate(retrieved_docs):
                docs_context += f"[{i+1}] {doc.get('source', 'Unknown')}: {doc.get('content', '')}\n"
            
            # Prepare the context from graph insights
            insights_context = ""
            for i, insight in enumerate(graph_insights):
                insights_context += f"[{i+1}] {insight.get('content', '')}\n"
            
            # Use OpenAI to generate the final answer
            prompt = f"""
            Answer the following query based on the retrieved information:
            
            Query: {query}
            
            Retrieved Documents:
            {docs_context}
            
            Graph Insights:
            {insights_context}
            
            Provide a comprehensive answer that synthesizes the information from both the retrieved documents and graph insights.
            """
            
            response = self.openai_client.chat.completions.create(
                model=settings.LLM_MODEL,
                messages=[
                    {"role": "system", "content": "You are an expert in synthesizing information to answer questions."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            # Get the response content
            final_answer = response.choices[0].message.content.strip()
            
            return final_answer
        
        except Exception as e:
            logger.error(f"Error generating final answer: {str(e)}")
            return f"Error generating answer: {str(e)}"
    
    async def plan_retrieval(self, state: PlannerState) -> PlannerState:
        """
        Analyze the query and create or revise a retrieval strategy.
        
        Args:
            state: The current state object containing the query and other information
            
        Returns:
            The updated state with a retrieval plan
        """
        query = state["original_query"]
        organization_id = state["organization_id"]
        current_plan = state.get("plan")
        
        logger.info(f"Planning retrieval strategy for query: {query}")
        
        try:
            # Use OpenAI to create a retrieval plan
            prompt = f"""
            You are simulating the Planner node in SynthDrive's LangGraph querying system.
            This is a stateful graph where the state object tracks progress:
            {{'original_query': '{query}', 'organization_id': '{organization_id}', 'plan': '{current_plan if current_plan else ""}', 'retrieved_docs': [], 'graph_insights': [], 'final_answer': null, 'error_log': []}}
            
            Analyze the query and create or revise a retrieval strategy (e.g., 'Search tools in Weaviate, then query Neo4j for context'). Update the 'plan' field and output the updated state object.
            
            Available data sources:
            
            WEAVIATE COLLECTIONS:
            1. Tenant_UploadedFiles - Organization-specific documents uploaded by users
            2. Global_Tools - Information about AI tools and their capabilities
            3. Global_Ecosystem - Information about ecosystem partners and their expertise
            4. Global_LearningResources - Educational content and learning materials
            
            NEO4J GRAPH DATABASE:
            - Contains entity relationships extracted from documents
            - Good for finding connections between entities
            - Supports multi-hop traversals to discover indirect relationships
            
            Query: {query}
            
            For queries about AI tools, use the format: "Search Global_Tools in Weaviate for AI tools related to [topic], then use Neo4j to explore related technologies and user reviews."
            
            For queries about ecosystem partners, use the format: "Search Global_Ecosystem collection in Weaviate for partners with [expertise] expertise, then query Neo4j for relationships."
            
            For queries about learning resources, use the format: "Search Global_LearningResources collection in Weaviate for [topic] materials, then search Global_Tools for related tools."
            
            For queries about internal documents, use the format: "Search Tenant_UploadedFiles collection in Weaviate for [topic] documents, then query Neo4j for relationships."
            
            Output the complete updated state object with the 'plan' field updated.
            """
            
            response = self.openai_client.chat.completions.create(
                model=settings.LLM_MODEL,
                messages=[
                    {"role": "system", "content": "You are an expert in query planning for retrieval-augmented generation systems."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            # Get the response content
            response_content = response.choices[0].message.content.strip()
            
            # Try to parse the response as a state object
            try:
                # Replace single quotes with double quotes for JSON parsing
                json_content = response_content.replace("'", "\"")
                
                # Replace "null" with "null" if needed
                json_content = json_content.replace("null", "null")
                
                # Parse the JSON
                parsed_state = json.loads(json_content)
                
                # Validate that it's a state object
                if not isinstance(parsed_state, dict):
                    raise ValueError("Response is not a dictionary")
                
                # Extract the plan
                if "plan" not in parsed_state:
                    raise ValueError("Response does not contain a plan field")
                
                plan = parsed_state["plan"]
                logger.info(f"Generated retrieval plan: {plan}")
                
                # Parse the plan to extract collection references
                collections_mentioned = []
                for collection in self.collections.keys():
                    if collection in plan:
                        collections_mentioned.append(collection)
                
                # Log which collections were mentioned in the plan
                if collections_mentioned:
                    logger.info(f"Plan references collections: {', '.join(collections_mentioned)}")
                else:
                    logger.info("Plan does not explicitly reference any collections")
                
                # Update the state with the new plan and collection references
                updated_state = {
                    **state,
                    "plan": plan,
                    "collections_to_search": collections_mentioned
                }
                
                # Now perform the actual searches based on the collections mentioned
                retrieved_docs = []
                graph_insights = []
                
                # Check if we have the necessary clients
                if not self.weaviate_client and collections_mentioned:
                    logger.warning("Weaviate client not available for searches")
                    error_log = state.get("error_log", [])
                    error_log.append("Weaviate client not available for searches")
                    updated_state["error_log"] = error_log
                    return updated_state
                
                # Perform searches for each collection
                for collection in collections_mentioned:
                    if collection in self.collections:
                        search_method = self.collections[collection].get("search_method")
                        if search_method:
                            if collection == "Tenant_UploadedFiles":
                                # Tenant files require organization_id
                                docs = await search_method(query, organization_id)
                            else:
                                # Other collections don't require organization_id
                                docs = await search_method(query)
                            
                            retrieved_docs.extend(docs)
                
                # Always try to get graph insights if Neo4j client is available
                if self.neo4j_client:
                    logger.info("Querying Neo4j for graph insights regardless of plan")
                    graph_insights = await self.query_graph_relationships(query)
                    logger.info(f"Found {len(graph_insights)} graph insights from Neo4j")
                else:
                    logger.warning("Neo4j client not available for graph queries")
                    error_log = state.get("error_log", [])
                    error_log.append("Neo4j client not available for graph queries")
                    updated_state["error_log"] = error_log
                
                # Generate a final answer if we have retrieved documents or graph insights
                final_answer = None
                if retrieved_docs or graph_insights:
                    final_answer = await self.generate_final_answer(query, retrieved_docs, graph_insights)
                
                # Ensure all objects are serializable
                serializable_docs = await self._ensure_serializable(retrieved_docs)
                serializable_insights = await self._ensure_serializable(graph_insights)
                
                # Update the state with the retrieved documents, graph insights, and final answer
                updated_state["retrieved_docs"] = serializable_docs
                updated_state["graph_insights"] = serializable_insights
                updated_state["final_answer"] = final_answer
                
                # Log the updated state object
                logger.info(f"Updated state object with {len(retrieved_docs)} retrieved documents and {len(graph_insights)} graph insights")
                
                return updated_state
                
            except (json.JSONDecodeError, ValueError) as e:
                # If parsing fails, treat the response as the plan itself
                logger.warning(f"Failed to parse response as state object: {str(e)}")
                logger.warning(f"Using response content as plan: {response_content}")
                
                # Extract plan using regex if it looks like it contains a plan field
                plan = response_content
                if "'plan':" in response_content or "\"plan\":" in response_content:
                    try:
                        import re
                        plan_match = re.search(r"['\"]plan['\"]\s*:\s*['\"]([^'\"]+)['\"]", response_content)
                        if plan_match:
                            plan = plan_match.group(1)
                    except:
                        pass
                
                # Parse the plan to extract collection references
                collections_mentioned = []
                for collection in self.collections.keys():
                    if collection in plan:
                        collections_mentioned.append(collection)
                
                # Log which collections were mentioned in the plan
                if collections_mentioned:
                    logger.info(f"Plan references collections: {', '.join(collections_mentioned)}")
                else:
                    logger.info("Plan does not explicitly reference any collections")
                
                # Update the state with the new plan and collection references
                updated_state = {
                    **state,
                    "plan": plan,
                    "collections_to_search": collections_mentioned
                }
                
                # Now perform the actual searches based on the collections mentioned
                retrieved_docs = []
                graph_insights = []
                
                # Check if we have the necessary clients
                if not self.weaviate_client and collections_mentioned:
                    logger.warning("Weaviate client not available for searches")
                    error_log = state.get("error_log", [])
                    error_log.append("Weaviate client not available for searches")
                    updated_state["error_log"] = error_log
                    return updated_state
                
                # Perform searches for each collection
                for collection in collections_mentioned:
                    if collection in self.collections:
                        search_method = self.collections[collection].get("search_method")
                        if search_method:
                            if collection == "Tenant_UploadedFiles":
                                # Tenant files require organization_id
                                docs = await search_method(query, organization_id)
                            else:
                                # Other collections don't require organization_id
                                docs = await search_method(query)
                            
                            retrieved_docs.extend(docs)
                
                # Always try to get graph insights if Neo4j client is available
                if self.neo4j_client:
                    logger.info("Querying Neo4j for graph insights regardless of plan")
                    graph_insights = await self.query_graph_relationships(query)
                    logger.info(f"Found {len(graph_insights)} graph insights from Neo4j")
                else:
                    logger.warning("Neo4j client not available for graph queries")
                    error_log = state.get("error_log", [])
                    error_log.append("Neo4j client not available for graph queries")
                    updated_state["error_log"] = error_log
                
                # Generate a final answer if we have retrieved documents or graph insights
                final_answer = None
                if retrieved_docs or graph_insights:
                    final_answer = await self.generate_final_answer(query, retrieved_docs, graph_insights)
                
                # Ensure all objects are serializable
                serializable_docs = await self._ensure_serializable(retrieved_docs)
                serializable_insights = await self._ensure_serializable(graph_insights)
                
                # Update the state with the retrieved documents, graph insights, and final answer
                updated_state["retrieved_docs"] = serializable_docs
                updated_state["graph_insights"] = serializable_insights
                updated_state["final_answer"] = final_answer
                
                # Log the updated state object
                logger.info(f"Updated state object with {len(retrieved_docs)} retrieved documents and {len(graph_insights)} graph insights")
                
                return updated_state
        
        except Exception as e:
            error_message = f"Error planning retrieval strategy: {str(e)}"
            logger.error(error_message)
            
            # Update error log in the state
            error_log = state.get("error_log", [])
            error_log.append(error_message)
            
            return {
                **state,
                "error_log": error_log
            }