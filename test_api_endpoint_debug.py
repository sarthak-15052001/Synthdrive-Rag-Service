#!/usr/bin/env python3
"""
Debug script for the /api/v1/rag/learning-resources/search API endpoint.
This script tests both the direct Weaviate client and the API endpoint to compare results.
"""

import requests
import json
import time
from datetime import datetime
import sys
from src.data_stores.weaviate_client import WeaviateClient

# Default base URL for the API
DEFAULT_BASE_URL = "http://localhost:8000/api/v1"

def test_direct_weaviate(query, filters=None, limit=5):
    """Test the Weaviate client directly"""
    print(f"\n=== Testing Direct Weaviate Client ===")
    print(f"Query: {query}")
    print(f"Filters: {filters}")
    print(f"Limit: {limit}")
    
    # Initialize the Weaviate client
    weaviate_client = WeaviateClient()
    
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

def test_api_endpoint(query, tenant_id="default", filters=None, limit=5, base_url=DEFAULT_BASE_URL):
    """Test the API endpoint"""
    print(f"\n=== Testing API Endpoint ===")
    print(f"Query: {query}")
    print(f"Tenant ID: {tenant_id}")
    print(f"Filters: {filters}")
    print(f"Limit: {limit}")
    
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
    print(f"Request URL: {base_url}/rag/learning-resources/search")
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
        print(f"Response Time: {response_time:.4f} seconds")
        print(f"Status Code: {response.status_code}")
        
        # Try to parse the response as JSON
        try:
            result = response.json()
            print(f"Response: {json.dumps(result, indent=2)}")
            return result
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON response")
            print(f"Response Text: {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"Error: {str(e)}")
        return None

def main():
    """Main function to run the tests."""
    # Test query
    query = "RAG"
    filters = {"resource_type": "Tutorial"}
    limit = 5
    
    # Test direct Weaviate
    direct_results = test_direct_weaviate(query, filters, limit)
    
    # Test API endpoint
    api_results = test_api_endpoint(query, "default", filters, limit)
    
    # Compare results
    print("\n=== Comparison ===")
    print(f"Direct Weaviate: {len(direct_results)} results")
    print(f"API Endpoint: {len(api_results.get('resources', [])) if api_results else 0} results")
    
    # Check if there's a discrepancy
    if direct_results and (not api_results or not api_results.get('resources')):
        print("\nDiscrepancy detected: Direct Weaviate returns results but API endpoint doesn't")
        print("This could indicate an issue with the API implementation")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        print(traceback.format_exc())
        sys.exit(1)