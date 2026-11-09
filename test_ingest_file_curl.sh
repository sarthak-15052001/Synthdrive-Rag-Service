#!/bin/bash

# Test the file ingestion API endpoint using curl
echo "Testing file ingestion API endpoint..."

# Define variables
API_URL="http://localhost:8000/api/v1/rag/ingest/file"
TEST_FILE="test_sample.txt"
TENANT_ID="default"
API_KEY="your_api_key_here"  # Replace with your actual API key or use environment variable

# Check if the test file exists
if [ ! -f "$TEST_FILE" ]; then
    echo "Error: Test file not found: $TEST_FILE"
    exit 1
fi

# Execute the curl command to upload the file
echo "Uploading file $TEST_FILE to $API_URL..."
RESPONSE=$(curl -s -X POST \
    -H "Authorization: Bearer $API_KEY" \
    -F "tenant_id=$TENANT_ID" \
    -F "file=@$TEST_FILE" \
    $API_URL)

# Check if curl command was successful
if [ $? -ne 0 ]; then
    echo "Error: Failed to execute curl command"
    exit 1
fi

# Display the response
echo "Response:"
echo $RESPONSE | jq .

# Extract job_id from the response
JOB_ID=$(echo $RESPONSE | jq -r '.job_id')

if [ "$JOB_ID" != "null" ] && [ ! -z "$JOB_ID" ]; then
    echo "Successfully initiated file ingestion with job ID: $JOB_ID"
    echo "Test completed successfully!"
else
    echo "Error: Failed to get job_id from response"
    exit 1
fi