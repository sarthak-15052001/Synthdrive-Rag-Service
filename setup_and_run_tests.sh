#!/bin/bash
# Script to set up and run the conditional edge router API tests

# Set colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}Setting up and running tests for the Conditional Edge Router API...${NC}"

# Make the test scripts executable
echo -e "${BLUE}Making test scripts executable...${NC}"
chmod +x test_conditional_edge_router_curl.sh
chmod +x test_conditional_edge_router_python_enhanced.py

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Python 3 is not installed. Please install Python 3 and try again.${NC}"
    exit 1
fi

# Check if pip is installed
if ! command -v pip &> /dev/null && ! command -v pip3 &> /dev/null; then
    echo -e "${RED}pip is not installed. Please install pip and try again.${NC}"
    exit 1
fi

# Determine which pip command to use
PIP_CMD="pip"
if ! command -v pip &> /dev/null; then
    PIP_CMD="pip3"
fi

# Install required Python packages
echo -e "${BLUE}Installing required Python packages...${NC}"
$PIP_CMD install requests colorama httpx fastapi

# Run the curl tests
echo -e "\n${BLUE}Running curl tests...${NC}"
./test_conditional_edge_router_curl.sh

# Run the Python tests
echo -e "\n${BLUE}Running Python tests...${NC}"
python test_conditional_edge_router_python_enhanced.py --save-results

echo -e "\n${GREEN}All tests completed!${NC}"
echo -e "${GREEN}Test results have been saved to conditional_edge_router_test_results.md${NC}"
echo -e "${BLUE}Please check the test results to verify the API behavior.${NC}"