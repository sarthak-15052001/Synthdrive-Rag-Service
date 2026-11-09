#!/bin/bash

# Test the document ingestion API endpoint using curl

# Configuration
API_URL="http://localhost:8000/api/v1/rag/ingest/document"
API_KEY="your_api_key_here"  # Replace with your actual API key

# Create a JSON payload file
cat > ingest_document_payload.json << 'EOF'
{
  "tenant_id": "default",
  "content": "SynthDrive Inc. is working on a new AI project called Project Horizon. The project is led by Dr. Sarah Johnson, who joined the company in 2023. The team is using OpenAI's GPT-4 and Google's BERT models for natural language processing tasks. They are collaborating with Microsoft on cloud infrastructure. The project deadline is December 15, 2025, and they plan to present at the AI Summit in San Francisco.",
  "metadata": {
    "source": "test_document",
    "author": "Test User",
    "created_at": "2025-10-25T00:00:00Z",
    "document_type": "test",
    "tags": ["test", "document", "ingestion"],
    "additional_metadata": {
      "priority": "high",
      "department": "R&D"
    }
  }
}
EOF

# Execute the curl command
echo "Sending request to $API_URL..."
curl -X POST "$API_URL" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $API_KEY" \
  -d @ingest_document_payload.json \
  | jq .

echo "Done!"