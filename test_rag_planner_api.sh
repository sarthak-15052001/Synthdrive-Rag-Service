#!/bin/bash

# Test script for the RAG Planner API
# This script tests the planner API with various sample queries

# Set environment variables
API_BASE_URL=${API_BASE_URL:-"http://localhost:8000"}
API_KEY=${API_KEY:-"test-api-key"}
PLANNER_ENDPOINT="${API_BASE_URL}/api/v1/planner"
OUTPUT_FILE="planner_test_results.json"

# Clear previous test results
echo "# RAG Planner API Test Results" > $OUTPUT_FILE

# Function to test a specific query type
test_query() {
    local query_type=$1
    local payload_file="rag_planner_sample_payloads.json"
    
    echo "=== Testing planner API with $query_type query ==="
    
    # Extract the payload for this query type
    payload=$(jq -c ".$query_type" $payload_file)
    
    # Make the API request
    echo "Request payload: $payload"
    response=$(curl -s -X POST \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer $API_KEY" \
        -d "$payload" \
        $PLANNER_ENDPOINT)
    
    # Save the response to the output file
    echo -e "\n\n--- $query_type Query ---" >> $OUTPUT_FILE
    echo "$response" | jq '.' >> $OUTPUT_FILE
    
    # Display key information from the response
    echo "Response:"
    echo "Original Query: $(echo $response | jq -r '.original_query // "N/A"')"
    echo "Plan: $(echo $response | jq -r '.plan // "No plan generated"')"
    
    # Check if collections_to_search is present and not empty
    collections=$(echo $response | jq -r '.collections_to_search | join(", ") // "None"')
    echo "Collections to search: $collections"
    
    # Check if retrieved_docs is present and not empty
    doc_count=$(echo $response | jq -r '.retrieved_docs | length // 0')
    echo "Retrieved documents: $doc_count"
    
    # Check if graph_insights is present and not empty
    insight_count=$(echo $response | jq -r '.graph_insights | length // 0')
    echo "Graph insights: $insight_count"
    
    # Check if final_answer is present
    final_answer=$(echo $response | jq -r '.final_answer // "No final answer generated"')
    if [ "$final_answer" != "null" ] && [ "$final_answer" != "No final answer generated" ]; then
        echo "Final answer: [Generated]"
    else
        echo "Final answer: None"
    fi
    
    echo ""
}

# Test each query type
echo "=== Starting RAG Planner API Tests ==="
echo "API Base URL: $API_BASE_URL"
echo "Using test payloads from rag_planner_sample_payloads.json"
echo ""

# Test AI tools query
test_query "ai_tools_query"

# Test ecosystem partners query
test_query "ecosystem_partners_query"

# Test learning resources query
test_query "learning_resources_query"

# Test tenant files query
test_query "tenant_files_query"

# Test complex query
test_query "complex_query"

# Test relationship query
test_query "relationship_query"

# Test multi-collection query
test_query "multi_collection_query"

# Test specific tool query
test_query "specific_tool_query"

# Test specific partner query
test_query "specific_partner_query"

# Test specific document query
test_query "specific_document_query"

echo "=== RAG Planner API Tests Completed ==="
echo "Results saved to $OUTPUT_FILE"