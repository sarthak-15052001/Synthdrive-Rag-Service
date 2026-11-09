#!/bin/bash
# Test script for the Conditional Edge Router API using curl
# This script tests different scenarios for the conditional-edge-router endpoint

# Set the base URL
BASE_URL="http://localhost:8000"

# Set the API endpoint
ENDPOINT="/api/v1/rag/conditional-edge-router"

# Set the headers
HEADERS="Content-Type: application/json"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}Testing Conditional Edge Router API...${NC}"

# Function to make API calls and display results
test_scenario() {
    local scenario=$1
    local payload=$2
    
    echo -e "\n${BLUE}Test Case: $scenario${NC}"
    echo "Request Payload:"
    echo "$payload" | python3 -m json.tool 2>/dev/null || echo "$payload"
    
    response=$(curl -s -X POST \
        -H "$HEADERS" \
        -d "$payload" \
        "$BASE_URL$ENDPOINT")
    
    status=$?
    
    if [ $status -eq 0 ]; then
        echo -e "${GREEN}Response:${NC}"
        echo "$response" | python3 -m json.tool 2>/dev/null || echo "$response"
        
        # Extract key information using grep and sed instead of jq
        next_node=$(echo "$response" | grep -o '"next_node"[^,}]*' | sed 's/"next_node"://;s/"//g;s/^ *//')
        reason=$(echo "$response" | grep -o '"reason"[^,}]*' | sed 's/"reason"://;s/"//g;s/^ *//')
        
        echo -e "${GREEN}Next Node:${NC} $next_node"
        echo -e "${GREEN}Reason:${NC} $reason"
    else
        echo -e "${RED}Error: Failed to connect to the API${NC}"
    fi
}

# Test Case 1: Empty state (should route to planner)
echo -e "\n${BLUE}========== Test Case 1: Empty state (should route to planner) ==========${NC}"
payload1='{
    "original_query": "What AI tools are available for video generation?",
    "organization_id": "test_org",
    "tenant_id": "test_tenant",
    "plan": null,
    "retrieved_docs": [],
    "graph_insights": [],
    "final_answer": null,
    "error_log": []
}'

test_scenario "Empty state (should route to planner)" "$payload1"

# Test Case 2: State with plan but no retrieved docs (should continue retrieval)
echo -e "\n${BLUE}========== Test Case 2: State with plan but no retrieved docs ==========${NC}"
payload2='{
    "original_query": "What AI tools are available for video generation?",
    "organization_id": "test_org",
    "tenant_id": "test_tenant",
    "plan": "First search for AI tools in Weaviate, then query Neo4j for relationships between the found tools.",
    "retrieved_docs": [],
    "graph_insights": [],
    "final_answer": null,
    "error_log": []
}'

test_scenario "State with plan but no retrieved docs" "$payload2"

# Test Case 3: State with plan and retrieved docs (should proceed to synthesis)
echo -e "\n${BLUE}========== Test Case 3: State with plan and retrieved docs ==========${NC}"
payload3='{
    "original_query": "What AI tools are available for video generation?",
    "organization_id": "test_org",
    "tenant_id": "test_tenant",
    "plan": "First search for AI tools in Weaviate, then query Neo4j for relationships between the found tools.",
    "retrieved_docs": [
        {
            "content": "Runway ML is an AI tool for video generation. It allows users to create videos from text prompts.",
            "source": "weaviate",
            "citation_id": "doc-1"
        },
        {
            "content": "Synthesia is an AI video generation platform that creates videos with virtual avatars.",
            "source": "weaviate",
            "citation_id": "doc-2"
        },
        {
            "content": "Descript offers AI-powered video editing tools including text-based editing and overdub features.",
            "source": "weaviate",
            "citation_id": "doc-3"
        }
    ],
    "graph_insights": [
        {
            "content": "Runway ML and Synthesia are both used in the creative industry for video production.",
            "source": "graph_database",
            "citation_id": "graph-1"
        }
    ],
    "final_answer": null,
    "error_log": []
}'

test_scenario "State with plan and retrieved docs" "$payload3"

# Test Case 4: State with error (should route to error handling)
echo -e "\n${BLUE}========== Test Case 4: State with error ==========${NC}"
payload4='{
    "original_query": "What AI tools are available for video generation?",
    "organization_id": "test_org",
    "tenant_id": "test_tenant",
    "plan": "First search for AI tools in Weaviate, then query Neo4j for relationships between the found tools.",
    "retrieved_docs": [],
    "graph_insights": [],
    "final_answer": null,
    "error_log": ["Error connecting to Weaviate: Connection refused"]
}'

test_scenario "State with error" "$payload4"

echo -e "\n${GREEN}Testing completed!${NC}"