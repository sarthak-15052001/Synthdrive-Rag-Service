import os
import json
import logging
import requests
from uuid import uuid4

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_file_ingestion_api():
    """
    Test the file ingestion endpoint by uploading a sample file.
    
    This test uploads a file to the /api/v1/rag/ingest/file endpoint and verifies
    the response contains a job_id.
    """
    # API endpoint
    url = "http://localhost:8000/api/v1/rag/ingest/file"
    
    # Sample file path
    file_path = "test_sample.txt"
    
    # Check if the file exists
    if not os.path.exists(file_path):
        logger.error(f"Test file not found: {file_path}")
        return None
    
    # Tenant ID (optional, defaults to "default" in the API)
    tenant_id = "default"
    
    # API key for authorization
    api_key = os.environ.get("TEST_API_KEY", "your_api_key_here")
    
    # Prepare headers
    headers = {
        "Authorization": f"Bearer {api_key}"
    }
    
    # Prepare form data
    form_data = {
        "tenant_id": tenant_id
    }
    
    # Prepare file for upload
    files = {
        "file": (os.path.basename(file_path), open(file_path, "rb"), "text/plain")
    }
    
    try:
        logger.info(f"Uploading file {file_path} to {url}")
        
        # Send POST request
        response = requests.post(
            url,
            headers=headers,
            data=form_data,
            files=files
        )
        
        # Check response status code
        if response.status_code == 200:
            response_data = response.json()
            logger.info(f"Response: {json.dumps(response_data, indent=2)}")
            
            # Verify the response contains a job_id
            if "job_id" in response_data:
                logger.info(f"Successfully initiated file ingestion with job ID: {response_data['job_id']}")
                return response_data["job_id"]
            else:
                logger.error("Response does not contain job_id")
                return None
        else:
            logger.error(f"Request failed with status code {response.status_code}: {response.text}")
            return None
            
    except Exception as e:
        logger.error(f"Error during file ingestion test: {str(e)}")
        return None
    finally:
        # Close the file
        files["file"][1].close()

if __name__ == "__main__":
    logger.info("Starting file ingestion test...")
    
    try:
        job_id = test_file_ingestion_api()
        
        if job_id:
            logger.info(f"Test passed with job ID: {job_id}")
            logger.info("File ingestion test completed successfully!")
        else:
            logger.error("Test failed: No job ID returned")
    except Exception as e:
        logger.error(f"Test failed with exception: {str(e)}")