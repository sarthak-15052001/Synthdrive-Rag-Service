#!/usr/bin/env python3
"""
Test script for the URL ingestion API endpoint.
This script sends a POST request to the /api/v1/rag/ingest/url endpoint
to test URL ingestion functionality.
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

def test_ingest_url():
    """
    Test the URL ingestion API endpoint by sending a POST request
    with a sample URL and metadata.
    
    Returns:
        str: The job_id if successful, None otherwise
    """
    # API configuration
    api_url = "http://localhost:8000/api/v1/rag/ingest/url"
    api_key = "your_api_key_here"  # Replace with your actual API key
    
    # Prepare the request payload
    payload = {
        "tenant_id": "default",
        "url": "https://httpbin.org/html",
        "metadata": {
            "source": "wikipedia",
            "author": "Test User",
            "created_at": datetime.now().isoformat(),
            "document_type": "reference",
            "tags": ["ai", "test", "ingestion"],
            "additional_metadata": {
                "priority": "medium",
                "department": "Research"
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
            logger.info(f"URL ingestion started with job ID: {job_id}")
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

def test_ingest_url_without_metadata():
    """
    Test the URL ingestion API endpoint with minimal data (no metadata).
    
    Returns:
        str: The job_id if successful, None otherwise
    """
    # API configuration
    api_url = "http://localhost:8000/api/v1/rag/ingest/url"
    api_key = "your_api_key_here"  # Replace with your actual API key
    
    # Prepare the request payload with minimal data
    payload = {
        "tenant_id": "default",
        "url": "https://httpbin.org/json"
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
            logger.info(f"URL ingestion started with job ID: {job_id}")
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
    logger.info("Starting URL ingestion API tests")
    
    # Test with complete data
    logger.info("Running test with complete data...")
    job_id = test_ingest_url()
    if job_id:
        logger.info(f"Test passed with job ID: {job_id}")
    else:
        logger.error("Test failed")
    
    # Test with minimal data
    logger.info("Running test with minimal data...")
    job_id_minimal = test_ingest_url_without_metadata()
    if job_id_minimal:
        logger.info(f"Minimal test passed with job ID: {job_id_minimal}")
    else:
        logger.error("Minimal test failed")
    
    logger.info("All tests completed")