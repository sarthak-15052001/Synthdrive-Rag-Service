import requests
import os
import json
from datetime import datetime

def test_tenant_file_ingestion():
    """
    Test the tenant file ingestion API endpoint using Python requests.
    """
    # Define variables
    api_url = "http://localhost:8000/api/v1/rag/ingest/tenant-file"
    test_file_path = "test_sample.txt"
    organization_id = "test-org-1"
    tenant_id = "default"
    file_tags = "test,sample,documentation"
    # api_key = "your_api_key_here"  # Not needed for development environment as it allows unauthenticated access
    
    # Check if the test file exists
    if not os.path.exists(test_file_path):
        print(f"Error: Test file not found: {test_file_path}")
        return False
    
    # Prepare the headers and files for the request
    # No authorization header needed for development environment
    headers = {}
    
    # Open the file in binary mode
    with open(test_file_path, "rb") as file:
        # Prepare the files for the request
        files = {
            "file": (os.path.basename(test_file_path), file, "text/plain")
        }
        
        # Prepare the query parameters
        params = {
            "organization_id": organization_id,
            "tenant_id": tenant_id,
            "file_tags": file_tags
        }
        
        print(f"Uploading file {test_file_path} to {api_url}...")
        
        # Make the POST request with query parameters
        response = requests.post(
            api_url,
            headers=headers,
            files=files,
            params=params
        )
    
    # Check if the request was successful
    if response.status_code == 200:
        response_data = response.json()
        print("Response:")
        print(json.dumps(response_data, indent=2))
        
        # Extract job_id from the response
        job_id = response_data.get("job_id")
        
        if job_id:
            print(f"Successfully initiated tenant file ingestion with job ID: {job_id}")
            print("Test completed successfully!")
            return True
        else:
            print("Error: Failed to get job_id from response")
            return False
    else:
        print(f"Error: Request failed with status code {response.status_code}")
        print(f"Response: {response.text}")
        return False

if __name__ == "__main__":
    print(f"Starting tenant file ingestion test at {datetime.now().isoformat()}")
    result = test_tenant_file_ingestion()
    print(f"Test {'succeeded' if result else 'failed'}")