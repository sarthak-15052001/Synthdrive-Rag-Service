"""
Test script for the /api/v1/rag/vector-search-tenant-docs API endpoint with specific payloads.

This script:
1. Adds sample tenant documents to the database
2. Tests the API endpoint with specific payloads
3. Displays the results
"""
import asyncio
import logging
import json
import requests
import os
import sys
import traceback
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

# Sample tenant document data for testing
sample_tenant_docs = [
    {
        "file_id": "file-001",
        "file_name": "Financial Report 2023.pdf",
        "file_path": "/reports/financial/2023.pdf",
        "content_chunk": "The financial performance for 2023 showed a 15% increase in revenue compared to the previous year. Key growth areas included cloud services and AI solutions.",
        "organization_id": "test_org_123",
        "upload_date": "2023-12-15T00:00:00Z",
        "file_type": "pdf",
        "tags": ["financial", "2023"],
        "tenant_id": "default"
    },
    {
        "file_id": "file-002",
        "file_name": "Marketing Strategy 2023.docx",
        "file_path": "/marketing/strategy/2023.docx",
        "content_chunk": "Our marketing strategy for 2023 focuses on digital channels, with increased investment in social media and content marketing. Target demographics include tech professionals aged 25-45.",
        "organization_id": "test_org_123",
        "upload_date": "2023-01-10T00:00:00Z",
        "file_type": "docx",
        "tags": ["marketing", "strategy"],
        "tenant_id": "default"
    },
    {
        "file_id": "file-003",
        "file_name": "Product Roadmap 2023-2024.pptx",
        "file_path": "/product/roadmap/2023-2024.pptx",
        "content_chunk": "The product roadmap for 2023-2024 includes the launch of our AI-powered analytics platform in Q2 2023, followed by the mobile app integration in Q4 2023.",
        "organization_id": "test_org_123",
        "upload_date": "2023-02-28T00:00:00Z",
        "file_type": "pptx",
        "tags": ["product", "roadmap"],
        "tenant_id": "default"
    },
    {
        "file_id": "file-004",
        "file_name": "Annual Report 2023.pdf",
        "file_path": "/reports/annual/2023.pdf",
        "content_chunk": "Annual report for 2023 fiscal year. This document contains financial statements, business performance analysis, and future outlook for all business units.",
        "organization_id": "test_org_123",
        "upload_date": "2023-12-31T00:00:00Z",
        "file_type": "pdf",
        "tags": ["2023", "annual", "report"],
        "tenant_id": "default"
    },
    {
        "file_id": "file-005",
        "file_name": "Business Strategy 2023.pptx",
        "file_path": "/strategy/business/2023.pptx",
        "content_chunk": "Business strategy and performance insights for 2023. This presentation outlines our core business objectives, market analysis, and strategic initiatives for the coming year.",
        "organization_id": "test_org_123",
        "upload_date": "2023-01-05T00:00:00Z",
        "file_type": "pptx",
        "tags": ["business", "strategy", "performance"],
        "tenant_id": "default"
    }
]

# Test payloads
test_payloads = [
    # Payload 1: Search for financial documents
    {
        "query": "financial performance report for 2023",
        "organization_id": "test_org_123",
        "tenant_id": "default",
        "filters": {
            "file_type": "pdf",
            "tags": ["financial", "2023"]
        },
        "limit": 5
    },
    # Payload 2: Search for marketing strategy documents
    {
        "query": "marketing strategy and target demographics",
        "organization_id": "test_org_123",
        "tenant_id": "default",
        "filters": {
            "file_type": "docx",
            "tags": ["marketing", "strategy"]
        },
        "limit": 5
    },
    # Payload 3: Search for product roadmap
    {
        "query": "product roadmap and AI-powered analytics platform",
        "organization_id": "test_org_123",
        "tenant_id": "default",
        "filters": {
            "file_type": "pptx",
            "tags": ["product", "roadmap"]
        },
        "limit": 5
    },
    # Payload 4: Search using general 2023 documents
    {
        "query": "all reports and documents for 2023",
        "organization_id": "test_org_123",
        "tenant_id": "default",
        "filters": {
            "tags": ["2023"]
        },
        "limit": 5
    },
    # Payload 5: Search across all document types
    {
        "query": "business strategy and performance insights",
        "organization_id": "test_org_123",
        "tenant_id": "default",
        "filters": {},
        "limit": 5
    }
]

async def add_sample_tenant_docs():
    """Add sample tenant documents to the database."""
    try:
        # Initialize Weaviate client
        weaviate_url = os.getenv("WEAVIATE_URL", "http://localhost:8080")
        weaviate_api_key = os.getenv("WEAVIATE_API_KEY", "")
        
        logger.info(f"Connecting to Weaviate at {weaviate_url}")
        weaviate_client = WeaviateClient(weaviate_url=weaviate_url, api_key=weaviate_api_key)
        
        # Add sample tenant documents to Weaviate
        logger.info("Adding sample tenant documents to Weaviate")
        for doc in sample_tenant_docs:
            try:
                # Add to Weaviate using the client's method specifically for tenant files
                file_id = weaviate_client.add_tenant_uploaded_file(
                    file_data=doc,
                    organization_id=doc["organization_id"],
                    tenant_id=doc["tenant_id"]
                )
                logger.info(f"Added document: {doc['file_name']} with ID: {file_id}")
            except Exception as e:
                logger.error(f"Error adding document {doc['file_name']}: {str(e)}")
                logger.error(traceback.format_exc())
        
        # Verify documents were added by directly querying Weaviate
        logger.info("Verifying documents were added by directly querying Weaviate")
        results = weaviate_client.search_tenant_uploaded_files(
            query="",  # Empty query to get all documents
            organization_id="test_org_123",
            filters={"tenant_id": "default"},
            limit=10
        )
        
        logger.info(f"Found {len(results)} documents in Weaviate")
        for i, doc in enumerate(results):
            logger.info(f"Document {i+1}: {doc.get('file_name', 'Unknown')}")
        
        logger.info("Sample tenant documents added successfully")
        return True
    
    except Exception as e:
        logger.error(f"Error adding sample tenant documents: {str(e)}")
        logger.error(traceback.format_exc())
        return False

def test_vector_search_tenant_docs_api():
    """Test the Vector Search Tenant Documents API endpoint with specific payloads."""
    
    try:
        # API endpoint URL
        api_url = "http://localhost:8001/api/v1/rag/vector-search-tenant-docs"
        
        # Headers for the request
        headers = {
            "Content-Type": "application/json"
        }
        
        # Try to get API key if available
        api_key = os.getenv("API_KEY", "")
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        
        # Check if the API server is running
        try:
            requests.get("http://localhost:8001/docs", timeout=2)
        except requests.exceptions.ConnectionError:
            logger.warning("API server is not running. Skipping API test.")
            return False
        
        # Run test payloads
        logger.info("Testing Vector Search Tenant Documents API with specific payloads")
        for i, payload in enumerate(test_payloads):
            logger.info(f"\nPayload {i+1}: {payload['query']}")
            logger.info(f"Filters: {payload['filters']}")
            
            # Make the API request
            response = requests.post(api_url, headers=headers, json=payload)
            
            # Check if the request was successful
            if response.status_code == 200:
                # Parse the response
                result = response.json()
                
                # Display results
                logger.info(f"Response: {json.dumps(result, indent=2)}")
                logger.info(f"Found {len(result.get('files', []))} results:")
                for j, file in enumerate(result.get("files", [])):
                    logger.info(f"Result {j+1}:")
                    logger.info(f"  File ID: {file.get('file_id')}")
                    logger.info(f"  File Name: {file.get('file_name')}")
                    logger.info(f"  Content Chunk: {file.get('content_chunk')[:50]}...")  # First 50 chars
                    logger.info(f"  File Type: {file.get('file_type')}")
                    logger.info(f"  Tags: {file.get('tags')}")
                    logger.info(f"  Relevance Score: {file.get('relevance_score')}")
                    logger.info("---")
            else:
                logger.error(f"API request failed with status code {response.status_code}")
                logger.error(f"Response: {response.text}")
        
        logger.info("API test completed")
        return True
    
    except Exception as e:
        logger.error(f"Error in API test: {str(e)}")
        logger.error(traceback.format_exc())
        return False

async def main():
    """Main function to run the test."""
    # Add sample tenant documents
    success = await add_sample_tenant_docs()
    if not success:
        logger.error("Failed to add sample tenant documents. Aborting test.")
        return
    
    # Test the API endpoint
    test_vector_search_tenant_docs_api()

if __name__ == "__main__":
    # Run the test
    asyncio.run(main())