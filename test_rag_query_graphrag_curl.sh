#!/bin/bash

# Test script for Graph RAG Contextualizer API
# This script sends sample payloads to the API endpoint using curl

# Set the API endpoint
API_URL="http://localhost:8000/api/v1/graph-rag-contextualizer"

# Set the authorization token (if needed)
AUTH_TOKEN="test_token"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Testing Graph RAG Contextualizer API...${NC}"
echo "API URL: $API_URL"
echo "----------------------------------------"

# Function to test a single payload
test_payload() {
    local description=$1
    local payload=$2
    
    echo -e "${YELLOW}Testing: $description${NC}"
    echo "Payload: $payload"
    
    # Send the request
    response=$(curl -s -X POST \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer $AUTH_TOKEN" \
        -d "$payload" \
        $API_URL)
    
    # Check if the response contains graph_insights
    if echo "$response" | grep -q "graph_insights"; then
        echo -e "${GREEN}Success! Response contains graph insights.${NC}"
        
        # Count the number of insights
        insights_count=$(echo "$response" | grep -o "citation_id" | wc -l)
        echo "Number of graph insights: $insights_count"
        
        # Show a sample of the response (first 200 characters)
        echo "Sample response:"
        echo "$response" | head -c 200
        echo "..."
    else
        echo -e "${RED}Error! Response does not contain graph insights.${NC}"
        echo "Response:"
        echo "$response"
    fi
    
    echo "----------------------------------------"
}

# Test with simple query
echo -e "${YELLOW}Test 1: Simple query about team workflows${NC}"
payload='{
    "query": "Find workflows used by the Marketing team",
    "organization_id": "test_org",
    "tenant_id": "default",
    "retrieved_docs": []
}'
test_payload "Simple query about team workflows" "$payload"

# Test with relationship query
echo -e "${YELLOW}Test 2: Query about team relationships${NC}"
payload='{
    "query": "What are the relationships between the Sales and Engineering teams?",
    "organization_id": "test_org",
    "tenant_id": "default",
    "retrieved_docs": []
}'
test_payload "Query about team relationships" "$payload"

# Test with creator query
echo -e "${YELLOW}Test 3: Query about workflow creator${NC}"
payload='{
    "query": "Who created the Customer Onboarding workflow?",
    "organization_id": "test_org",
    "tenant_id": "default",
    "retrieved_docs": []
}'
test_payload "Query about workflow creator" "$payload"

# Test with knowledge silos query
echo -e "${YELLOW}Test 4: Query about knowledge silos${NC}"
payload='{
    "query": "Find potential knowledge silos in our organization",
    "organization_id": "test_org",
    "tenant_id": "default",
    "retrieved_docs": []
}'
test_payload "Query about knowledge silos" "$payload"

# Test with complex query and retrieved documents
echo -e "${YELLOW}Test 5: Complex query with retrieved documents${NC}"
payload='{
    "query": "How are the Product and Marketing teams collaborating on the new product launch?",
    "organization_id": "test_org",
    "tenant_id": "default",
    "retrieved_docs": [
        {
            "content": "The Product team has been working on the new product launch scheduled for Q3. They have completed the feature set and are now working with Marketing on messaging.",
            "metadata": {
                "source": "meeting_notes",
                "date": "2025-09-15",
                "author": "John Smith"
            },
            "citation_id": "doc-1"
        },
        {
            "content": "Marketing team is preparing the launch campaign for the new product. They are coordinating with Product on technical specifications and key selling points.",
            "metadata": {
                "source": "email",
                "date": "2025-09-20",
                "author": "Sarah Johnson"
            },
            "citation_id": "doc-2"
        }
    ]
}'
test_payload "Complex query with retrieved documents" "$payload"

echo -e "${GREEN}All tests completed!${NC}"