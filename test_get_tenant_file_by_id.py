import requests
import json

# Base URL for the API
BASE_URL = "http://localhost:8000/api/v1"

# Test data
TEST_FILE_ID = "test-file-123"  # The file ID from the error message
TEST_ORG_ID = "test-org-456"    # The organization ID from the error message
TEST_TENANT_ID = "default"

def test_get_file_by_id():
    """Test getting a specific file by ID"""
    print(f"\n=== Testing Get File by ID: {TEST_FILE_ID} ===")
    
    # Make the request
    url = f"{BASE_URL}/rag/tenant-files/{TEST_FILE_ID}"
    params = {
        "organization_id": TEST_ORG_ID,
        "tenant_id": TEST_TENANT_ID
    }
    
    print(f"Making request to: {url}")
    print(f"With parameters: {params}")
    
    response = requests.get(url, params=params)
    
    # Check response
    print(f"Status code: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        file = response.json()
        print(f"✅ Successfully retrieved file: {file.get('file_name')}")
        print(f"  Content Chunk: {file.get('content_chunk')[:50]}...")
        return file
    else:
        print(f"❌ Get file failed with status code: {response.status_code}")
        print(f"Error: {response.text}")
        return None

if __name__ == "__main__":
    print("Starting tenant file retrieval test...")
    test_get_file_by_id()
    print("\nTest completed!")