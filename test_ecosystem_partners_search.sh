#!/bin/bash

# API endpoint
URL="http://localhost:8000/api/v1/rag/ecosystem-partners/search"

# Replace with your actual token
TOKEN="your_token_here"

# Payload for the request
PAYLOAD='{
  "tenant_id": "default",
  "query": "supply chain experts",
  "filters": {},
  "limit": 5
}'

# Make the request using curl
curl -X POST "$URL" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d "$PAYLOAD" \
  | python -m json.tool  # Pretty print the JSON response