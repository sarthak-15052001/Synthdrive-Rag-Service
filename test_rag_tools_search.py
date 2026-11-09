#!/usr/bin/env python3
"""
Test script for the /api/v1/rag/tools/search API endpoint.

This script tests the RAG tools search API with various queries and parameters.
It demonstrates how to use the API to search for AI tools using natural language queries.
"""

import requests
import json
import sys
import argparse
from typing import Dict, Any, List, Optional
from datetime import datetime

# Default base URL for the API
DEFAULT_BASE_URL = "http://localhost:8000/api/v1"

class RagToolsSearchTester:
    """Class to test the RAG tools search API endpoint."""
    
    def __init__(self, base_url: str = DEFAULT_BASE_URL):
        """
        Initialize the tester with the base URL.
        
        Args:
            base_url: Base URL for the API
        """
        self.base_url = base_url
        self.endpoint = "rag/tools/search"
        self.api_url = f"{self.base_url}/{self.endpoint}"
        
    def search_tools(self, 
                    query: str, 
                    tenant_id: str = "default", 
                    filters: Optional[Dict[str, Any]] = None, 
                    limit: int = 5) -> Dict[str, Any]:
        """
        Search for AI tools using the API.
        
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
            
        # Make the request
        try:
            response = requests.post(
                self.api_url,
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            # Check if the request was successful
            response.raise_for_status()
            
            # Parse and return the response
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error making request: {str(e)}")
            if hasattr(e, 'response') and e.response:
                print(f"Response status code: {e.response.status_code}")
                print(f"Response text: {e.response.text}")
            return {"error": str(e)}
    
    def print_results(self, results: Dict[str, Any]) -> None:
        """
        Print the search results in a formatted way.
        
        Args:
            results: Search results from the API
        """
        if "error" in results:
            print(f"Error: {results['error']}")
            return
            
        print(f"\nQuery: {results.get('query', 'N/A')}")
        
        tools = results.get('tools', [])
        if not tools:
            print("No tools found.")
            return
            
        print(f"\nFound {len(tools)} tools:")
        
        for i, tool in enumerate(tools, 1):
            print(f"\n{i}. {tool.get('name', 'Unnamed Tool')}")
            print(f"   Description: {tool.get('description', 'No description')}")
            if tool.get('use_case'):
                print(f"   Use Case: {tool.get('use_case')}")
            print(f"   URL: {tool.get('url', 'No URL')}")
            if tool.get('category'):
                print(f"   Category: {tool.get('category')}")
            if tool.get('pricing'):
                print(f"   Pricing: {tool.get('pricing')}")
            if tool.get('rating'):
                print(f"   Rating: {tool.get('rating')}")
            print(f"   Relevance Score: {tool.get('relevance_score', 'N/A')}")
            print(f"   Tool ID: {tool.get('tool_id', 'N/A')}")
            if tool.get('tags'):
                print(f"   Tags: {', '.join(tool.get('tags', []))}")
            print("   " + "-" * 40)
    
    def run_test_cases(self) -> None:
        """Run a series of test cases to demonstrate the API."""
        test_cases = [
            {
                "name": "Basic search for video tools",
                "query": "find a tool to make videos from text",
                "tenant_id": "default",
                "filters": None,
                "limit": 5
            },
            {
                "name": "Search for coding tools",
                "query": "I need something to help with coding",
                "tenant_id": "default",
                "filters": None,
                "limit": 3
            },
            {
                "name": "Search with category filter",
                "query": "AI tools",
                "tenant_id": "default",
                "filters": {"category": "Development"},
                "limit": 5
            },
            {
                "name": "Search with minimum parameters",
                "query": "data visualization",
                "tenant_id": "default",
                "filters": None,
                "limit": 5
            },
            {
                "name": "Search with tags filter",
                "query": "content creation tools",
                "tenant_id": "default",
                "filters": {"tags": ["video"]},
                "limit": 5
            }
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n{'=' * 60}")
            print(f"Test Case {i}: {test_case['name']}")
            print(f"{'=' * 60}")
            
            results = self.search_tools(
                query=test_case["query"],
                tenant_id=test_case["tenant_id"],
                filters=test_case["filters"],
                limit=test_case["limit"]
            )
            
            self.print_results(results)
            
        print(f"\n{'=' * 60}")
        print("All test cases completed.")
        print(f"{'=' * 60}")

def main():
    """Main function to run the tests."""
    parser = argparse.ArgumentParser(description="Test the RAG tools search API endpoint.")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL, help="Base URL for the API")
    parser.add_argument("--query", help="Specific query to test (optional)")
    parser.add_argument("--tenant-id", default="default", help="Tenant ID to use")
    parser.add_argument("--limit", type=int, default=5, help="Maximum number of results to return")
    parser.add_argument("--category", help="Filter by category (optional)")
    
    args = parser.parse_args()
    
    # Create the tester
    tester = RagToolsSearchTester(base_url=args.base_url)
    
    # If a specific query is provided, run just that query
    if args.query:
        filters = {}
        if args.category:
            filters["category"] = args.category
            
        print(f"\nRunning single query: {args.query}")
        results = tester.search_tools(
            query=args.query,
            tenant_id=args.tenant_id,
            filters=filters if filters else None,
            limit=args.limit
        )
        
        tester.print_results(results)
    else:
        # Run all test cases
        tester.run_test_cases()

if __name__ == "__main__":
    main()