#!/bin/bash

# Test the RAG query API endpoint using curl with direct document ingestion and querying
echo "Testing RAG query API with direct document ingestion and querying..."

# Step 1: Ingest a sample document
echo "==================================================================="
echo "STEP 1: INGESTING SAMPLE DOCUMENT"
echo "URL: http://localhost:8000/api/v1/rag/ingest/document"
echo "==================================================================="

# Create a JSON payload file for document ingestion
cat > rag_ingest_payload.json << EOF
{
  "content": "SynthDrive RAG Service is a powerful retrieval-augmented generation system designed to enhance AI applications with accurate, contextual information retrieval. The system combines vector search capabilities with knowledge graph technologies to provide comprehensive and relevant responses to user queries. It features multi-tenant architecture for data isolation, supports various document types, and offers semantic chunking for optimal text processing. Key features include: 1. Hybrid retrieval combining vector search and graph-based knowledge retrieval 2. Semantic chunking for meaningful text segmentation 3. Entity extraction and relationship mapping 4. Multi-tenant data isolation 5. Support for various document types including PDFs, text files, and structured data. The ingestion pipeline processes documents through several stages: - Document loading and parsing - Semantic chunking - Entity extraction - Vector embedding generation - Storage in vector and graph databases",
  "metadata": {
    "source": "SynthDrive Documentation",
    "author": "SynthDrive Team",
    "document_type": "documentation",
    "tags": ["rag", "documentation", "overview"]
  },
  "tenant_id": "default"
}
EOF

# Execute the curl command for document ingestion
INGEST_RESPONSE=$(curl -s -X POST \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer test-token" \
  -d @rag_ingest_payload.json \
  http://localhost:8000/api/v1/rag/ingest/document)

echo "Ingestion Response:"
echo $INGEST_RESPONSE

# We're not extracting the job_id since we don't have jq installed
echo "Waiting for document processing..."

# Step 2: Wait for processing
echo "==================================================================="
echo "STEP 2: WAITING FOR DOCUMENT PROCESSING (10 seconds)"
echo "==================================================================="
sleep 10

# Step 3: Query the system
echo "==================================================================="
echo "STEP 3: QUERYING THE SYSTEM"
echo "URL: http://localhost:8000/api/v1/rag/query"
echo "==================================================================="
echo "NOTE: If you see 'No reasoning available' or similar messages, it means:"
echo "1. The document might still be processing"
echo "2. The query processing pipeline might not be generating reasoning"
echo "3. There might be an issue with the vector database or graph database"
echo "==================================================================="

# Test queries
QUERIES=("What is SynthDrive RAG Service?" "How does the ingestion pipeline work?" "What are the key features of the system?")

for QUERY in "${QUERIES[@]}"; do
  echo "Sending query: $QUERY"
  
  # Create a JSON payload file for the query
  cat > rag_query_payload.json << EOF
  {
    "query_str": "$QUERY",
    "tenant_id": "default",
    "top_k": 5
  }
EOF

  # Execute the curl command for the query
  curl -X POST \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer test-token" \
    -d @rag_query_payload.json \
    --no-buffer \
    http://localhost:8000/api/v1/rag/query

  echo -e "\n==================================================================="
done

echo "Test completed at $(date)"

# Clean up
rm rag_ingest_payload.json rag_query_payload.json