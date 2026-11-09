#!/bin/bash

# Test script for the Kernel of Truth API endpoint using curl

echo "Testing Kernel of Truth API endpoint..."

# API endpoint URL (adjust if needed)
URL="http://localhost:8000/api/v1/rag/kernel-of-truth/query"

# Sample request payload
PAYLOAD=$(cat <<EOF
{
  "query": "What workflows did user John create?",
  "tenant_id": "default",
  "max_depth": 3,
  "limit": 10
}
EOF
)

# Send the request
echo "Sending request to $URL with payload: $PAYLOAD"
curl -X POST "$URL" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer test_token" \
  -d "$PAYLOAD" \
  -v

echo -e "\nTest completed."