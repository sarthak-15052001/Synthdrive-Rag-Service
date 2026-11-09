import requests
import json
import os
from datetime import datetime

def test_generate_embeddings_api():
    """Test the generate embeddings API endpoint"""
    print("Testing generate embeddings API endpoint...")
    
    # Set the base URL for the API
    base_url = "http://localhost:8000"
    
    # Load the payload from the JSON file
    with open('generate_embeddings_payload.json', 'r') as f:
        payload = json.load(f)
    
    # Add a timestamp to the processing log
    payload["processing_log"].append(f"Test started at {datetime.now().isoformat()}")
    
    # Set headers for the request
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer test-token"
    }
    
    print("=================================================================")
    print(f"TESTING GENERATE EMBEDDINGS API WITH PYTHON")
    print(f"URL: {base_url}/api/v1/rag/ingest/generate-embeddings")
    print("=================================================================")
    
    # Make the API request
    response = requests.post(
        f"{base_url}/api/v1/rag/ingest/generate-embeddings",
        json=payload,
        headers=headers
    )
    
    # Print the status code
    print(f"Status Code: {response.status_code}")
    
    # Check if the request was successful
    if response.status_code == 200:
        # Parse the response
        result = response.json()
        
        # Print the number of chunks processed
        print(f"Successfully processed {len(result.get('chunks', []))} chunks")
        
        # Print the first chunk with embedding as an example
        if result.get('chunks'):
            print("\nExample chunk with embedding:")
            first_chunk = result.get('chunks')[0]
            print(f"Content: {first_chunk.get('content')}")
            
            # Print just the first few values of the embedding vector to avoid overwhelming output
            vector = first_chunk.get('vector', [])
            if vector:
                print(f"Embedding vector (first 5 values): {vector[:5]}")
                print(f"Vector dimensions: {len(vector)}")
            else:
                print("No embedding vector found in the response")
        
        # Print the processing log
        print("\nProcessing Log:")
        for log_entry in result.get('processing_log', []):
            print(f"- {log_entry}")
            
        print("=================================================================")
        print(f"Test completed at {datetime.now().isoformat()}")
        
        return result
    else:
        # Print the error message
        print(f"Error: {response.text}")
        print("=================================================================")
        print(f"Test failed at {datetime.now().isoformat()}")
        return None

if __name__ == "__main__":
    test_generate_embeddings_api()