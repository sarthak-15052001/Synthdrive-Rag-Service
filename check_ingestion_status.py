import requests
import json
import sys
import time

def check_ingestion_status(job_id):
    """
    Check the status of a file ingestion job.
    """
    # Define variables
    api_url = f"http://localhost:8000/api/v1/rag/ingest/status/{job_id}"
    
    # Prepare the headers
    headers = {
        "Content-Type": "application/json"
    }
    
    print(f"Checking ingestion status for job ID: {job_id}")
    
    # Make the GET request
    response = requests.get(
        api_url,
        headers=headers
    )
    
    # Check if the request was successful
    if response.status_code == 200:
        response_data = response.json()
        print("Response:")
        print(json.dumps(response_data, indent=2))
        return True
    else:
        print(f"Error: Request failed with status code {response.status_code}")
        print(f"Response: {response.text}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 check_ingestion_status.py <job_id>")
        sys.exit(1)
    
    job_id = sys.argv[1]
    
    # Check status every 5 seconds for 1 minute
    for i in range(12):
        print(f"\nCheck {i+1}/12:")
        result = check_ingestion_status(job_id)
        if i < 11:  # Don't sleep after the last check
            print("Waiting 5 seconds before next check...")
            time.sleep(5)