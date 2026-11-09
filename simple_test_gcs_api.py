import requests
import json
import uuid
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# API base URL
BASE_URL = "http://localhost:8000"

def test_gcs_file_ingestion():
    """Simple test for the GCS file ingestion API endpoint"""
    
    # Generate test data
    file_id = str(uuid.uuid4())
    organization_id = "test-org-123"
    gcs_path = f"gs://test-bucket/documents/sample-{file_id}.pdf"
    
    # Create request payload
    payload = {
        "file_id": file_id,
        "organization_id": organization_id,
        "gcs_path": gcs_path,
        "tenant_id": "default",
        # Add metadata to match the expected schema
        "metadata": {
            "source": "test",
            "document_type": "pdf",
            "tags": ["test", "sample"]
        }
    }
    
    # API endpoint
    url = f"{BASE_URL}/api/v1/rag/ingest/gcs-file"
    
    # Headers
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer test-key"
    }
    
    logger.info(f"Sending request to {url}")
    logger.info(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        # Make the API call
        response = requests.post(url, json=payload, headers=headers)
        
        # Log response details
        logger.info(f"Response status code: {response.status_code}")
        logger.info(f"Response body: {response.text}")
        
        # Check if successful
        if response.status_code == 200:
            logger.info("✅ API call successful!")
            return True
        else:
            logger.error(f"❌ API call failed with status code {response.status_code}")
            return False
    
    except Exception as e:
        logger.error(f"❌ Error making API call: {str(e)}")
        return False

if __name__ == "__main__":
    logger.info("Testing GCS file ingestion API...")
    test_gcs_file_ingestion()