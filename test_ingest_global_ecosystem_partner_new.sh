#!/bin/bash

# Test the global ecosystem partner ingestion API endpoint using curl with the new payload
echo "Testing global ecosystem partner ingestion API endpoint with new payload..."

# Execute the curl command
curl -X POST \
  -H "Content-Type: application/json" \
  -d @ecosystem_partner_payload_new.json \
  http://localhost:8000/api/v1/rag/ingest/global/ecosystem-partner

echo ""
echo "Test completed!"