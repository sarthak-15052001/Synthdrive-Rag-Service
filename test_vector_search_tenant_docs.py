"""
Test for the Vector Search Tenant Documents functionality.

This script tests the vector search for tenant documents functionality,
which allows semantically searching tenant-specific uploaded files,
filtered by organization_id, to retrieve relevant documents.
"""
import asyncio
import os
import sys
import logging
from dotenv import load_dotenv

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


async def test_vector_search_tenant_docs():
    """
    Test the Vector Search Tenant Documents functionality.
    
    This function initializes the Weaviate client and the Vector Search Tenant Docs node,
    then performs a search for tenant documents using a test query.
    """
    try:
        # Initialize Weaviate client
        weaviate_url = os.getenv("WEAVIATE_URL", "http://localhost:8080")
        weaviate_api_key = os.getenv("WEAVIATE_API_KEY", "")
        
        logger.info(f"Connecting to Weaviate at {weaviate_url}")
        weaviate_client = WeaviateClient(weaviate_url=weaviate_url, api_key=weaviate_api_key)
        
        # Initialize Vector Search Tenant Docs node
        vector_search_tenant_docs_node = VectorSearchTenantDocsNode(weaviate_client=weaviate_client)
        
        # Test query and organization ID
        test_query = "financial reports from 2023"
        test_organization_id = "test_org_123"  # Replace with a valid organization ID
        
        # Create initial state
        initial_state = {
            "original_query": test_query,
            "organization_id": test_organization_id,
            "plan": None,
            "retrieved_docs": [],
            "graph_insights": [],
            "final_answer": None,
            "error_log": []
        }
        
        # Perform search
        logger.info(f"Searching for tenant documents with query: {test_query} for organization: {test_organization_id}")
        result_state = await vector_search_tenant_docs_node.search_tenant_documents(initial_state)
        
        # Check for errors
        if result_state.get("error_log") and len(result_state["error_log"]) > 0:
            logger.error(f"Error in Vector Search Tenant Docs: {result_state['error_log'][-1]}")
            return
        
        # Print results
        retrieved_docs = result_state.get("retrieved_docs", [])
        logger.info(f"Found {len(retrieved_docs)} tenant documents")
        
        for i, doc in enumerate(retrieved_docs):
            logger.info(f"Document {i+1}:")
            logger.info(f"  File ID: {doc.get('file_id', '')}")
            logger.info(f"  File Name: {doc.get('file_name', '')}")
            logger.info(f"  Content: {doc.get('content', '')[:100]}...")  # Print first 100 chars of content
            logger.info(f"  Relevance Score: {doc.get('relevance_score', 0.0)}")
            logger.info("")
        
        logger.info("Vector Search Tenant Docs test completed successfully")
        
    except Exception as e:
        logger.error(f"Error testing Vector Search Tenant Docs: {str(e)}")


if __name__ == "__main__":
    # Run the test
    asyncio.run(test_vector_search_tenant_docs())