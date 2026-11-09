#!/bin/bash

# Test the chunk-text API endpoint using curl
echo "Testing chunk-text API endpoint..."

# Create a JSON payload file
cat > chunk_text_payload.json << EOF
{
  "file_id": "test-file-001",
  "organization_id": "test-org-001",
  "tenant_id": "default",
  "raw_text": "SynthDrive RAG Service is a powerful retrieval-augmented generation system designed to enhance AI applications with accurate, contextual information retrieval.

The system combines vector search capabilities with knowledge graph technologies to provide comprehensive and relevant responses to user queries. It features multi-tenant architecture for data isolation, supports various document types, and offers semantic chunking for optimal text processing.

Key features include:
1. Hybrid retrieval combining vector search and graph-based knowledge retrieval
2. Semantic chunking for meaningful text segmentation
3. Entity extraction and relationship mapping
4. Multi-tenant data isolation
5. Support for various document types including PDFs, text files, and structured data

The ingestion pipeline processes documents through several stages:
- Document loading and parsing
- Semantic chunking
- Entity extraction
- Vector embedding generation
- Storage in vector and graph databases

This test demonstrates the semantic chunking capabilities of the system, which breaks text into meaningful segments based on semantic coherence rather than arbitrary character counts.",
  "gcs_path": "gs://synthdrive-rag/test-documents/test-file-001.txt",
  "status": "processing",
  "processing_log": ["Test started via curl"]
}
EOF

echo "==================================================================="
echo "TESTING CHUNK TEXT API WITH CURL"
echo "URL: http://localhost:8000/api/v1/rag/ingest/chunk-text"
echo "==================================================================="

# Execute the curl command
curl -X POST \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer test-token" \
  -d @chunk_text_payload.json \
  http://localhost:8000/api/v1/rag/ingest/chunk-text | jq .

echo "==================================================================="
echo "Test completed at $(date)"