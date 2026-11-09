#!/bin/bash
# Test script for the /api/v1/rag/learning-resources/search API endpoint using curl

# Set default values
BASE_URL="http://localhost:8000/api/v1"
ENDPOINT="rag/learning-resources/search"
TENANT_ID="default"
LIMIT=5

# Text colors for better readability
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to display usage information
usage() {
  echo -e "${BLUE}Usage:${NC} $0 [options]"
  echo -e "${BLUE}Options:${NC}"
  echo "  -u, --url URL       Base URL for the API (default: http://localhost:8000/api/v1)"
  echo "  -q, --query QUERY   Search query (required)"
  echo "  -t, --tenant TENANT Tenant ID (default: default)"
  echo "  -l, --limit LIMIT   Maximum number of results to return (default: 5)"
  echo "  -f, --filter TYPE:VALUE  Add a filter (can be used multiple times)"
  echo "  -h, --help          Display this help message"
  echo "  -r, --run-tests     Run predefined test cases"
  exit 1
}

# Function to run a single test
run_test() {
  local query="$1"
  local tenant_id="$2"
  local limit="$3"
  local filters=("${@:4}")
  
  echo -e "\n${BLUE}=====================================${NC}"
  echo -e "${GREEN}Running test with query:${NC} $query"
  echo -e "${BLUE}=====================================${NC}"
  
  # Build the filter JSON if filters are provided
  FILTER_JSON=""
  if [ ${#filters[@]} -gt 0 ]; then
    FILTER_JSON='"filters": {'
    
    for i in "${!filters[@]}"; do
      IFS=':' read -r key value <<< "${filters[$i]}"
      
      # Handle different filter types
      if [[ "$key" == "tags" ]]; then
        # Tags should be an array
        FILTER_JSON+="\"$key\": [\"$value\"]"
      elif [[ "$value" =~ ^[0-9]+(\.[0-9]+)?$ ]]; then
        # Numeric values should not have quotes
        FILTER_JSON+="\"$key\": $value"
      else
        # String values should have quotes
        FILTER_JSON+="\"$key\": \"$value\""
      fi
      
      # Add comma if not the last filter
      if [ $i -lt $((${#filters[@]} - 1)) ]; then
        FILTER_JSON+=", "
      fi
    done
    
    FILTER_JSON+='}, '
  fi
  
  # Build the full request payload
  PAYLOAD="{
    \"query\": \"$query\",
    \"tenant_id\": \"$tenant_id\",
    ${FILTER_JSON}\"limit\": $limit
  }"
  
  # Display request information
  echo -e "${BLUE}Request URL:${NC} ${BASE_URL}/${ENDPOINT}"
  echo -e "${BLUE}Request payload:${NC}"
  echo "$PAYLOAD" | jq '.' 2>/dev/null || echo "$PAYLOAD"
  
  # Make the request
  echo -e "\n${YELLOW}Sending request...${NC}"
  RESPONSE=$(curl -s -X POST "${BASE_URL}/${ENDPOINT}" \
    -H "Content-Type: application/json" \
    -d "$PAYLOAD")
  
  # Check if the response is valid JSON
  if jq -e . >/dev/null 2>&1 <<<"$RESPONSE"; then
    # Display the response
    echo -e "\n${GREEN}Response:${NC}"
    echo "$RESPONSE" | jq '.'
    
    # Extract and display the number of resources found
    RESOURCES_COUNT=$(echo "$RESPONSE" | jq '.resources | length')
    echo -e "\n${GREEN}Found ${RESOURCES_COUNT} learning resources${NC}"
    
    # Display each resource
    if [ "$RESOURCES_COUNT" -gt 0 ]; then
      echo -e "\n${BLUE}Learning Resources:${NC}"
      for i in $(seq 0 $(($RESOURCES_COUNT - 1))); do
        TITLE=$(echo "$RESPONSE" | jq -r ".resources[$i].title")
        RESOURCE_TYPE=$(echo "$RESPONSE" | jq -r ".resources[$i].resource_type // \"N/A\"")
        URL=$(echo "$RESPONSE" | jq -r ".resources[$i].url // \"N/A\"")
        SCORE=$(echo "$RESPONSE" | jq -r ".resources[$i].relevance_score")
        
        echo -e "${YELLOW}Resource $((i+1)):${NC}"
        echo -e "  ${BLUE}Title:${NC} $TITLE"
        echo -e "  ${BLUE}Type:${NC} $RESOURCE_TYPE"
        echo -e "  ${BLUE}URL:${NC} $URL"
        echo -e "  ${BLUE}Relevance Score:${NC} $SCORE"
        echo ""
      done
    fi
  else
    # Display error
    echo -e "\n${RED}Error: Invalid response${NC}"
    echo "$RESPONSE"
  fi
}

# Function to run predefined test cases
run_test_cases() {
  echo -e "\n${BLUE}Running predefined test cases...${NC}"
  
  # Test Case 1: Basic search
  run_test "machine learning tutorials" "default" 5
  
  # Test Case 2: Search with resource_type filter
  run_test "AI tutorials" "default" 5 "resource_type:tutorial"
  
  # Test Case 3: Search with tags filter
  run_test "python programming" "default" 5 "tags:python"
  
  # Test Case 4: Search with multiple tags filter
  run_test "data science" "default" 5 "tags:python" "tags:data-science"
  
  # Test Case 5: Search with combined filters
  run_test "machine learning for beginners" "default" 5 "resource_type:tutorial" "tags:beginner" "tags:machine-learning"
  
  # Test Case 6: Search with higher limit
  run_test "AI resources" "default" 10
  
  echo -e "\n${GREEN}All test cases completed.${NC}"
}

# Parse command line arguments
FILTERS=()
RUN_TESTS=false

while [[ $# -gt 0 ]]; do
  key="$1"
  case $key in
    -u|--url)
      BASE_URL="$2"
      shift 2
      ;;
    -q|--query)
      QUERY="$2"
      shift 2
      ;;
    -t|--tenant)
      TENANT_ID="$2"
      shift 2
      ;;
    -l|--limit)
      LIMIT="$2"
      shift 2
      ;;
    -f|--filter)
      FILTERS+=("$2")
      shift 2
      ;;
    -r|--run-tests)
      RUN_TESTS=true
      shift
      ;;
    -h|--help)
      usage
      ;;
    *)
      echo -e "${RED}Unknown option:${NC} $1"
      usage
      ;;
  esac
done

# Run predefined test cases if requested
if [ "$RUN_TESTS" = true ]; then
  run_test_cases
  exit 0
fi

# Check if query is provided when not running test cases
if [ -z "$QUERY" ] && [ "$RUN_TESTS" = false ]; then
  echo -e "${RED}Error:${NC} Query parameter is required when not running test cases"
  usage
fi

# Run a single test with the provided parameters if not running test cases
if [ "$RUN_TESTS" = false ]; then
  run_test "$QUERY" "$TENANT_ID" "$LIMIT" "${FILTERS[@]}"
fi

# Examples section
echo -e "\n${BLUE}Example usage:${NC}"
echo -e "${GREEN}Basic search:${NC}"
echo "  $0 -q \"machine learning tutorials\""
echo -e "${GREEN}Search with filters:${NC}"
echo "  $0 -q \"deep learning\" -f resource_type:tutorial -f tags:python"
echo -e "${GREEN}Search with custom limit:${NC}"
echo "  $0 -q \"NLP examples\" -l 10"
echo -e "${GREEN}Run all predefined test cases:${NC}"
echo "  $0 -r"