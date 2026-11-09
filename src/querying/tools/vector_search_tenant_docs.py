"""
Vector Search Tenant Documents node for SynthDrive's LangGraph flow.

This module contains the implementation of the Vector Search Tenant Documents node that
performs semantic vector search on tenant-specific uploaded files, filtered by organization_id.
"""
from typing import Dict, List, Any, Optional, TypedDict
import logging

from src.data_stores.weaviate_client import WeaviateClient
from src.querying.tools.vector_search import VectorSearchTool

# Configure logging
logger = logging.getLogger(__name__)


class VectorSearchTenantDocsState(TypedDict):
    """
    State object for the Vector Search Tenant Documents node.
    
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


class VectorSearchTenantDocsNode:
    """
    Vector Search Tenant Documents node for SynthDrive's LangGraph flow.
    
    This node performs semantic vector search on tenant-specific uploaded files,
    filtered by organization_id, to retrieve relevant documents based on the query.
    """
    
    def __init__(self, weaviate_client: WeaviateClient):
        """
        Initialize the Vector Search Tenant Documents node.
        
        Args:
            weaviate_client: The Weaviate client for vector search
        """
        self.weaviate_client = weaviate_client
        self.vector_search_tool = VectorSearchTool(weaviate_client=weaviate_client)
    
    async def search_tenant_documents(self, state: VectorSearchTenantDocsState) -> VectorSearchTenantDocsState:
        """
        Search for tenant-specific uploaded files using the query from the state.
        
        Args:
            state: The current state object containing the query and other information
            
        Returns:
            The updated state with retrieved tenant documents
        """
        query = state["original_query"]
        organization_id = state.get("organization_id", "default")
        
        logger.info(f"Searching for tenant documents with query: {query} for organization: {organization_id}")
        
        try:
            # Search for tenant uploaded files using the Weaviate client
            tenant_files_results = self.weaviate_client.search_tenant_uploaded_files(
                query=query,
                organization_id=organization_id,
                filters={"tenant_id": "default"},  # Using default tenant or can be customized
                limit=5  # Default limit
            )
            
            # Format the results for the state
            formatted_results = []
            for i, file in enumerate(tenant_files_results):
                formatted_results.append({
                    "file_id": file.get("file_id", f"file-{i+1}"),
                    "file_name": file.get("file_name", "Unknown File"),
                    "file_path": file.get("file_path", ""),
                    "content": file.get("content_chunk", ""),  # Map content_chunk to content for consistency
                    "organization_id": file.get("organization_id", ""),
                    "upload_date": file.get("upload_date", ""),
                    "file_type": file.get("file_type", ""),
                    "tags": file.get("tags", []),
                    "relevance_score": file.get("relevance_score", 0.0),
                    "citation_id": f"tenant-doc-{i+1}",
                    "source": "Tenant_UploadedFiles"
                })
            
            logger.info(f"Found {len(formatted_results)} tenant documents")
            
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
            error_message = f"Error searching for tenant documents: {str(e)}"
            logger.error(error_message)
            
            # Update error log in the state
            error_log = state.get("error_log", [])
            error_log.append(error_message)
            
            return {
                **state,
                "error_log": error_log
            }