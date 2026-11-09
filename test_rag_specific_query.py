#!/usr/bin/env python3
"""
Simple test script to query the /api/v1/rag/learning-resources/search API endpoint
with specific queries that should match existing content.
"""

import requests
import json
import time
from datetime import datetime

# Default base URL for the API
BASE_URL = "http://localhost:8000/api/v1"

def search_learning_resources(query, tenant_id="default", filters=None, limit=5):
    """
    Search for learning resources using the API.
    
    Args:
        query: Natural language query
        tenant_id: Tenant ID (default: "default")
        filters: Optional filters to apply
        limit: Maximum number of results to return
        
    Returns:
        API response as a dictionary
    """
    # Create the request payload
    payload = {
        "query": query,
        "tenant_id": tenant_id,
        "limit": limit
    }
    
    # Add filters if provided
    if filters:
        payload["filters"] = filters
    
    # Print request details
    print(f"\nRequest URL: {BASE_URL}/rag/learning-resources/search")
    print(f"Request payload: {json.dumps(payload, indent=2)}")
    
    # Make the request
    start_time = time.time()
    try:
        response = requests.post(
            f"{BASE_URL}/rag/learning-resources/search",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        # Calculate response time
        response_time = time.time() - start_time
        
        # Try to parse the response as JSON
        try:
            result = response.json()
            # Add metadata to the result
            result["_metadata"] = {
                "status_code": response.status_code,
                "response_time": response_time,
                "timestamp": datetime.now().isoformat(),
                "request_payload": payload
            }
            
            return result
        except json.JSONDecodeError:
            error_result = {
                "error": "Invalid JSON response",
                "response_text": response.text,
                "_metadata": {
                    "status_code": response.status_code,
                    "response_time": response_time,
                    "timestamp": datetime.now().isoformat(),
                    "request_payload": payload
                }
            }
            return error_result
            
    except requests.exceptions.RequestException as e:
        error_result = {
            "error": str(e),
            "_metadata": {
                "status_code": getattr(e.response, 'status_code', None) if hasattr(e, 'response') else None,
                "response_time": time.time() - start_time,
                "timestamp": datetime.now().isoformat(),
                "request_payload": payload
            }
        }
        
        if hasattr(e, 'response') and e.response:
            error_result["status_code"] = e.response.status_code
            try:
                error_result["response_text"] = e.response.text
            except:
                error_result["response_text"] = "Could not extract response text"
        
        return error_result

def print_results(results):
    """
    Print the search results in a formatted way.
    
    Args:
        results: Search results from the API
    """
    # Print metadata if available
    if "_metadata" in results:
        metadata = results["_metadata"]
        print("\nRequest Details:")
        print(f"Status Code: {metadata.get('status_code', 'N/A')}")
        print(f"Response Time: {metadata.get('response_time', 0):.4f} seconds")
        print(f"Timestamp: {metadata.get('timestamp', 'N/A')}")
    
    # Check for errors
    if "error" in results:
        print(f"\nError: {results['error']}")
        if "response_text" in results:
            print(f"Response Text: {results['response_text']}")
        return
        
    # Print query
    print(f"\nQuery: {results.get('query', 'N/A')}")
    
    # Print resources
    resources = results.get('resources', [])
    if not resources:
        print("\nNo learning resources found.")
        return
        
    print(f"\nFound {len(resources)} learning resources:")
    
    for i, resource in enumerate(resources, 1):
        print(f"\n{i}. {resource.get('title', 'Unnamed Resource')}")
        print(f"   Content: {resource.get('content', 'No content')[:100]}...")
        if resource.get('url'):
            print(f"   URL: {resource.get('url')}")
        if resource.get('author'):
            print(f"   Author: {resource.get('author')}")
        if resource.get('resource_type'):
            print(f"   Type: {resource.get('resource_type')}")
        if resource.get('tags'):
            print(f"   Tags: {', '.join(resource.get('tags', []))}")
        print(f"   Relevance Score: {resource.get('relevance_score', 'N/A')}")
        print(f"   Resource ID: {resource.get('resource_id', 'N/A')}")
        print(f"   {'-' * 40}")

def main():
    """Run specific queries that should match existing content."""
    # List of specific queries to try
    queries = [
        "RAG",
        "Retrieval-Augmented Generation",
        "Introduction to RAG Systems",
        "Knowledge Retrieval",
        "AI Research Team"
    ]
    
    # Try each query
    for query in queries:
        print(f"\n{'=' * 60}")
        print(f"Testing query: {query}")
        print(f"{'=' * 60}")
        
        # Try with no filters
        results = search_learning_resources(query=query)
        print_results(results)
        
        # Try with resource_type filter
        results = search_learning_resources(
            query=query,
            filters={"resource_type": "Tutorial"}
        )
        print_results(results)
        
        # Try with tags filter
        results = search_learning_resources(
            query=query,
            filters={"tags": ["RAG", "LLM"]}
        )
        print_results(results)

if __name__ == "__main__":
    main()