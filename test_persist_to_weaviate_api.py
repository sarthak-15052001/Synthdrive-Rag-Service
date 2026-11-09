import json
import requests
from datetime import datetime, timezone

# Configuration
API_URL = "http://localhost:8000/api/v1/rag/ingest/persist-to-weaviate"
API_KEY = "your_api_key_here"  # Replace with your actual API key

def test_persist_to_weaviate():
    """
    Test the persist_to_weaviate API endpoint.
    """
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

    # Set headers with API key
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }

    # Make the API request
    response = requests.post(API_URL, json=payload, headers=headers)

    # Print the response
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

    return response

if __name__ == "__main__":
    test_persist_to_weaviate()