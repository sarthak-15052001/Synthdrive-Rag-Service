"""
Simple test for the Vector Search Tenant Documents API endpoint.

This script tests the API endpoint for vector searching tenant documents,
focusing on retrieving documents by organization_id without relying on semantic search.
"""
import requests
import logging
import json
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_vector_search_tenant_docs_api():
    """Test the Vector Search Tenant Documents API endpoint."""
    
    try:
        # API endpoint URL
        api_url = "http://localhost:8001/api/v1/rag/vector-search-tenant-docs"
        
        # Headers for the request
        headers = {
            "Content-Type": "application/json"
        }
        
        # API key if available
        api_key = os.getenv("API_KEY", "")
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        
        # Check if the API server is running
        try:
            requests.get("http://localhost:8001/docs", timeout=2)
        except requests.exceptions.ConnectionError:
            logger.warning("API server is not running. Skipping API test.")
            return False
        
        # Test organization ID - this is the key filter that should return results
        test_organization_id = "test_org_123"
        
        # Request payload - using a simple query
        payload = {
            "query": "any",  # Simple query that should match any document
            "organization_id": test_organization_id,
            "tenant_id": "default",
            "filters": {},
            "limit": 10  # Increase limit to get more results
        }
        
        # Make the API request
        logger.info(f"Making request to {api_url} with organization_id: {test_organization_id}")
        response = requests.post(api_url, headers=headers, json=payload)
        
        # Check if the request was successful
        if response.status_code == 200:
            # Parse the response
            result = response.json()
            
            # Display results
            logger.info(f"Found {len(result.get('files', []))} results:")
            for i, file in enumerate(result.get("files", [])):
                logger.info(f"Result {i+1}:")
                logger.info(f"  File ID: {file.get('file_id')}")
                logger.info(f"  File Name: {file.get('file_name')}")
                logger.info(f"  Content Chunk: {file.get('content_chunk')[:100]}...")  # First 100 chars
                logger.info(f"  Organization ID: {file.get('organization_id')}")
                logger.info("---")
        else:
            logger.error(f"API request failed with status code {response.status_code}")
            logger.error(f"Response: {response.text}")
        
        logger.info("API test completed")
        return True
    
    except Exception as e:
        logger.error(f"Error in API test: {str(e)}")
        return False

if __name__ == "__main__":
    # Test the Vector Search Tenant Documents API
    logger.info("Testing Vector Search Tenant Documents API...")
    test_vector_search_tenant_docs_api()