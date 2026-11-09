#!/usr/bin/env python3
"""
Direct test of Weaviate client's search_learning_resources function.
"""

import sys
import json
from src.data_stores.weaviate_client import WeaviateClient

def main():
    # Initialize the Weaviate client
    weaviate_client = WeaviateClient()
    
    # Test query
    query = "RAG"
    
    print(f"Searching for learning resources with query: {query}")
    
    # Call the search_learning_resources method directly
    results = weaviate_client.search_learning_resources(
        query=query,
        filters={},
        limit=5
    )
    
    # Print the results
    print(f"\nFound {len(results)} learning resources:")
    print(json.dumps(results, indent=2))
    
    # Print each resource in a readable format
    for i, resource in enumerate(results, 1):
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

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        print(traceback.format_exc())
        sys.exit(1)