#!/bin/bash

# Test the URL ingestion API endpoint using curl
echo "Testing URL ingestion API endpoint..."

# Create a JSON payload file
cat > ingest_url_payload.json << EOF
{
  "tenant_id": "default",
  "url": "https://httpbin.org/html",
  "metadata": {
    "source": "wikipedia",
    "author": "Test User",
    "created_at": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
    "document_type": "reference",
    "tags": ["ai", "test", "ingestion"],
    "additional_metadata": {
      "priority": "medium",
      "department": "Research"
    }
  }
}
EOF

# Execute the curl command
curl -X POST \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your_api_key_here" \
  -d @ingest_url_payload.json \
  http://localhost:8000/api/v1/rag/ingest/url | jq .

echo "Test completed!"

# Test with minimal data
echo "Testing URL ingestion API endpoint with minimal data..."

# Create a minimal JSON payload file
cat > ingest_url_minimal_payload.json << EOF
{
  "tenant_id": "default",
  "url": "https://httpbin.org/json"
}
EOF

# Execute the curl command with minimal data
curl -X POST \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your_api_key_here" \
  -d @ingest_url_minimal_payload.json \
  http://localhost:8000/api/v1/rag/ingest/url | jq .

echo "Minimal test completed!"