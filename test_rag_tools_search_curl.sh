#!/bin/bash

# Test the RAG tools search API endpoint using curl
echo "Testing RAG tools search API endpoint..."

# Base URL for the API
BASE_URL="http://localhost:8000/api/v1"

# Define the endpoint
ENDPOINT="rag/tools/search"
API_URL="${BASE_URL}/${ENDPOINT}"

# Test case 1: Basic search for video tools
echo -e "\n\nTest Case 1: Basic search for video tools"
echo "Query: find a tool to make videos from text"

# Create the JSON payload
PAYLOAD_1=$(cat <<EOF
{
  "query": "find a tool to make videos from text",
  "tenant_id": "default",
  "limit": 5
}
EOF
)

# Execute the curl command
echo "Sending request to $API_URL..."
curl -X POST "$API_URL" \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD_1"

# Test case 2: Search with different query
echo -e "\n\nTest Case 2: Search for coding tools"
echo "Query: I need something to help with coding"

# Create the JSON payload
PAYLOAD_2=$(cat <<EOF
{
  "query": "I need something to help with coding",
  "tenant_id": "default",
  "limit": 3
}
EOF
)

# Execute the curl command
echo "Sending request to $API_URL..."
curl -X POST "$API_URL" \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD_2"

# Test case 3: Search with filters
echo -e "\n\nTest Case 3: Search with category filter"
echo "Query: AI tools with category filter"

# Create the JSON payload
PAYLOAD_3=$(cat <<EOF
{
  "query": "AI tools",
  "tenant_id": "default",
  "filters": {
    "category": "Development"
  },
  "limit": 5
}
EOF
)

# Execute the curl command
echo "Sending request to $API_URL..."
curl -X POST "$API_URL" \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD_3"

# Test case 4: Search with minimum parameters
echo -e "\n\nTest Case 4: Search with minimum parameters"
echo "Query: data visualization"

# Create the JSON payload
PAYLOAD_4=$(cat <<EOF
{
  "query": "data visualization"
}
EOF
)

# Execute the curl command
echo "Sending request to $API_URL..."
curl -X POST "$API_URL" \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD_4"

echo -e "\n\nAll tests completed."