#!/bin/bash

# Test the RAG query API endpoint using curl
echo "Testing RAG query API endpoint..."

# Create a JSON payload file
cat > rag_query_payload.json << EOF
{
  "query_str": "What is SynthDrive RAG Service?",
  "tenant_id": "default",
  "top_k": 5
}
EOF

echo "==================================================================="
echo "TESTING RAG QUERY API WITH CURL"
echo "URL: http://localhost:8000/api/v1/rag/query"
echo "==================================================================="
echo "NOTE: If you see 'No reasoning available' or similar messages, it means:"
echo "1. The system may not have any data ingested yet"
echo "2. The query processing pipeline might not be generating reasoning"
echo "3. You may need to ingest some documents first using the ingestion endpoints"
echo "==================================================================="

# Execute the curl command
echo "Sending query: What is SynthDrive RAG Service?"
curl -X POST \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer test-token" \
  -d @rag_query_payload.json \
  --no-buffer \
  http://localhost:8000/api/v1/rag/query

echo -e "\n==================================================================="

# Try another query
echo "Sending query: How does the ingestion pipeline work?"
cat > rag_query_payload.json << EOF
{
  "query_str": "How does the ingestion pipeline work?",
  "tenant_id": "default",
  "top_k": 5
}
EOF

curl -X POST \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer test-token" \
  -d @rag_query_payload.json \
  --no-buffer \
  http://localhost:8000/api/v1/rag/query

echo -e "\n==================================================================="

# Try a third query
echo "Sending query: What are the key features of the system?"
cat > rag_query_payload.json << EOF
{
  "query_str": "What are the key features of the system?",
  "tenant_id": "default",
  "top_k": 5
}
EOF

curl -X POST \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer test-token" \
  -d @rag_query_payload.json \
  --no-buffer \
  http://localhost:8000/api/v1/rag/query

echo -e "\n==================================================================="
echo "Test completed at $(date)"

# Clean up
rm rag_query_payload.json