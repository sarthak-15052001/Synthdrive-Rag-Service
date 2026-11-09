#!/usr/bin/env python3
"""
Simple test script for the /api/v1/rag/learning-resources/search API endpoint.

This script provides a straightforward way to test the RAG learning resources search API
with various queries and filter combinations.

Usage:
    python test_rag_learning_resources_search_simple.py
"""

import requests
import json
import time
from datetime import datetime
import argparse
import sys

# Default base URL for the API
DEFAULT_BASE_URL = "http://localhost:8000/api/v1"

def search_learning_resources(query, tenant_id="default", filters=None, limit=5, base_url=DEFAULT_BASE_URL):
    """
    Search for learning resources using the API.
    
    Args:
        query: Natural language query
        tenant_id: Tenant ID (default: "default")
        filters: Optional filters to apply
        limit: Maximum number of results to return
        base_url: Base URL for the API
        
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
    print(f"\nRequest URL: {base_url}/rag/learning-resources/search")
    print(f"Request payload: {json.dumps(payload, indent=2)}")
    
    # Make the request
    start_time = time.time()
    try:
        response = requests.post(
            f"{base_url}/rag/learning-resources/search",
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

def run_test_cases(base_url=DEFAULT_BASE_URL):
    """Run a series of test cases to demonstrate the API."""
    test_cases = [
        {
            "name": "Basic search for machine learning resources",
            "query": "machine learning tutorials",
            "tenant_id": "default",
            "filters": None,
            "limit": 5
        },
        {
            "name": "Search with resource_type filter",
            "query": "AI tutorials",
            "tenant_id": "default",
            "filters": {"resource_type": "tutorial"},
            "limit": 5
        },
        {
            "name": "Search with tags filter",
            "query": "python programming",
            "tenant_id": "default",
            "filters": {"tags": ["python"]},
            "limit": 5
        },
        {
            "name": "Search with multiple tags filter",
            "query": "data science",
            "tenant_id": "default",
            "filters": {"tags": ["python", "data-science"]},
            "limit": 5
        },
        {
            "name": "Search with combined filters",
            "query": "machine learning for beginners",
            "tenant_id": "default",
            "filters": {
                "resource_type": "tutorial",
                "tags": ["beginner", "machine-learning"]
            },
            "limit": 5
        },
        {
            "name": "Search with higher limit",
            "query": "AI resources",
            "tenant_id": "default",
            "filters": None,
            "limit": 10
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'=' * 60}")
        print(f"Test Case {i}: {test_case['name']}")
        print(f"{'=' * 60}")
        
        results = search_learning_resources(
            query=test_case["query"],
            tenant_id=test_case["tenant_id"],
            filters=test_case["filters"],
            limit=test_case["limit"],
            base_url=base_url
        )
        
        print_results(results)
        
    print(f"\n{'=' * 60}")
    print("All test cases completed.")
    print(f"{'=' * 60}")

def main():
    """Main function to run the tests."""
    parser = argparse.ArgumentParser(description="Test the RAG learning resources search API endpoint.")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL, help="Base URL for the API")
    parser.add_argument("--query", help="Specific query to test (optional)")
    parser.add_argument("--tenant-id", default="default", help="Tenant ID to use")
    parser.add_argument("--limit", type=int, default=5, help="Maximum number of results to return")
    parser.add_argument("--resource-type", help="Filter by resource type (optional)")
    parser.add_argument("--tags", help="Filter by tags, comma-separated (optional)")
    
    args = parser.parse_args()
    
    # If a specific query is provided, run just that query
    if args.query:
        filters = {}
        if args.resource_type:
            filters["resource_type"] = args.resource_type
        if args.tags:
            filters["tags"] = args.tags.split(",")
            
        print(f"\nRunning single query: {args.query}")
        results = search_learning_resources(
            query=args.query,
            tenant_id=args.tenant_id,
            filters=filters if filters else None,
            limit=args.limit,
            base_url=args.base_url
        )
        
        print_results(results)
    else:
        # Run all test cases
        run_test_cases(base_url=args.base_url)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nTest interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\nAn error occurred: {str(e)}")
        import traceback
        print(traceback.format_exc())
        sys.exit(1)