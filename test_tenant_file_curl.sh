#!/bin/bash

# Test the tenant file ingestion API endpoint using curl
echo "Testing tenant file ingestion API endpoint..."

# Define variables
API_URL="http://localhost:8000/api/v1/rag/ingest/tenant-file"
TEST_FILE="test_sample.txt"
ORGANIZATION_ID="test-org-1"
TENANT_ID="default"
FILE_TAGS="test,sample,documentation"
# API_KEY="your_api_key_here"  # Not needed for development environment as it allows unauthenticated access

# Check if the test file exists
if [ ! -f "$TEST_FILE" ]; then
    echo "Error: Test file not found: $TEST_FILE"
    exit 1
fi

# Execute the curl command to upload the file
echo "Uploading file $TEST_FILE to $API_URL..."
echo "Using organization_id: $ORGANIZATION_ID"
RESPONSE=$(curl -s -X POST \
    -F file=@"$TEST_FILE" \
    "$API_URL?organization_id=$ORGANIZATION_ID&tenant_id=$TENANT_ID&file_tags=$FILE_TAGS")

# Check if curl command was successful
if [ $? -ne 0 ]; then
    echo "Error: Failed to execute curl command"
    exit 1
fi

# Display the response
echo "Response:"
echo $RESPONSE

# Check if jq is installed
if command -v jq &> /dev/null; then
    echo "Formatted response:"
    echo $RESPONSE | jq .
    # Extract job_id from the response
    JOB_ID=$(echo $RESPONSE | jq -r '.job_id')
else
    echo "jq not installed, parsing response manually"
    # Simple parsing to extract job_id
    JOB_ID=$(echo $RESPONSE | grep -o '"job_id":"[^"]*"' | cut -d'"' -f4)
fi

if [ "$JOB_ID" != "null" ] && [ ! -z "$JOB_ID" ]; then
    echo "Successfully initiated tenant file ingestion with job ID: $JOB_ID"
    echo "Test completed successfully!"
else
    echo "Error: Failed to get job_id from response"
    exit 1
fi