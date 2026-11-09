import asyncio
import json
import logging
import os
import uuid
from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient

from src.main import app
from src.api.v1.schemas import GCSFileIngestionRequest, IngestResponse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create a test client
client = TestClient(app)

def test_gcs_file_ingestion():
    """
    Test the GCS file ingestion endpoint.
    
    This test simulates sending a request to ingest a file from GCS.
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
    
    # Send the request to the endpoint
    response = client.post(
        "/rag/ingest/gcs-file",
        json=request_data,
        headers={"Authorization": f"Bearer {os.environ.get('TEST_API_KEY', 'test-key')}"}
    )
    
    # Check the response
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}: {response.text}"
    
    # Parse the response
    response_data = response.json()
    
    # Verify the response contains a job_id
    assert "job_id" in response_data, "Response does not contain job_id"
    assert isinstance(response_data["job_id"], str), "job_id is not a string"
    
    logger.info(f"Successfully initiated GCS file ingestion with job ID: {response_data['job_id']}")
    
    # In a real test, you might want to poll for the job status or check the database
    # to verify the document was properly ingested
    
    return response_data["job_id"]

def test_gcs_file_ingestion_missing_fields():
    """
    Test the GCS file ingestion endpoint with missing required fields.
    """
    # Create an incomplete request payload
    request_data = {
        "file_id": str(uuid.uuid4()),
        # Missing organization_id
        "gcs_path": "gs://test-bucket/documents/sample.pdf",
        "tenant_id": "default"
    }
    
    # Send the request to the endpoint
    response = client.post(
        "/rag/ingest/gcs-file",
        json=request_data,
        headers={"Authorization": f"Bearer {os.environ.get('TEST_API_KEY', 'test-key')}"}
    )
    
    # Check that we get a validation error
    assert response.status_code == 422, f"Expected status code 422, got {response.status_code}: {response.text}"
    
    logger.info("Successfully validated that missing required fields are caught")

def test_gcs_file_ingestion_invalid_path():
    """
    Test the GCS file ingestion endpoint with an invalid GCS path.
    """
    # Create a request with an invalid GCS path
    request_data = {
        "file_id": str(uuid.uuid4()),
        "organization_id": "test-org-123",
        "gcs_path": "invalid-path", # Not a valid GCS path
        "tenant_id": "default"
    }
    
    # Send the request to the endpoint
    response = client.post(
        "/rag/ingest/gcs-file",
        json=request_data,
        headers={"Authorization": f"Bearer {os.environ.get('TEST_API_KEY', 'test-key')}"}
    )
    
    # The request should be accepted but the processing should fail
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}: {response.text}"
    
    # Parse the response
    response_data = response.json()
    
    # Verify the response contains a job_id
    assert "job_id" in response_data, "Response does not contain job_id"
    
    logger.info(f"Successfully initiated GCS file ingestion with invalid path, job ID: {response_data['job_id']}")
    
    # In a real test, you would check that the job status eventually becomes 'failed'
    
    return response_data["job_id"]

if __name__ == "__main__":
    # Run the tests
    logger.info("Running GCS file ingestion tests...")
    
    try:
        job_id = test_gcs_file_ingestion()
        logger.info(f"Test passed with job ID: {job_id}")
        
        test_gcs_file_ingestion_missing_fields()
        logger.info("Missing fields test passed")
        
        job_id_invalid = test_gcs_file_ingestion_invalid_path()
        logger.info(f"Invalid path test passed with job ID: {job_id_invalid}")
        
        logger.info("All tests passed!")
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        raise