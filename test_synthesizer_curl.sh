#!/bin/bash

# Test script for the Synthesizer API using curl
# This script demonstrates how to call the Synthesizer API with different payloads

# Server URL
BASE_URL="http://localhost:8000"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Testing Synthesizer API with curl ===${NC}"

# Function to test the Synthesizer API with a payload
test_synthesizer() {
    local payload_name=$1
    local payload_file=$2
    
    echo -e "\n${BLUE}=== Testing with payload: ${payload_name} ===${NC}"
    
    # Send the request
    response=$(curl -s -X POST \
        -H "Content-Type: application/json" \
        -d @"$payload_file" \
        "${BASE_URL}/api/v1/rag/synthesizer")
    
    # Check if the request was successful
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}Request successful!${NC}"
        
        # Display the raw response
        echo -e "\n${BLUE}Response:${NC}"
        echo "$response"
    else
        echo -e "${RED}Request failed!${NC}"
        echo "$response"
    fi
}

# Create temporary payload files for each test

# Example 1: AI Video Tools
cat > /tmp/payload_video_tools.json << 'EOF'
{
  "query": "What AI tools are available for video generation?",
  "organization_id": "test-org-123",
  "tenant_id": "default",
  "retrieved_docs": [
    {
      "content": "Runway is an AI video generation tool that allows users to create videos from text prompts. It offers features like text-to-video, image-to-video, and video editing capabilities.",
      "metadata": {"type": "ai_tool"},
      "source": "global_tools_database",
      "citation_id": "doc-1"
    },
    {
      "content": "Synthesia is a platform that enables users to create AI-generated videos with virtual presenters. Users can input text, and the platform will generate a video with a virtual human presenting the content.",
      "metadata": {"type": "ai_tool"},
      "source": "global_tools_database",
      "citation_id": "doc-2"
    }
  ],
  "graph_insights": [
    {
      "content": "The marketing team has been using Runway for their recent video campaigns.",
      "metadata": {"type": "graph_relationship"},
      "source": "graph_database",
      "citation_id": "graph-rel-1",
      "explanation": "This insight shows that the marketing team has practical experience with Runway.",
      "inferred_context": "The marketing team might have valuable feedback on Runway's effectiveness for promotional content."
    }
  ]
}
EOF

# Example 2: Data Analysis Tools (shorter version)
cat > /tmp/payload_data_tools.json << 'EOF'
{
  "query": "What are the best tools for data analysis?",
  "organization_id": "test-org-456",
  "tenant_id": "default",
  "retrieved_docs": [
    {
      "content": "Tableau is a powerful data visualization tool that helps users create interactive dashboards and reports.",
      "metadata": {"type": "ai_tool"},
      "source": "global_tools_database",
      "citation_id": "doc-1"
    },
    {
      "content": "Python with libraries like Pandas and NumPy offers powerful data analysis capabilities for data scientists.",
      "metadata": {"type": "ai_tool"},
      "source": "global_tools_database",
      "citation_id": "doc-2"
    }
  ],
  "graph_insights": []
}
EOF

# Run the tests
echo -e "\n${BLUE}Running tests...${NC}"
test_synthesizer "AI Video Tools" "/tmp/payload_video_tools.json"
test_synthesizer "Data Analysis Tools" "/tmp/payload_data_tools.json"

# Clean up
rm /tmp/payload_video_tools.json
rm /tmp/payload_data_tools.json

echo -e "\n${BLUE}=== All tests completed ===${NC}"