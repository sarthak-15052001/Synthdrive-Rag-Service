#!/usr/bin/env python3
"""
Simplified script to test the Weaviate client directly for learning resources search.
"""

import json
import time
import sys
from src.data_stores.weaviate_client import WeaviateClient

# Initialize the Weaviate client
weaviate_client = WeaviateClient()

def test_direct_weaviate(query, filters=None, limit=5):
    """Test the Weaviate client directly"""
    print(f"\n=== Testing Direct Weaviate Client ===")
    print(f"Query: {query}")
    print(f"Filters: {filters}")
    print(f"Limit: {limit}")
    
    # Call the search_learning_resources method directly
    start_time = time.time()
    results = weaviate_client.search_learning_resources(
        query=query,
        filters=filters or {},
        limit=limit
    )
    response_time = time.time() - start_time
    
    print(f"Response Time: {response_time:.4f} seconds")
    print(f"Found {len(results)} learning resources")
    
    return results

def main():
    """Main function to test different queries and filters."""
    # Test cases
    test_cases = [
        {
            "name": "Basic search for RAG",
            "query": "RAG",
            "filters": {},
            "limit": 5
        },
        {
            "name": "Search with resource_type filter",
            "query": "RAG",
            "filters": {"resource_type": "Tutorial"},
            "limit": 5
        },
        {
            "name": "Search with tags filter",
            "query": "RAG",
            "filters": {"tags": ["LLM"]},
            "limit": 5
        },
        {
            "name": "Search with multiple tags filter",
            "query": "RAG",
            "filters": {"tags": ["LLM", "AI"]},
            "limit": 5
        },
        {
            "name": "Search with combined filters",
            "query": "RAG",
            "filters": {
                "resource_type": "Tutorial",
                "tags": ["LLM"]
            },
            "limit": 5
        },
        {
            "name": "Search with higher limit",
            "query": "RAG",
            "filters": {},
            "limit": 10
        }
    ]
    
    # Run each test case
    for test_case in test_cases:
        print(f"\n{'=' * 60}")
        print(f"Test Case: {test_case['name']}")
        print(f"{'=' * 60}")
        
        # Run the test
        results = test_direct_weaviate(
            test_case["query"],
            test_case["filters"],
            test_case["limit"]
        )
        
        # Print the results
        print("\nResults:")
        for i, resource in enumerate(results, 1):
            print(f"{i}. {resource.get('title', 'Unnamed Resource')}")
            print(f"   Type: {resource.get('resource_type', 'N/A')}")
            if resource.get('tags'):
                print(f"   Tags: {', '.join(resource.get('tags', []))}")
            print(f"   Relevance Score: {resource.get('relevance_score', 'N/A')}")
    
    print("\nBased on our testing, we've identified the following issues:")
    print("1. The API endpoint is not returning results even though the Weaviate client has data")
    print("2. This could be due to a filter issue or a problem in the API implementation")
    print("\nPotential fixes:")
    print("1. Check if the tenant_id filter is being applied correctly")
    print("2. Ensure that the filters are being properly passed to the Weaviate client")
    print("3. Verify that the response mapping is correct")
    print("4. Add more logging to the API endpoint to identify where the issue occurs")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        print(traceback.format_exc())
        sys.exit(1)