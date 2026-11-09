#!/bin/bash

# Test script for the /api/v1/rag/vector-search-tenant-docs API endpoint using curl
# This script tests the API with the 5 payloads provided in the task

# Set the API endpoint URL
API_URL="http://localhost:8001/api/v1/rag/vector-search-tenant-docs"

# Set the content type header
CONTENT_TYPE="Content-Type: application/json"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Testing /api/v1/rag/vector-search-tenant-docs API endpoint...${NC}"
echo

# Function to test a payload
test_payload() {
    local payload_name=$1
    local payload=$2
    
    echo -e "${YELLOW}Testing Payload $payload_name:${NC}"
    echo "$payload" | jq '.'
    echo
    
    # Make the API request
    response=$(curl -s -X POST -H "$CONTENT_TYPE" -d "$payload" "$API_URL")
    
    # Check if the response is valid JSON
    if echo "$response" | jq '.' &>/dev/null; then
        echo -e "${GREEN}Response:${NC}"
        echo "$response" | jq '.'
        
        # Check if the response contains the expected fields
        if echo "$response" | jq -e '.query' &>/dev/null && \
           echo "$response" | jq -e '.organization_id' &>/dev/null && \
           echo "$response" | jq -e '.files' &>/dev/null; then
            echo -e "${GREEN}✓ Response contains the expected fields${NC}"
            
            # Check if the organization_id is correct
            org_id=$(echo "$payload" | jq -r '.organization_id')
            resp_org_id=$(echo "$response" | jq -r '.organization_id')
            if [ "$org_id" = "$resp_org_id" ]; then
                echo -e "${GREEN}✓ organization_id is correct: $resp_org_id${NC}"
            else
                echo -e "${RED}✗ organization_id is incorrect: expected $org_id, got $resp_org_id${NC}"
            fi
            
            # Check if files array exists
            files_count=$(echo "$response" | jq '.files | length')
            echo -e "${GREEN}✓ Found $files_count files in the response${NC}"
        else
            echo -e "${RED}✗ Response does not contain the expected fields${NC}"
        fi
    else
        echo -e "${RED}✗ Invalid JSON response:${NC}"
        echo "$response"
    fi
    
    echo -e "${YELLOW}----------------------------------------${NC}"
    echo
}

# Payload 1: Search for financial documents
payload1='{
  "query": "financial performance report for 2023",
  "organization_id": "test_org_123",
  "tenant_id": "default",
  "filters": {
    "file_type": "pdf",
    "tags": ["financial", "2023"]
  },
  "limit": 5
}'

# Payload 2: Search for marketing strategy documents
payload2='{
  "query": "marketing strategy and target demographics",
  "organization_id": "test_org_123",
  "tenant_id": "default",
  "filters": {
    "file_type": "docx",
    "tags": ["marketing", "strategy"]
  },
  "limit": 5
}'

# Payload 3: Search for product roadmap
payload3='{
  "query": "product roadmap and AI-powered analytics platform",
  "organization_id": "test_org_123",
  "tenant_id": "default",
  "filters": {
    "file_type": "pptx",
    "tags": ["product", "roadmap"]
  },
  "limit": 5
}'

# Payload 4: Search using general 2023 documents
payload4='{
  "query": "all reports and documents for 2023",
  "organization_id": "test_org_123",
  "tenant_id": "default",
  "filters": {
    "tags": ["2023"]
  },
  "limit": 5
}'

# Payload 5: Search across all document types
payload5='{
  "query": "business strategy and performance insights",
  "organization_id": "test_org_123",
  "tenant_id": "default",
  "filters": {},
  "limit": 5
}'

# Test each payload
test_payload "1 (Financial Documents)" "$payload1"
test_payload "2 (Marketing Strategy)" "$payload2"
test_payload "3 (Product Roadmap)" "$payload3"
test_payload "4 (2023 Documents)" "$payload4"
test_payload "5 (All Document Types)" "$payload5"

echo -e "${GREEN}Testing completed!${NC}"