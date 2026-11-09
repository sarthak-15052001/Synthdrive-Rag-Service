import requests
import json
import os
from datetime import datetime

# Set the base URL for the API
base_url = "http://localhost:8001"

# Sample chunks to generate embeddings for
sample_chunks = [
    {
        "content": "SynthDrive RAG Service is a powerful retrieval-augmented generation system designed to enhance AI applications with accurate, contextual information retrieval.",
        "metadata": {
            "chunk_id": 0,
            "chunk_type": "semantic",
            "semantic_type": "introduction",
            "chunk_index": 0,
            "total_chunks": 3,
            "file_id": "test-file-001",
            "organization_id": "test-org-001",
            "chunking_method": "ai_semantic"
        }
    },
    {
        "content": "The system combines vector search capabilities with knowledge graph technologies to provide comprehensive and relevant responses to user queries. It features multi-tenant architecture for data isolation, supports various document types, and offers semantic chunking for optimal text processing.",
        "metadata": {
            "chunk_id": 1,
            "chunk_type": "semantic",
            "semantic_type": "explanation",
            "chunk_index": 1,
            "total_chunks": 3,
            "file_id": "test-file-001",
            "organization_id": "test-org-001",
            "chunking_method": "ai_semantic"
        }
    },
    {
        "content": "Key features include hybrid retrieval combining vector search and graph-based knowledge retrieval, semantic chunking for meaningful text segmentation, entity extraction and relationship mapping, multi-tenant data isolation, and support for various document types.",
        "metadata": {
            "chunk_id": 2,
            "chunk_type": "semantic",
            "semantic_type": "features",
            "chunk_index": 2,
            "total_chunks": 3,
            "file_id": "test-file-001",
            "organization_id": "test-org-001",
            "chunking_method": "ai_semantic"
        }
    }
]

# Create the request payload
payload = {
    "file_id": "test-file-001",
    "organization_id": "test-org-001",
    "tenant_id": "default",
    "chunks": sample_chunks,
    "status": "processing",
    "processing_log": [f"Test embedding generation started at {datetime.now().isoformat()}"]
}

# Set headers for the request
headers = {
    "Content-Type": "application/json",
    # Add authorization if required
    "Authorization": "Bearer test-token"
}

def test_generate_embeddings_api():
    """Test the generate embeddings API endpoint"""
    print("Testing generate embeddings API endpoint...")
    
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
            
        return result
    else:
        # Print the error message
        print(f"Error: {response.text}")
        return None

if __name__ == "__main__":
    test_generate_embeddings_api()