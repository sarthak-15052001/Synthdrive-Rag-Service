#!/usr/bin/env python3
"""
Script to test error handling scenarios for the learning resources search API.
"""

import requests
import json
import sys

# Default base URL for the API
DEFAULT_BASE_URL = "http://localhost:8000/api/v1"

def test_api_endpoint(query, tenant_id="default", filters=None, limit=5, base_url=DEFAULT_BASE_URL):
    """Test the API endpoint with the given parameters"""
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
    try:
        response = requests.post(
            f"{base_url}/rag/learning-resources/search",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        # Print response details
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
    """Main function to test error handling scenarios."""
    # Test cases for error handling
    error_test_cases = [
        {
            "name": "Empty query",
            "query": "",
            "tenant_id": "default",
            "filters": None,
            "limit": 5
        },
        {
            "name": "Invalid limit (negative)",
            "query": "RAG",
            "tenant_id": "default",
            "filters": None,
            "limit": -1
        },
        {
            "name": "Invalid limit (zero)",
            "query": "RAG",
            "tenant_id": "default",
            "filters": None,
            "limit": 0
        },
        {
            "name": "Very large limit",
            "query": "RAG",
            "tenant_id": "default",
            "filters": None,
            "limit": 1000
        },
        {
            "name": "Invalid filter format",
            "query": "RAG",
            "tenant_id": "default",
            "filters": {"invalid_filter": "value"},
            "limit": 5
        },
        {
            "name": "Non-existent tenant",
            "query": "RAG",
            "tenant_id": "non_existent_tenant",
            "filters": None,
            "limit": 5
        }
    ]
    
    # Run each test case
    for test_case in error_test_cases:
        print(f"\n{'=' * 60}")
        print(f"Error Test Case: {test_case['name']}")
        print(f"{'=' * 60}")
        
        # Run the test
        result = test_api_endpoint(
            test_case["query"],
            test_case["tenant_id"],
            test_case["filters"],
            test_case["limit"]
        )
        
        # Check if the API handled the error correctly
        if result is not None:
            if "error" in result:
                print(f"API correctly returned an error: {result['error']}")
            else:
                print(f"API did not return an error for this case")
                if "resources" in result and len(result["resources"]) == 0:
                    print(f"API returned empty resources list")
                else:
                    print(f"API returned {len(result.get('resources', []))} resources")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        print(traceback.format_exc())
        sys.exit(1)