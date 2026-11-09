#!/bin/bash

# Test the persist_to_neo4j API endpoint using curl

# Configuration
API_URL="http://localhost:8000/api/v1/rag/ingest/persist-to-neo4j"
API_KEY="your_api_key_here"  # Replace with your actual API key

# Create a JSON payload file
cat > persist_to_neo4j_payload.json << 'EOF'
{
  "file_id": "test-file-123",
  "organization_id": "test-org-456",
  "tenant_id": "default",
  "entities_and_relations": {
    "entities": [
      {
        "id": "entity-1",
        "name": "John Doe",
        "type": "PERSON"
      },
      {
        "id": "entity-2",
        "name": "Acme Corporation",
        "type": "ORGANIZATION"
      },
      {
        "id": "entity-3",
        "name": "Project Alpha",
        "type": "PROJECT"
      }
    ],
    "relationships": [
      {
        "source": "John Doe",
        "target": "Acme Corporation",
        "type": "WORKS_FOR"
      },
      {
        "source": "John Doe",
        "target": "Project Alpha",
        "type": "MANAGES"
      },
      {
        "source": "Acme Corporation",
        "target": "Project Alpha",
        "type": "OWNS"
      }
    ]
  },
  "status": "entities_extracted",
  "processing_log": ["Entity extraction completed"]
}
EOF

# Execute the curl command
echo "Sending request to $API_URL..."
curl -X POST "$API_URL" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $API_KEY" \
  -d @persist_to_neo4j_payload.json \
  | jq .

echo "Done!"