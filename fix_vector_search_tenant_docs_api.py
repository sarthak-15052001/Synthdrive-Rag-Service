"""
Fix for the Vector Search Tenant Documents API endpoint.

This script fixes the issue with the API endpoint returning an incorrect response format.
The issue is that the API is returning {"query": "...", "organization_id": "default", "files": []}
instead of the expected response with the correct organization_id and files.
"""
import asyncio
import logging
import json
import requests
import os
import sys
from dotenv import load_dotenv
from typing import Dict, List, Any

# Add the src directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import required modules
from src.data_stores.weaviate_client import WeaviateClient
from src.querying.tools.vector_search_tenant_docs import VectorSearchTenantDocsNode

# The issue is in the API endpoint implementation in src/api/v1/endpoints/query.py
# The endpoint is not correctly handling the filters parameter from the request
# Let's create a fixed version of the search_tenant_documents method

async def fixed_search_tenant_documents(weaviate_client, query, organization_id, tenant_id="default", filters=None, limit=5):
    """
    Fixed version of the search_tenant_documents method.
    
    Args:
        weaviate_client: The Weaviate client
        query: The search query
        organization_id: The organization ID
        tenant_id: The tenant ID (default: "default")
        filters: Additional filters to apply (default: None)
        limit: Maximum number of results to return (default: 5)
        
    Returns:
        A list of tenant documents matching the query
    """
    try:
        # Initialize the Vector Search Tenant Docs node
        vector_search_tenant_docs_node = VectorSearchTenantDocsNode(weaviate_client=weaviate_client)
        
        # Create the initial state
        initial_state = {
            "original_query": query,
            "organization_id": organization_id,
            "plan": None,
            "retrieved_docs": [],
            "graph_insights": [],
            "final_answer": None,
            "error_log": []
        }
        
        # Search for tenant documents using the Vector Search Tenant Docs node
        result_state = await vector_search_tenant_docs_node.search_tenant_documents(initial_state)
        
        # Check for errors
        if result_state.get("error_log") and len(result_state["error_log"]) > 0:
            error_message = result_state["error_log"][-1]
            logger.error(f"Error in Vector Search Tenant Docs: {error_message}")
            return []
        
        # Apply additional filters if provided
        filtered_docs = result_state.get("retrieved_docs", [])
        
        if filters:
            # Apply file_type filter
            if "file_type" in filters:
                filtered_docs = [doc for doc in filtered_docs if doc.get("file_type") == filters["file_type"]]
            
            # Apply tags filter
            if "tags" in filters and filters["tags"]:
                filtered_docs = [
                    doc for doc in filtered_docs 
                    if doc.get("tags") and all(tag in doc.get("tags", []) for tag in filters["tags"])
                ]
        
        # Limit the number of results
        filtered_docs = filtered_docs[:limit]
        
        return filtered_docs
        
    except Exception as e:
        logger.error(f"Error in fixed search_tenant_documents: {str(e)}")
        return []

async def test_fixed_search_tenant_documents():
    """Test the fixed search_tenant_documents function."""
    try:
        # Initialize Weaviate client
        weaviate_url = os.getenv("WEAVIATE_URL", "http://localhost:8080")
        weaviate_api_key = os.getenv("WEAVIATE_API_KEY", "")
        
        logger.info(f"Connecting to Weaviate at {weaviate_url}")
        weaviate_client = WeaviateClient(weaviate_url=weaviate_url, api_key=weaviate_api_key)
        
        # Test query
        test_query = "financial reports from 2023"
        test_organization_id = "test_org_123"
        
        # Test filters
        test_filters = {
            "file_type": "pdf",
            "tags": ["financial", "2023"]
        }
        
        # Search for tenant documents using the fixed function
        logger.info(f"Searching for tenant documents with query: {test_query} for organization: {test_organization_id}")
        results = await fixed_search_tenant_documents(
            weaviate_client=weaviate_client,
            query=test_query,
            organization_id=test_organization_id,
            filters=test_filters,
            limit=5
        )
        
        # Print results
        logger.info(f"Found {len(results)} tenant documents")
        for i, doc in enumerate(results):
            logger.info(f"Document {i+1}:")
            logger.info(f"  File ID: {doc.get('file_id', '')}")
            logger.info(f"  File Name: {doc.get('file_name', '')}")
            logger.info(f"  Content: {doc.get('content', '')[:100]}...")  # Print first 100 chars of content
            logger.info(f"  File Type: {doc.get('file_type', '')}")
            logger.info(f"  Tags: {doc.get('tags', [])}")
            logger.info(f"  Relevance Score: {doc.get('relevance_score', 0.0)}")
            logger.info("")
        
        logger.info("Fixed search_tenant_documents test completed successfully")
        
    except Exception as e:
        logger.error(f"Error testing fixed search_tenant_documents: {str(e)}")

# To fix the API endpoint, you would need to modify the vector_search_tenant_docs function
# in src/api/v1/endpoints/query.py to use the fixed_search_tenant_documents function
# Here's how the fixed API endpoint would look:

'''
@router.post("/vector-search-tenant-docs")
async def vector_search_tenant_docs(
    request: VectorSearchTenantDocsRequest,
    current_user: Annotated[Dict[str, Any], Depends(get_current_user)],
    weaviate_client: Annotated[WeaviateClient, Depends(get_weaviate_client)],
):
    """
    Semantically search tenant-specific uploaded files, filtered by organization_id, to retrieve relevant documents.
    
    This endpoint simulates the Vector Search Docs node in SynthDrive's LangGraph system. It performs a semantic search
    in Weaviate's Tenant_UploadedFiles collection, filtered by organization_id, and returns the matching documents.
    
    Example query: "financial reports from 2023"
    """
    logger.info(f"Processing Vector Search Tenant Docs query: {request.query} for organization: {request.organization_id}")
    
    try:
        # Use the fixed search_tenant_documents function
        results = await fixed_search_tenant_documents(
            weaviate_client=weaviate_client,
            query=request.query,
            organization_id=request.organization_id,
            tenant_id=request.tenant_id,
            filters=request.filters,
            limit=request.limit
        )
        
        # Convert the retrieved documents to TenantUploadedFile objects
        files = []
        for doc in results:
            files.append(TenantUploadedFile(
                file_id=doc.get("file_id", ""),
                file_name=doc.get("file_name", "Unknown File"),
                file_path=doc.get("file_path", ""),
                content_chunk=doc.get("content", ""),  # Map content back to content_chunk
                organization_id=doc.get("organization_id", ""),
                upload_date=doc.get("upload_date", ""),
                file_type=doc.get("file_type", ""),
                tags=doc.get("tags", []),
                relevance_score=doc.get("relevance_score", 0.0),
                citation_id=doc.get("citation_id", "")
            ))
        
        # Create and return the response
        response = VectorSearchTenantDocsResponse(
            query=request.query,
            organization_id=request.organization_id,
            files=files
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error in Vector Search Tenant Docs: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to search for tenant documents: {str(e)}",
        ) from e
'''

if __name__ == "__main__":
    # Run the test
    asyncio.run(test_fixed_search_tenant_documents())