#!/bin/bash

# Test the extract entities and relations API endpoint using curl
echo "Testing extract entities and relations API endpoint..."

# Create a JSON payload file
cat > extract_entities_payload.json << EOF
{
  "file_id": "test-file-123",
  "organization_id": "test-org-456",
  "tenant_id": "default",
  "raw_text": "SynthDrive Inc. is working on a new AI project called Project Horizon. The project is led by Dr. Sarah Johnson, who joined the company in 2023. The team is using OpenAI's GPT-4 and Google's BERT models for natural language processing tasks. They are collaborating with Microsoft on cloud infrastructure. The project deadline is December 15, 2025, and they plan to present at the AI Summit in San Francisco.",
  "status": "processing",
  "processing_log": ["Test started via curl"]
}
EOF

# Execute the curl command
curl -X POST \
  -H "Content-Type: application/json" \
  -d @extract_entities_payload.json \
  http://localhost:8000/api/v1/rag/ingest/extract-entities-relations | jq .

echo "Test completed!"