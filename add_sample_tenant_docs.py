"""
Script to add sample tenant documents to the database for testing.

This script adds sample tenant documents to the Weaviate database
that can be used for testing the vector-search-tenant-docs API.
"""
import asyncio
import logging
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
                import traceback
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
        import traceback
        logger.error(traceback.format_exc())
        return False

if __name__ == "__main__":
    # Run the function
    asyncio.run(add_sample_tenant_docs())