#!/bin/bash

# Test the persist_to_weaviate API endpoint using curl

# Configuration
API_URL="http://localhost:8000/api/v1/rag/ingest/persist-to-weaviate"
API_KEY="your_api_key_here"  # Replace with your actual API key

# Create a JSON payload file
cat > persist_to_weaviate_payload.json << 'EOF'
{
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
      "vector": [0.021, -0.015, 0.042, 0.036, 0.018, -0.027, 0.031, -0.019, 0.022, 0.033]
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
      "vector": [0.018, -0.022, 0.039, 0.041, 0.015, -0.031, 0.029, -0.017, 0.025, 0.036]
    }
  ],
  "status": "embedded",
  "processing_log": ["Embedding generation completed"]
}
EOF

# Execute the curl command
echo "Sending request to $API_URL..."
curl -X POST "$API_URL" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $API_KEY" \
  -d @persist_to_weaviate_payload.json \
  | jq .

echo "Done!"