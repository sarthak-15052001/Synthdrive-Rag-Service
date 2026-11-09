"""
Direct test for the Vector Search Tenant Documents API endpoint.

This script tests the API endpoint directly without relying on the Weaviate client,
which helps isolate issues with the API endpoint itself.
"""
import json
import logging
import requests
import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# API endpoint URL
API_URL = "http://localhost:8001/api/v1/rag/vector-search-tenant-docs"

# Headers for the request
HEADERS = {
    "Content-Type": "application/json"
}

def test_api_with_payload(payload):
    """Test the API with a payload."""
    logger.info(f"Testing API with payload: {json.dumps(payload, indent=2)}")
    
    try:
        # Make the API request
        response = requests.post(API_URL, headers=HEADERS, json=payload, timeout=10)
        
        # Check if the request was successful
        if response.status_code == 200:
            # Parse the response
            result = response.json()
            
            logger.info(f"Response: {json.dumps(result, indent=2)}")
            
            # Check if the response contains the expected fields
            if "query" in result and "organization_id" in result and "files" in result:
                logger.info("✓ Response contains the expected fields")
                
                # Check if the organization_id is correct
                org_id = payload["organization_id"]
                resp_org_id = result["organization_id"]
                if org_id == resp_org_id:
                    logger.info(f"✓ organization_id is correct: {resp_org_id}")
                else:
                    logger.info(f"✗ organization_id is incorrect: expected {org_id}, got {resp_org_id}")
                
                # Check if files array exists
                files_count = len(result.get("files", []))
                logger.info(f"✓ Found {files_count} files in the response")
            else:
                logger.info("✗ Response does not contain the expected fields")
        else:
            logger.info(f"✗ Request failed with status code {response.status_code}")
            logger.info(f"Response: {response.text}")
    
    except requests.exceptions.ConnectionError:
        logger.info("✗ Connection error: API server is not running")
    except requests.exceptions.Timeout:
        logger.info("✗ Request timed out")
    except Exception as e:
        logger.info(f"✗ Error: {str(e)}")
    
    logger.info("----------------------------------------")

def main():
    """Main function to run the test."""
    logger.info("Testing Vector Search Tenant Documents API endpoint directly...")
    
    # Payload 2: Search for marketing strategy documents
    payload2 = {
        "query": "marketing strategy and target demographics",
        "organization_id": "test_org_123",
        "tenant_id": "default",
        "filters": {
            "file_type": "docx",
            "tags": ["marketing", "strategy"]
        },
        "limit": 5
    }
    
    # Test the API with the payload
    test_api_with_payload(payload2)
    
    logger.info("Testing completed!")

if __name__ == "__main__":
    main()