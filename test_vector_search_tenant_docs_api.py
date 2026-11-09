"""
Test for the Vector Search Tenant Documents API endpoint.

This script tests the API endpoint for vector searching tenant documents,
which allows semantically searching tenant-specific uploaded files,
filtered by organization_id, to retrieve relevant documents.
"""
import asyncio
import logging
import json
import requests
import os
from dotenv import load_dotenv
from typing import Dict, List, Any

from src.core.config import settings

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Sample tenant document data for testing (optional, only needed if you want to add test data)
sample_tenant_docs = [
    {
        "file_id": "file-001",
        "file_name": "Financial Report 2023.pdf",
        "file_path": "/reports/financial/2023.pdf",
        "content_chunk": "The financial performance for 2023 showed a 15% increase in revenue compared to the previous year. Key growth areas included cloud services and AI solutions.",
        "organization_id": "test_org_123",
        "upload_date": "2023-12-15T00:00:00Z",
        "file_type": "pdf",
        "tags": ["financial", "annual report", "2023"],
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
        "tags": ["marketing", "strategy", "2023"],
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
        "tags": ["product", "roadmap", "2023", "2024"],
        "tenant_id": "default"
    }
]

def test_vector_search_tenant_docs_api():
    """Test the Vector Search Tenant Documents API endpoint."""
    
    try:
        # API endpoint URL
        api_url = "http://localhost:8001/api/v1/rag/vector-search-tenant-docs"
        
        # Test queries
        test_queries = [
            "financial reports from 2023",
            "marketing strategy",
            "product roadmap",
            "annual report"
        ]
        
        # Headers for the request
        headers = {
            "Content-Type": "application/json"
        }
        
        # Try to get API key if available
        try:
            if hasattr(settings, 'API_KEY') and settings.API_KEY:
                headers["Authorization"] = f"Bearer {settings.API_KEY}"
        except Exception:
            logger.warning("API_KEY not found in settings, proceeding without authentication")
        
        # Check if the API server is running
        try:
            # Make a simple request to check if the server is running
            requests.get("http://localhost:8001/docs", timeout=2)
        except requests.exceptions.ConnectionError:
            logger.warning("API server is not running. Skipping API test.")
            return False
        
        # Run test queries
        logger.info("Testing Vector Search Tenant Documents API with sample queries")
        for query in test_queries:
            logger.info(f"\nQuery: {query}")
            
            # Request payload
            payload = {
                "query": query,
                "organization_id": "test_org_123",  # Use a test organization ID
                "tenant_id": "default",
                "filters": {},
                "limit": 5
            }
            
            # Make the API request
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
                    logger.info(f"  File Path: {file.get('file_path')}")
                    logger.info(f"  Content Chunk: {file.get('content_chunk')[:100]}...")  # First 100 chars
                    logger.info(f"  Organization ID: {file.get('organization_id')}")
                    logger.info(f"  Upload Date: {file.get('upload_date')}")
                    logger.info(f"  File Type: {file.get('file_type')}")
                    logger.info(f"  Tags: {file.get('tags')}")
                    logger.info(f"  Relevance Score: {file.get('relevance_score')}")
                    logger.info(f"  Citation ID: {file.get('citation_id')}")
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