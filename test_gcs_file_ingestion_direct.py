import requests
import json
import uuid
import logging
import os
import time
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# API base URL - adjust as needed for your environment
BASE_URL = "http://localhost:8000"  # Change this to match your server address

def test_gcs_file_ingestion_api():
    """
    Test the GCS file ingestion API endpoint directly using requests.
    """
    # Generate a unique file ID
    file_id = str(uuid.uuid4())
    organization_id = "test-org-123"
    
    # Create a test GCS path (this would be a real GCS path in production)
    gcs_path = f"gs://test-bucket/documents/sample-{file_id}.pdf"
    
    # Create the request payload
    request_data = {
        "file_id": file_id,
        "organization_id": organization_id,
        "gcs_path": gcs_path,
        "tenant_id": "default",
        "metadata": {
            "source": "test",
            "document_type": "pdf",
            "tags": ["test", "sample"]
        }
    }
    
    # API endpoint
    endpoint = f"{BASE_URL}/rag/ingest/gcs-file"
    
    # Headers - add your API key or authentication token here
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.environ.get('API_KEY', 'test-key')}"
    }
    
    logger.info(f"Sending request to {endpoint}")
    logger.info(f"Request data: {json.dumps(request_data, indent=2)}")
    
    # Send the request
    try:
        response = requests.post(
            endpoint,
            json=request_data,
            headers=headers
        )
        
        # Log the response status and content
        logger.info(f"Response status code: {response.status_code}")
        logger.info(f"Response content: {response.text}")
        
        # Check if the request was successful
        if response.status_code == 200:
            response_data = response.json()
            job_id = response_data.get("job_id")
            logger.info(f"Successfully initiated GCS file ingestion with job ID: {job_id}")
            return job_id
        else:
            logger.error(f"Request failed with status code {response.status_code}")
            logger.error(f"Response: {response.text}")
            return None
            
    except Exception as e:
        logger.error(f"Error sending request: {str(e)}")
        return None

def test_invalid_gcs_path():
    """
    Test the API with an invalid GCS path.
    """
    # Create a request with an invalid GCS path
    request_data = {
        "file_id": str(uuid.uuid4()),
        "organization_id": "test-org-123",
        "gcs_path": "invalid-path",  # Not a valid GCS path
        "tenant_id": "default"
    }
    
    # API endpoint
    endpoint = f"{BASE_URL}/rag/ingest/gcs-file"
    
    # Headers
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.environ.get('API_KEY', 'test-key')}"
    }
    
    logger.info(f"Testing with invalid GCS path")
    logger.info(f"Request data: {json.dumps(request_data, indent=2)}")
    
    # Send the request
    try:
        response = requests.post(
            endpoint,
            json=request_data,
            headers=headers
        )
        
        logger.info(f"Response status code: {response.status_code}")
        logger.info(f"Response content: {response.text}")
        
        # The request should be accepted but the processing should fail
        if response.status_code == 200:
            response_data = response.json()
            job_id = response_data.get("job_id")
            logger.info(f"Successfully initiated GCS file ingestion with invalid path, job ID: {job_id}")
            return job_id
        else:
            logger.error(f"Request failed with status code {response.status_code}")
            logger.error(f"Response: {response.text}")
            return None
            
    except Exception as e:
        logger.error(f"Error sending request: {str(e)}")
        return None

def test_missing_required_field():
    """
    Test the API with missing required fields.
    """
    # Create an incomplete request payload
    request_data = {
        "file_id": str(uuid.uuid4()),
        # Missing organization_id
        "gcs_path": "gs://test-bucket/documents/sample.pdf",
        "tenant_id": "default"
    }
    
    # API endpoint
    endpoint = f"{BASE_URL}/rag/ingest/gcs-file"
    
    # Headers
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.environ.get('API_KEY', 'test-key')}"
    }
    
    logger.info(f"Testing with missing required field (organization_id)")
    logger.info(f"Request data: {json.dumps(request_data, indent=2)}")
    
    # Send the request
    try:
        response = requests.post(
            endpoint,
            json=request_data,
            headers=headers
        )
        
        logger.info(f"Response status code: {response.status_code}")
        logger.info(f"Response content: {response.text}")
        
        # We expect a validation error (422)
        if response.status_code == 422:
            logger.info("Successfully validated that missing required fields are caught")
            return True
        else:
            logger.error(f"Unexpected status code {response.status_code}, expected 422")
            return False
            
    except Exception as e:
        logger.error(f"Error sending request: {str(e)}")
        return False

if __name__ == "__main__":
    logger.info("Starting direct API tests for GCS file ingestion")
    
    # Make sure the server is running before testing
    logger.info(f"Ensure your API server is running at {BASE_URL}")
    # No need to wait for input in non-interactive environment
    logger.info("Proceeding with tests...")
    
    # Run the tests
    logger.info("Running test with valid data...")
    job_id = test_gcs_file_ingestion_api()
    if job_id:
        logger.info(f"✅ Valid data test passed with job ID: {job_id}")
    else:
        logger.error("❌ Valid data test failed")
    
    logger.info("\nRunning test with invalid GCS path...")
    job_id_invalid = test_invalid_gcs_path()
    if job_id_invalid:
        logger.info(f"✅ Invalid path test passed with job ID: {job_id_invalid}")
    else:
        logger.error("❌ Invalid path test failed")
    
    logger.info("\nRunning test with missing required field...")
    if test_missing_required_field():
        logger.info("✅ Missing field test passed")
    else:
        logger.error("❌ Missing field test failed")
    
    logger.info("\nAll tests completed!")