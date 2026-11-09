import requests
import json
import uuid
import logging
import sys
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# API base URL
BASE_URL = "http://localhost:8000"

def test_gcs_file_ingestion():
    """
    Test the GCS file ingestion API endpoint
    """
    
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
    
    logger.info("=" * 80)
    logger.info(f"TESTING GCS FILE INGESTION API")
    logger.info(f"URL: {url}")
    logger.info(f"Payload: {json.dumps(payload, indent=2)}")
    logger.info("=" * 80)
    
    try:
        # Make the API call
        response = requests.post(url, json=payload, headers=headers)
        
        # Log detailed response information
        logger.info("RESPONSE DETAILS:")
        logger.info(f"Status Code: {response.status_code}")
        logger.info(f"Status Message: {response.reason}")
        logger.info(f"Headers: {json.dumps(dict(response.headers), indent=2)}")
        logger.info(f"Body: {response.text}")
        logger.info("=" * 80)
        
        # Check if successful
        if response.status_code == 200:
            logger.info("✅ API call successful!")
            response_data = response.json()
            logger.info(f"Job ID: {response_data.get('job_id')}")
            return response_data.get('job_id')
        else:
            logger.error(f"❌ API call failed with status code {response.status_code}")
            return None
    
    except Exception as e:
        logger.error(f"❌ Error making API call: {str(e)}")
        return None

if __name__ == "__main__":
    logger.info(f"Starting GCS file ingestion API test at {datetime.now().isoformat()}")
    job_id = test_gcs_file_ingestion()
    
    if job_id:
        logger.info(f"Test completed successfully with job ID: {job_id}")
    else:
        logger.error("Test failed")
    
    logger.info(f"Test finished at {datetime.now().isoformat()}")