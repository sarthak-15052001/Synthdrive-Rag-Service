# RAG Tools Search API Testing Examples

This document provides examples of how to test the `/api/v1/rag/tools/search` API endpoint using both curl and Python.

## API Endpoint Details

- **URL**: `/api/v1/rag/tools/search`
- **Method**: POST
- **Content-Type**: application/json

## Request Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| query | string | Yes | - | Natural language query to search for AI tools |
| tenant_id | string | No | "default" | Tenant ID to filter results by |
| filters | object | No | {} | Additional filters to apply to the search |
| limit | integer | No | 5 | Maximum number of results to return (1-100) |

## Response Format

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

## Testing with curl

### Basic Search

```bash
curl -X POST "http://localhost:8001/api/v1/tools/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "find a tool to make videos from text",
    "tenant_id": "default",
    "limit": 5
  }'
```

### Search with Category Filter

```bash
curl -X POST "http://localhost:8001/api/v1/tools/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "AI tools",
    "tenant_id": "default",
    "filters": {
      "category": "Development"
    },
    "limit": 5
  }'
```

### Search with Tags Filter

```bash
curl -X POST "http://localhost:8001/api/v1/tools/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "content creation tools",
    "tenant_id": "default",
    "filters": {
      "tags": ["video"]
    },
    "limit": 5
  }'
```

### Search with Rating Filter

```bash
curl -X POST "http://localhost:8000/api/v1/rag/tools/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "high quality AI tools",
    "tenant_id": "default",
    "filters": {
      "rating": 4.5
    },
    "limit": 5
  }'
```

### Minimal Request

```bash
curl -X POST "http://localhost:8000/api/v1/rag/tools/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "data visualization"
  }'
```

## Testing with Python

### Basic Usage

```python
import requests
import json

def search_ai_tools(query, tenant_id="default", filters=None, limit=5):
    """Search for AI tools using the API."""
    url = "http://localhost:8000/api/v1/rag/tools/search"
    
    # Create the request payload
    payload = {
        "query": query,
        "tenant_id": tenant_id,
        "limit": limit
    }
    
    # Add filters if provided
    if filters:
        payload["filters"] = filters
        
    # Make the request
    response = requests.post(
        url,
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    
    # Check if the request was successful
    response.raise_for_status()
    
    # Return the response as a dictionary
    return response.json()

# Example usage
results = search_ai_tools("find a tool to make videos from text")
print(f"Found {len(results.get('tools', []))} tools")
for tool in results.get('tools', []):
    print(f"- {tool.get('name')}: {tool.get('description')}")
```

### Using the Test Script

The provided `test_rag_tools_search.py` script can be used to test the API with various parameters:

```bash
# Run all test cases
./test_rag_tools_search.py

# Test with a specific query
./test_rag_tools_search.py --query "AI image generation tools"

# Test with a specific query and category filter
./test_rag_tools_search.py --query "AI tools" --category "Development"

# Test with a custom base URL
./test_rag_tools_search.py --base-url "http://api.example.com/api/v1"

# Test with a specific limit
./test_rag_tools_search.py --query "data visualization" --limit 10
```

## Common Filter Examples

Here are some common filter combinations you might want to use:

### Category Filters

```json
{
  "filters": {
    "category": "Video Creation"
  }
}
```

### Tag Filters

```json
{
  "filters": {
    "tags": ["video", "marketing"]
  }
}
```

### Combined Filters

```json
{
  "filters": {
    "category": "Development",
    "tags": ["coding", "programming"]
  }
}
```

### Tenant-specific Filters

```json
{
  "tenant_id": "enterprise-customer-123",
  "filters": {
    "category": "Data Analysis"
  }
}
```

## Error Handling

The API may return various error responses:

- 400 Bad Request: Invalid request parameters
- 401 Unauthorized: Authentication failure
- 404 Not Found: Resource not found
- 500 Internal Server Error: Server-side error

Always check the response status code and handle errors appropriately in your application.