#!/bin/bash

# Generate a random UUID for file_id
FILE_ID=$(cat /proc/sys/kernel/random/uuid)
ORGANIZATION_ID="test-org-123"
GCS_PATH="gs://test-bucket/documents/sample-${FILE_ID}.pdf"

# API endpoint
URL="http://localhost:8000/api/v1/rag/ingest/gcs-file"

# Create the JSON payload
PAYLOAD=$(cat <<EOF
{
  "file_id": "${FILE_ID}",
  "organization_id": "${ORGANIZATION_ID}",
  "gcs_path": "${GCS_PATH}",
  "tenant_id": "default",
  "metadata": {
    "source": "test",
    "document_type": "pdf",
    "tags": ["test", "sample"]
  }
}
EOF
)

echo "==================================================================="
echo "TESTING GCS FILE INGESTION API WITH CURL"
echo "URL: ${URL}"
echo "Payload:"
echo "${PAYLOAD}" | jq '.'
echo "==================================================================="

# Make the API call
curl -X POST "${URL}" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer test-key" \
  -d "${PAYLOAD}" \
  -v | jq '.'

echo "==================================================================="
echo "Test completed at $(date)"