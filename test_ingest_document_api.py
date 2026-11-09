#!/usr/bin/env python3
"""
Test script for the document ingestion API endpoint.
This script sends a POST request to the /api/v1/rag/ingest/document endpoint
to test document ingestion functionality.
"""

import json
import logging
import requests
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def test_ingest_document():
    """
    Test the document ingestion API endpoint by sending a POST request
    with sample document content and metadata.
    
    Returns:
        str: The job_id if successful, None otherwise
    """
    # API configuration
    api_url = "http://localhost:8000/api/v1/rag/ingest/document"
    api_key = "your_api_key_here"  # Replace with your actual API key
    
    # Prepare the request payload
    payload = {
        "tenant_id": "default",
        "content": "SynthDrive Inc. is working on a new AI project called Project Horizon. "
                  "The project is led by Dr. Sarah Johnson, who joined the company in 2023. "
                  "The team is using OpenAI's GPT-4 and Google's BERT models for natural "
                  "language processing tasks. They are collaborating with Microsoft on cloud "
                  "infrastructure. The project deadline is December 15, 2025, and they plan "
                  "to present at the AI Summit in San Francisco.",
        "metadata": {
            "source": "test_document",
            "author": "Test User",
            "created_at": datetime.now().isoformat(),
            "document_type": "test",
            "tags": ["test", "document", "ingestion"],
            "additional_metadata": {
                "priority": "high",
                "department": "R&D"
            }
        }
    }
    
    # Set request headers
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    try:
        # Send the POST request
        logger.info(f"Sending request to {api_url}...")
        response = requests.post(
            api_url,
            headers=headers,
            json=payload
        )
        
        # Check if the request was successful
        response.raise_for_status()
        
        # Parse the response
        result = response.json()
        logger.info(f"Response: {json.dumps(result, indent=2)}")
        
        # Extract and return the job_id
        job_id = result.get("job_id")
        if job_id:
            logger.info(f"Document ingestion started with job ID: {job_id}")
            return job_id
        else:
            logger.error("No job_id found in the response")
            return None
            
    except requests.RequestException as e:
        logger.error(f"Error sending request: {str(e)}")
        if hasattr(e, "response") and e.response is not None:
            logger.error(f"Response status code: {e.response.status_code}")
            logger.error(f"Response content: {e.response.text}")
        return None

def test_ingest_document_without_metadata():
    """
    Test the document ingestion API endpoint with minimal data (no metadata).
    
    Returns:
        str: The job_id if successful, None otherwise
    """
    # API configuration
    api_url = "http://localhost:8000/api/v1/rag/ingest/document"
    api_key = "your_api_key_here"  # Replace with your actual API key
    
    # Prepare the request payload with minimal data
    payload = {
        "tenant_id": "default",
        "content": "This is a simple test document without metadata."
    }
    
    # Set request headers
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    try:
        # Send the POST request
        logger.info(f"Sending minimal request to {api_url}...")
        response = requests.post(
            api_url,
            headers=headers,
            json=payload
        )
        
        # Check if the request was successful
        response.raise_for_status()
        
        # Parse the response
        result = response.json()
        logger.info(f"Response: {json.dumps(result, indent=2)}")
        
        # Extract and return the job_id
        job_id = result.get("job_id")
        if job_id:
            logger.info(f"Document ingestion started with job ID: {job_id}")
            return job_id
        else:
            logger.error("No job_id found in the response")
            return None
            
    except requests.RequestException as e:
        logger.error(f"Error sending request: {str(e)}")
        if hasattr(e, "response") and e.response is not None:
            logger.error(f"Response status code: {e.response.status_code}")
            logger.error(f"Response content: {e.response.text}")
        return None

if __name__ == "__main__":
    logger.info("Starting document ingestion API tests")
    
    # Test with complete data
    logger.info("Running test with complete data...")
    job_id = test_ingest_document()
    if job_id:
        logger.info(f"Test passed with job ID: {job_id}")
    else:
        logger.error("Test failed")
    
    # Test with minimal data
    logger.info("Running test with minimal data...")
    job_id_minimal = test_ingest_document_without_metadata()
    if job_id_minimal:
        logger.info(f"Minimal test passed with job ID: {job_id_minimal}")
    else:
        logger.error("Minimal test failed")
    
    logger.info("All tests completed")