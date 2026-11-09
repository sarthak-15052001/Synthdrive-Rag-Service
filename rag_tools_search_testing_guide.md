# RAG Tools Search API Testing Guide

This guide provides comprehensive instructions for testing the `/api/v1/rag/tools/search` API endpoint using both curl and Python scripts.

## Table of Contents

1. [API Overview](#api-overview)
2. [Testing with Curl](#testing-with-curl)
3. [Testing with Python](#testing-with-python)
4. [Common Test Scenarios](#common-test-scenarios)
5. [Error Handling](#error-handling)
6. [Interpreting Results](#interpreting-results)

## API Overview

The `/api/v1/rag/tools/search` API allows you to search for AI tools using natural language queries and various filters.

### Endpoint Details

- **URL**: `/api/v1/rag/tools/search`
- **Method**: POST
- **Content-Type**: application/json

### Request Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| query | string | Yes | - | Natural language query to search for AI tools |
| tenant_id | string | No | "default" | Tenant ID to filter results by |
| filters | object | No | {} | Additional filters to apply to the search |
| limit | integer | No | 5 | Maximum number of results to return (1-100) |

### Response Format

```json
{
  "query": "your search query",
  "tools": [
    {
      "name": "Tool Name",
      "description": "Tool description",
      "use_case": "Tool use case",
      "url": "https://tool-url.example.com",
      "category": "Tool Category",
      "pricing": "Pricing information",
      "reviews": "Tool reviews",
      "rating": 4.5,
      "tags": ["tag1", "tag2"],
      "tool_id": "tool-123",
      "relevance_score": 0.95,
      "citation_id": "citation-123"
    }
  ]
}
```

## Testing with Curl

We've provided an enhanced curl script (`test_rag_tools_search_enhanced.sh`) that tests various scenarios including different queries, filters, and error handling.

### Prerequisites

- Bash shell
- curl
- jq (for JSON formatting)

### Usage

```bash
# Basic usage with default settings
./test_rag_tools_search_enhanced.sh

# Specify a different base URL
./test_rag_tools_search_enhanced.sh http://api.example.com/api/v1
```

### Script Features

- Color-coded output for better readability
- Detailed request and response information
- HTTP status code reporting
- Tool count summary
- Multiple test cases covering various scenarios
- Error handling tests

### Example Output

```
Testing RAG tools search API endpoint...
Base URL: http://localhost:8000/api/v1
API URL: http://localhost:8000/api/v1/rag/tools/search

=======================================================
Test Case: Basic search for video tools
=======================================================
Request Payload:
{
  "query": "find a tool to make videos from text",
  "tenant_id": "default",
  "limit": 5
}

Sending request to http://localhost:8000/api/v1/rag/tools/search...

Response Status Code: 200
Response:
{
  "query": "find a tool to make videos from text",
  "tools": [
    {
      "name": "Synthesia",
      "description": "AI video generation platform that turns text into videos with virtual avatars",
      "url": "https://www.synthesia.io/",
      "category": "Video Creation",
      "pricing": "Free trial, then paid plans starting at $30/month",
      "rating": 4.7,
      "tags": ["video", "ai", "text-to-video"],
      "tool_id": "synthesia-01",
      "relevance_score": 0.95,
      "citation_id": "cit-001"
    },
    ...
  ]
}

Found 5 tools in the response
```

## Testing with Python

We've provided a comprehensive Python script (`test_rag_tools_search_comprehensive.py`) that offers more advanced testing capabilities.

### Prerequisites

- Python 3.6+
- Required packages: requests, colorama

### Installation

```bash
pip install requests colorama
```

### Usage

```bash
# Basic usage with default settings
python test_rag_tools_search_comprehensive.py

# Run with a specific query
python test_rag_tools_search_comprehensive.py --query "AI image generation tools"

# Run with filters
python test_rag_tools_search_comprehensive.py --query "AI tools" --category "Development" --tags "coding,programming" --rating 4.5

# Run a specific test case
python test_rag_tools_search_comprehensive.py --test-case 3

# Save results to a JSON file
python test_rag_tools_search_comprehensive.py --save-results

# Enable verbose output
python test_rag_tools_search_comprehensive.py --verbose
```

### Script Features

- Color-coded output for better readability
- Detailed request and response information
- Response time measurement
- Multiple test cases covering various scenarios
- Error handling tests
- Option to save results to a JSON file
- Verbose mode for debugging
- Command-line arguments for customization

### Example Output

```
Running test case 1: Basic search for video tools
=======================================================
Test Case: Basic search for video tools
=======================================================

Request Details:
Status Code: 200
Response Time: 0.3245 seconds
Timestamp: 2025-10-27T14:03:12.345678

Query: find a tool to make videos from text

Found 5 tools:

1. Synthesia
   Description: AI video generation platform that turns text into videos with virtual avatars
   Use Case: Creating professional-looking videos without filming
   URL: https://www.synthesia.io/
   Category: Video Creation
   Pricing: Free trial, then paid plans starting at $30/month
   Rating: 4.7
   Relevance Score: 0.95
   Tool ID: synthesia-01
   Tags: video, ai, text-to-video
   ----------------------------------------
...
```

## Common Test Scenarios

Both scripts include the following test scenarios:

1. **Basic search for video tools** - Simple query for video creation tools
2. **Search for coding tools** - Query for development and coding tools
3. **Search with category filter** - Filter results by category
4. **Search with minimum parameters** - Only provide the required query parameter
5. **Search with tags filter** - Filter results by tags
6. **Search with multiple tags filter** - Filter results by multiple tags
7. **Search with rating filter** - Filter results by minimum rating
8. **Search with combined filters** - Use multiple filters together

## Error Handling

Both scripts test the following error scenarios:

1. **Empty query** - Test with an empty query string
2. **Invalid limit** - Test with a negative limit value
3. **Very large limit** - Test with a limit value exceeding the maximum
4. **Non-existent category** - Test with a category that doesn't exist
5. **Non-default tenant** - Test with a custom tenant ID

## Interpreting Results

When analyzing the test results, pay attention to:

1. **Status codes**:
   - 200: Successful request
   - 400: Bad request (invalid parameters)
   - 401: Unauthorized
   - 404: Not found
   - 500: Server error

2. **Response time**: Look for consistent response times across different queries

3. **Tool count**: Check if the number of tools returned matches the requested limit

4. **Relevance scores**: Higher scores indicate better matches to the query

5. **Error messages**: For failed requests, check the error message for debugging

## Conclusion

These testing scripts provide a comprehensive way to test the RAG tools search API. By running these tests regularly, you can ensure the API is functioning correctly and catch any issues early.

For any questions or issues, please contact the API development team.