import requests
import json
import os
from datetime import datetime

# Set the base URL for the API
base_url = "http://localhost:8000"

# Sample text to be chunked
sample_text = """
SynthDrive RAG Service is a powerful retrieval-augmented generation system designed to enhance AI applications with accurate, contextual information retrieval. 

The system combines vector search capabilities with knowledge graph technologies to provide comprehensive and relevant responses to user queries. It features multi-tenant architecture for data isolation, supports various document types, and offers semantic chunking for optimal text processing.

Key features include:
1. Hybrid retrieval combining vector search and graph-based knowledge retrieval
2. Semantic chunking for meaningful text segmentation
3. Entity extraction and relationship mapping
4. Multi-tenant data isolation
5. Support for various document types including PDFs, text files, and structured data

The ingestion pipeline processes documents through several stages:
- Document loading and parsing
- Semantic chunking
- Entity extraction
- Vector embedding generation
- Storage in vector and graph databases

This test demonstrates the semantic chunking capabilities of the system, which breaks text into meaningful segments based on semantic coherence rather than arbitrary character counts.
"""

# Create the request payload
payload = {
    "file_id": "test-file-001",
    "organization_id": "test-org-001",
    "tenant_id": "default",
    "raw_text": sample_text,
    "gcs_path": "gs://synthdrive-rag/test-documents/test-file-001.txt",
    "status": "processing",
    "processing_log": [f"Test chunking started at {datetime.now().isoformat()}"]
}

# Set headers for the request
headers = {
    "Content-Type": "application/json",
    # Add authorization if required
    "Authorization": "Bearer test-token"
}

def test_chunk_text_api():
    """Test the chunk text API endpoint"""
    print("Testing chunk text API endpoint...")
    
    # Make the API request
    response = requests.post(
        f"{base_url}/api/v1/rag/ingest/chunk-text",
        json=payload,
        headers=headers
    )
    
    # Print the status code
    print(f"Status Code: {response.status_code}")
    
    # Check if the request was successful
    if response.status_code == 200:
        # Parse the response
        result = response.json()
        
        # Print the number of chunks created
        print(f"Successfully created {len(result.get('chunks', []))} chunks")
        
        # Print the first chunk as an example
        if result.get('chunks'):
            print("\nExample chunk:")
            first_chunk = result.get('chunks')[0]
            print(f"Content: {first_chunk.get('content')}")
            print(f"Metadata: {json.dumps(first_chunk.get('metadata'), indent=2)}")
        
        # Print the processing log
        print("\nProcessing Log:")
        for log_entry in result.get('processing_log', []):
            print(f"- {log_entry}")
            
        return result
    else:
        # Print the error message
        print(f"Error: {response.text}")
        return None

if __name__ == "__main__":
    test_chunk_text_api()