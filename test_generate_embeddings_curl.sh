#!/bin/bash

# Test the generate-embeddings API endpoint using curl
echo "Testing generate-embeddings API endpoint..."

# Set the base URL for the API
BASE_URL="http://localhost:8000"
API_URL="${BASE_URL}/api/v1/rag/ingest/generate-embeddings"

# Use the existing payload file
PAYLOAD_FILE="generate_embeddings_payload.json"

echo "==================================================================="
echo "TESTING GENERATE EMBEDDINGS API WITH CURL"
echo "URL: ${API_URL}"
echo "==================================================================="

# Execute the curl command
curl -X POST \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer test-token" \
  -d @${PAYLOAD_FILE} \
  ${API_URL} | jq .

echo "==================================================================="
echo "Test completed at $(date)"