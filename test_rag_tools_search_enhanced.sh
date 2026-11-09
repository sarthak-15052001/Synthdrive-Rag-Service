#!/bin/bash

# Enhanced test script for the RAG tools search API endpoint using curl
# This script tests various scenarios including error handling and different filter combinations

# Set colors for better readability
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Base URL for the API (can be overridden with command line argument)
BASE_URL=${1:-"http://localhost:8000/api/v1"}

# Define the endpoint
ENDPOINT="rag/tools/search"
API_URL="${BASE_URL}/${ENDPOINT}"

# Function to make API requests and display results
make_request() {
    local test_name=$1
    local payload=$2
    
    echo -e "\n${BLUE}=======================================================${NC}"
    echo -e "${GREEN}Test Case: ${test_name}${NC}"
    echo -e "${BLUE}=======================================================${NC}"
    
    echo -e "${YELLOW}Request Payload:${NC}"
    echo "$payload" | jq '.' 2>/dev/null || echo "$payload"
    
    echo -e "\n${YELLOW}Sending request to ${API_URL}...${NC}"
    
    # Execute the curl command and capture the response
    response=$(curl -s -X POST "$API_URL" \
        -H "Content-Type: application/json" \
        -d "$payload")
    
    # Get the HTTP status code
    status_code=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$API_URL" \
        -H "Content-Type: application/json" \
        -d "$payload")
    
    echo -e "\n${YELLOW}Response Status Code: ${status_code}${NC}"
    echo -e "${YELLOW}Response:${NC}"
    
    # Pretty print the JSON response if possible
    echo "$response" | jq '.' 2>/dev/null || echo "$response"
    
    # Check if the response contains tools and count them
    if echo "$response" | jq -e '.tools' >/dev/null 2>&1; then
        tool_count=$(echo "$response" | jq '.tools | length')
        echo -e "\n${GREEN}Found ${tool_count} tools in the response${NC}"
    fi
}

echo -e "${GREEN}Testing RAG tools search API endpoint...${NC}"
echo -e "${YELLOW}Base URL: ${BASE_URL}${NC}"
echo -e "${YELLOW}API URL: ${API_URL}${NC}"

# Test case 1: Basic search for video tools
PAYLOAD_1=$(cat <<EOF
{
  "query": "find a tool to make videos from text",
  "tenant_id": "default",
  "limit": 5
}
EOF
)

make_request "Basic search for video tools" "$PAYLOAD_1"

# Test case 2: Search for coding tools
PAYLOAD_2=$(cat <<EOF
{
  "query": "I need something to help with coding",
  "tenant_id": "default",
  "limit": 3
}
EOF
)

make_request "Search for coding tools" "$PAYLOAD_2"

# Test case 3: Search with category filter
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

make_request "Search with category filter" "$PAYLOAD_3"

# Test case 4: Search with minimum parameters
PAYLOAD_4=$(cat <<EOF
{
  "query": "data visualization"
}
EOF
)

make_request "Search with minimum parameters" "$PAYLOAD_4"

# Test case 5: Search with tags filter
PAYLOAD_5=$(cat <<EOF
{
  "query": "content creation tools",
  "tenant_id": "default",
  "filters": {
    "tags": ["video", "marketing"]
  },
  "limit": 5
}
EOF
)

make_request "Search with tags filter" "$PAYLOAD_5"

# Test case 6: Search with rating filter
PAYLOAD_6=$(cat <<EOF
{
  "query": "high quality AI tools",
  "tenant_id": "default",
  "filters": {
    "rating": 4.5
  },
  "limit": 5
}
EOF
)

make_request "Search with rating filter" "$PAYLOAD_6"

# Test case 7: Search with combined filters
PAYLOAD_7=$(cat <<EOF
{
  "query": "AI development tools",
  "tenant_id": "default",
  "filters": {
    "category": "Development",
    "tags": ["coding", "programming"],
    "rating": 4.0
  },
  "limit": 5
}
EOF
)

make_request "Search with combined filters" "$PAYLOAD_7"

# Test case 8: Error handling - empty query
PAYLOAD_8=$(cat <<EOF
{
  "query": "",
  "tenant_id": "default",
  "limit": 5
}
EOF
)

make_request "Error handling - empty query" "$PAYLOAD_8"

# Test case 9: Error handling - invalid limit
PAYLOAD_9=$(cat <<EOF
{
  "query": "AI tools",
  "tenant_id": "default",
  "limit": -1
}
EOF
)

make_request "Error handling - invalid limit" "$PAYLOAD_9"

# Test case 10: Error handling - invalid filter format
PAYLOAD_10=$(cat <<EOF
{
  "query": "AI tools",
  "tenant_id": "default",
  "filters": "invalid_filter",
  "limit": 5
}
EOF
)

make_request "Error handling - invalid filter format" "$PAYLOAD_10"

echo -e "\n${GREEN}All tests completed.${NC}"
echo -e "${YELLOW}Usage: $0 [base_url]${NC}"
echo -e "${YELLOW}Example: $0 http://api.example.com/api/v1${NC}"