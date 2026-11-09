import requests
import json
from datetime import datetime

def test_tenant_file_search():
    """
    Test the tenant file search API endpoint using Python requests.
    """
    # Define variables
    api_url = "http://localhost:8000/api/v1/rag/tenant-files/search"
    organization_id = "test-org-1"
    tenant_id = "default"
    query = "This is a sample text file for testing the file ingestion endpoint"
    
    # Prepare the headers and payload
    headers = {
        "Content-Type": "application/json"
    }
    
    # Prepare the payload
    payload = {
        "query": query,
        "organization_id": organization_id,
        "tenant_id": tenant_id,
        "filters": {},
        "limit": 5
    }
    
    print(f"Searching for '{query}' in organization {organization_id}...")
    
    # Make the POST request
    response = requests.post(
        api_url,
        headers=headers,
        json=payload
    )
    
    # Check if the request was successful
    if response.status_code == 200:
        response_data = response.json()
        print("Response:")
        print(json.dumps(response_data, indent=2))
        
        # Extract results from the response
        results = response_data.get("files", [])
        
        if results:
            print(f"Found {len(results)} results")
            for i, result in enumerate(results):
                print(f"\nResult {i+1}:")
                print(f"  File Name: {result.get('file_name', 'unknown')}")
                print(f"  Organization ID: {result.get('organization_id', 'unknown')}")
                print(f"  Content: {result.get('content_chunk', '')[:100]}...")
                print(f"  Relevance: {result.get('relevance_score', 0)}")
            return True
        else:
            print("No results found. The file might still be processing.")
            return False
    else:
        print(f"Error: Request failed with status code {response.status_code}")
        print(f"Response: {response.text}")
        return False

if __name__ == "__main__":
    print(f"Starting tenant file search test at {datetime.now().isoformat()}")
    # Wait longer for the file to be processed
    import time
    print("Waiting 20 seconds for the file to be processed...")
    time.sleep(20)
    
    result = test_tenant_file_search()
    print(f"Test {'succeeded' if result else 'failed'}")