# Conditional Edge Router API Testing

This directory contains scripts and documentation for testing the Conditional Edge Router API endpoint (`/api/v1/rag/conditional-edge-router`).

## Overview

The Conditional Edge Router is a component of the RAG (Retrieval-Augmented Generation) system that determines the next node to route to based on the current state of the query processing. It makes decisions based on:

- Whether a plan exists
- Whether documents have been retrieved
- Whether there are any errors

## Test Files

- `test_conditional_edge_router_curl.sh`: Bash script using curl to test the API
- `test_conditional_edge_router_python_enhanced.py`: Python script with enhanced output formatting
- `setup_and_run_tests.sh`: Helper script to set up and run all tests
- `conditional_edge_router_test_results.md`: Documentation of test scenarios and results

## Test Scenarios

The tests cover the following scenarios:

1. **Empty state** - No plan, no retrieved docs, no errors
2. **State with plan but no retrieved docs** - Has a plan but no documents retrieved yet
3. **State with plan and retrieved docs** - Has a plan and documents retrieved
4. **State with error** - Has an error in the error_log
5. **Custom query with different organization and tenant** - Using different organization and tenant IDs

## Running the Tests

### Prerequisites

- Python 3.6+
- pip (Python package manager)
- curl

### Option 1: Using the setup script

The easiest way to run all tests is to use the setup script:

```bash
# Make the script executable
chmod +x setup_and_run_tests.sh

# Run the script
./setup_and_run_tests.sh
```

This will:
1. Make all test scripts executable
2. Install required Python packages
3. Run the curl tests
4. Run the Python tests
5. Save the results to `conditional_edge_router_test_results.md`

### Option 2: Running tests individually

#### Curl Tests

```bash
# Make the script executable
chmod +x test_conditional_edge_router_curl.sh

# Run the tests
./test_conditional_edge_router_curl.sh
```

#### Python Tests

```bash
# Install required packages
pip install requests colorama httpx fastapi

# Make the script executable
chmod +x test_conditional_edge_router_python_enhanced.py

# Run the tests
python test_conditional_edge_router_python_enhanced.py --save-results
```

## Customizing the Tests

### Changing the API URL

By default, the tests use `http://localhost:8000` as the base URL. You can change this:

- For curl tests: Edit the `BASE_URL` variable in `test_conditional_edge_router_curl.sh`
- For Python tests: Use the `--base-url` command-line argument:
  ```bash
  python test_conditional_edge_router_python_enhanced.py --base-url "http://your-api-url"
  ```

### Adding Authentication

If your API requires authentication:

- For curl tests: Uncomment and modify the `Authorization` header in `test_conditional_edge_router_curl.sh`
- For Python tests: Modify the `DEFAULT_HEADERS` dictionary in `test_conditional_edge_router_python_enhanced.py`

## Test Results

After running the tests, check `conditional_edge_router_test_results.md` for detailed results and analysis.

## Troubleshooting

- If you encounter connection errors, make sure the API server is running and accessible
- If you get authentication errors, check that you've provided the correct authentication credentials
- If the API returns unexpected responses, verify that the API endpoint is correctly implemented