import json
import requests
from datetime import datetime, timezone
import argparse
import sys

def test_persist_to_weaviate(api_key=None, verbose=False):
    """
    Test the persist_to_weaviate API endpoint.
    
    Args:
        api_key (str, optional): API key for authentication. Defaults to None.
        verbose (bool, optional): Whether to print detailed output. Defaults to False.
    
    Returns:
        requests.Response: The response from the API
    """
    # Configuration
    API_URL = "http://localhost:8000/api/v1/rag/ingest/persist-to-weaviate"
    
    # Sample data with embedded chunks
    payload = {
        "file_id": "test-file-123",
        "organization_id": "test-org-456",
        "tenant_id": "default",
        "chunks": [
            {
                "content": "This is a test chunk for Weaviate persistence.",
                "metadata": {
                    "chunk_id": 0,
                    "chunk_type": "semantic",
                    "semantic_type": "introduction",
                    "chunk_index": 0,
                    "total_chunks": 2,
                    "file_id": "test-file-123",
                    "organization_id": "test-org-456",
                    "chunking_method": "ai_semantic"
                },
                "vector": [0.021, -0.015, 0.042, 0.036, 0.018, -0.027, 0.031, -0.019, 0.022, 0.033]  # Sample vector (truncated)
            },
            {
                "content": "This is another test chunk for Weaviate persistence.",
                "metadata": {
                    "chunk_id": 1,
                    "chunk_type": "semantic",
                    "semantic_type": "explanation",
                    "chunk_index": 1,
                    "total_chunks": 2,
                    "file_id": "test-file-123",
                    "organization_id": "test-org-456",
                    "chunking_method": "ai_semantic"
                },
                "vector": [0.018, -0.022, 0.039, 0.041, 0.015, -0.031, 0.029, -0.017, 0.025, 0.036]  # Sample vector (truncated)
            }
        ],
        "status": "embedded",
        "processing_log": [
            f"Embedding generation completed at {datetime.now(timezone.utc).isoformat()}"
        ]
    }

    # Set headers with API key if provided
    headers = {
        "Content-Type": "application/json"
    }
    
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    
    if verbose:
        print("Request URL:", API_URL)
        print("Request Headers:", headers)
        print("Request Payload:", json.dumps(payload, indent=2))
    
    try:
        # Make the API request
        response = requests.post(API_URL, json=payload, headers=headers)
        
        # Print the response
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("Success! Response:")
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"Error! Status code: {response.status_code}")
            try:
                print(json.dumps(response.json(), indent=2))
            except:
                print(response.text)
        
        return response
    
    except requests.RequestException as e:
        print(f"Request failed: {e}")
        return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test the persist-to-weaviate API endpoint")
    parser.add_argument("--api-key", help="API key for authentication")
    parser.add_argument("--verbose", action="store_true", help="Print detailed output")
    
    args = parser.parse_args()
    
    response = test_persist_to_weaviate(api_key=args.api_key, verbose=args.verbose)
    
    # Exit with appropriate status code
    if response and response.status_code == 200:
        sys.exit(0)
    else:
        sys.exit(1)