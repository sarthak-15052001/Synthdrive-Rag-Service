#!/bin/bash

# Test script for the /api/v1/rag/vector-search-tenant-docs API endpoint using curl
# This script provides curl commands for testing the API with different payloads

# Set the API endpoint URL
API_URL="http://localhost:8001/api/v1/rag/vector-search-tenant-docs"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Curl commands for testing /api/v1/rag/vector-search-tenant-docs API endpoint${NC}"
echo

# Payload 1: Search for financial documents
echo -e "${GREEN}Command for Payload 1 (Financial Documents):${NC}"
echo "curl -X POST -H \"Content-Type: application/json\" -d '{
  \"query\": \"financial performance report for 2023\",
  \"organization_id\": \"test_org_123\",
  \"tenant_id\": \"default\",
  \"filters\": {
    \"file_type\": \"pdf\",
    \"tags\": [\"financial\", \"2023\"]
  },
  \"limit\": 5
}' $API_URL"
echo

# Payload 2: Search for marketing strategy documents
echo -e "${GREEN}Command for Payload 2 (Marketing Strategy):${NC}"
echo "curl -X POST -H \"Content-Type: application/json\" -d '{
  \"query\": \"marketing strategy and target demographics\",
  \"organization_id\": \"test_org_123\",
  \"tenant_id\": \"default\",
  \"filters\": {
    \"file_type\": \"docx\",
    \"tags\": [\"marketing\", \"strategy\"]
  },
  \"limit\": 5
}' $API_URL"
echo

# Payload 3: Search for product roadmap
echo -e "${GREEN}Command for Payload 3 (Product Roadmap):${NC}"
echo "curl -X POST -H \"Content-Type: application/json\" -d '{
  \"query\": \"product roadmap and AI-powered analytics platform\",
  \"organization_id\": \"test_org_123\",
  \"tenant_id\": \"default\",
  \"filters\": {
    \"file_type\": \"pptx\",
    \"tags\": [\"product\", \"roadmap\"]
  },
  \"limit\": 5
}' $API_URL"
echo

# Payload 4: Search using general 2023 documents
echo -e "${GREEN}Command for Payload 4 (2023 Documents):${NC}"
echo "curl -X POST -H \"Content-Type: application/json\" -d '{
  \"query\": \"all reports and documents for 2023\",
  \"organization_id\": \"test_org_123\",
  \"tenant_id\": \"default\",
  \"filters\": {
    \"tags\": [\"2023\"]
  },
  \"limit\": 5
}' $API_URL"
echo

# Payload 5: Search across all document types
echo -e "${GREEN}Command for Payload 5 (All Document Types):${NC}"
echo "curl -X POST -H \"Content-Type: application/json\" -d '{
  \"query\": \"business strategy and performance insights\",
  \"organization_id\": \"test_org_123\",
  \"tenant_id\": \"default\",
  \"filters\": {},
  \"limit\": 5
}' $API_URL"
echo

# Simple Payload: Basic search
echo -e "${GREEN}Command for Simple Payload (Basic Search):${NC}"
echo "curl -X POST -H \"Content-Type: application/json\" -d '{
  \"query\": \"important documents\",
  \"organization_id\": \"test_org_123\",
  \"tenant_id\": \"default\",
  \"filters\": {},
  \"limit\": 10
}' $API_URL"
echo

echo -e "${YELLOW}To execute a command, copy and paste it into your terminal.${NC}"
echo -e "${YELLOW}To save the output to a file, add ' > output.json' to the end of the command.${NC}"