"""
Vector Search Tools node for SynthDrive's LangGraph flow.

This module contains the implementation of the Vector Search Tools node that
performs semantic vector search on global AI tools.
"""
from typing import Dict, List, Any, Optional, TypedDict
import logging

from src.data_stores.weaviate_client import WeaviateClient
from src.querying.tools.vector_search import VectorSearchTool

# Configure logging
logger = logging.getLogger(__name__)


class VectorSearchToolsState(TypedDict):
    """
    State object for the Vector Search Tools node.
    
    This state object tracks the progress of the search process and stores
    the retrieved documents.
    """
    original_query: str
    organization_id: str
    plan: Optional[str]
    retrieved_docs: List[Dict[str, Any]]
    graph_insights: List[Dict[str, Any]]
    final_answer: Optional[str]
    error_log: List[str]


class VectorSearchToolsNode:
    """
    Vector Search Tools node for SynthDrive's LangGraph flow.
    
    This node performs semantic vector search on global AI tools to discover
    relevant items based on the query.
    """
    
    def __init__(self, weaviate_client: WeaviateClient):
        """
        Initialize the Vector Search Tools node.
        
        Args:
            weaviate_client: The Weaviate client for vector search
        """
        self.weaviate_client = weaviate_client
        self.vector_search_tool = VectorSearchTool(weaviate_client=weaviate_client)
    
    async def search_ai_tools(self, state: VectorSearchToolsState) -> VectorSearchToolsState:
        """
        Search for AI tools using the query from the state.
        
        Args:
            state: The current state object containing the query and other information
            
        Returns:
            The updated state with retrieved AI tools
        """
        query = state["original_query"]
        organization_id = state.get("organization_id", "default")
        
        logger.info(f"Searching for AI tools with query: {query}")
        
        try:
            # Search for AI tools using the vector search tool
            tools_results = await self.vector_search_tool.search_ai_tools(
                query=query,
                filters={"tenant_id": "default"},  # Using default tenant for global tools
                limit=5  # Default limit
            )
            
            # Format the results for the state
            formatted_results = []
            for i, tool in enumerate(tools_results):
                formatted_results.append({
                    "name": tool.get("name", "Unknown Tool"),
                    "description": tool.get("description", ""),
                    "use_case": tool.get("use_case", ""),
                    "url": tool.get("url", ""),
                    "category": tool.get("category", ""),
                    "pricing": tool.get("pricing", ""),
                    "rating": tool.get("rating", 0.0),
                    "relevance_score": tool.get("relevance_score", 0.0),
                    "citation_id": f"tool-{i+1}",
                    "source": "Global_Tools"
                })
            
            logger.info(f"Found {len(formatted_results)} AI tools")
            
            # Get the current retrieved_docs from the state
            retrieved_docs = state.get("retrieved_docs", [])
            
            # Append the new results to the retrieved_docs
            retrieved_docs.extend(formatted_results)
            
            # Update the state with the new retrieved_docs
            return {
                **state,
                "retrieved_docs": retrieved_docs
            }
        
        except Exception as e:
            error_message = f"Error searching for AI tools: {str(e)}"
            logger.error(error_message)
            
            # Update error log in the state
            error_log = state.get("error_log", [])
            error_log.append(error_message)
            
            return {
                **state,
                "error_log": error_log
            }