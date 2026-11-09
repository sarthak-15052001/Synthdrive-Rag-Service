#!/usr/bin/env python3
"""
Comprehensive test script for the /api/v1/rag/tools/search API endpoint.

This script provides a thorough testing framework for the RAG tools search API,
including various query types, filter combinations, and error handling scenarios.

Usage:
    ./test_rag_tools_search_comprehensive.py [options]

Options:
    --base-url BASE_URL    Base URL for the API (default: http://localhost:8000/api/v1)
    --query QUERY          Specific query to test (optional)
    --tenant-id TENANT_ID  Tenant ID to use (default: default)
    --limit LIMIT          Maximum number of results to return (default: 5)
    --category CATEGORY    Filter by category (optional)
    --tags TAGS            Filter by tags, comma-separated (optional)
    --rating RATING        Filter by minimum rating (optional)
    --verbose              Enable verbose output
    --save-results         Save test results to a JSON file
    --test-case TEST_CASE  Run a specific test case by number
    --add-sample-data      Add sample data before running tests
"""

import requests
import json
import sys
import argparse
import time
import os
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
import logging
import colorama
from colorama import Fore, Style

# Initialize colorama
colorama.init(autoreset=True)

# Default base URL for the API
DEFAULT_BASE_URL = "http://localhost:8000/api/v1"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format=f"{Fore.CYAN}%(asctime)s{Style.RESET_ALL} - {Fore.GREEN}%(levelname)s{Style.RESET_ALL} - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)


class RagToolsSearchTester:
    """Class to test the RAG tools search API endpoint."""
    
    def __init__(self, base_url: str = DEFAULT_BASE_URL, verbose: bool = False):
        """
        Initialize the tester with the base URL.
        
        Args:
            base_url: Base URL for the API
            verbose: Enable verbose output
        """
        self.base_url = base_url
        self.endpoint = "rag/tools/search"
        self.api_url = f"{self.base_url}/{self.endpoint}"
        self.verbose = verbose
        self.results_history = []
        
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
            
        # Log the request details if verbose
        if self.verbose:
            logger.info(f"Request URL: {self.api_url}")
            logger.info(f"Request payload: {json.dumps(payload, indent=2)}")
            
        # Make the request
        start_time = time.time()
        try:
            response = requests.post(
                self.api_url,
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
                
                # Store the result in history
                self.results_history.append(result)
                
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
                self.results_history.append(error_result)
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
            
            self.results_history.append(error_result)
            return error_result
    
    def print_results(self, results: Dict[str, Any], test_name: str = None) -> None:
        """
        Print the search results in a formatted way.
        
        Args:
            results: Search results from the API
            test_name: Name of the test case
        """
        if test_name:
            print(f"\n{Fore.BLUE}{'=' * 60}")
            print(f"{Fore.GREEN}Test Case: {test_name}")
            print(f"{Fore.BLUE}{'=' * 60}")
        
        # Print metadata if available
        if "_metadata" in results:
            metadata = results["_metadata"]
            print(f"\n{Fore.YELLOW}Request Details:")
            print(f"{Fore.CYAN}Status Code: {metadata.get('status_code', 'N/A')}")
            print(f"{Fore.CYAN}Response Time: {metadata.get('response_time', 0):.4f} seconds")
            print(f"{Fore.CYAN}Timestamp: {metadata.get('timestamp', 'N/A')}")
            
            if self.verbose:
                print(f"\n{Fore.YELLOW}Request Payload:")
                print(json.dumps(metadata.get('request_payload', {}), indent=2))
        
        # Check for errors
        if "error" in results:
            print(f"\n{Fore.RED}Error: {results['error']}")
            if "response_text" in results:
                print(f"{Fore.RED}Response Text: {results['response_text']}")
            return
            
        # Print query
        print(f"\n{Fore.YELLOW}Query: {results.get('query', 'N/A')}")
        
        # Print tools
        tools = results.get('tools', [])
        if not tools:
            print(f"\n{Fore.YELLOW}No tools found. This could be because:")
            print(f"{Fore.YELLOW}1. No tools match the search criteria")
            print(f"{Fore.YELLOW}2. The database doesn't contain any tools yet")
            print(f"{Fore.YELLOW}3. The API is working correctly but returning empty results")
            print(f"\n{Fore.CYAN}Suggestion: Run the add_sample_tools_for_testing.py script to add sample data")
            print(f"{Fore.CYAN}Or use the --add-sample-data flag with this script")
            return
            
        print(f"\n{Fore.GREEN}Found {len(tools)} tools:")
        
        for i, tool in enumerate(tools, 1):
            print(f"\n{Fore.CYAN}{i}. {Fore.WHITE}{tool.get('name', 'Unnamed Tool')}")
            print(f"   {Fore.YELLOW}Description: {Style.RESET_ALL}{tool.get('description', 'No description')}")
            if tool.get('use_case'):
                print(f"   {Fore.YELLOW}Use Case: {Style.RESET_ALL}{tool.get('use_case')}")
            print(f"   {Fore.YELLOW}URL: {Style.RESET_ALL}{tool.get('url', 'No URL')}")
            if tool.get('category'):
                print(f"   {Fore.YELLOW}Category: {Style.RESET_ALL}{tool.get('category')}")
            if tool.get('pricing'):
                print(f"   {Fore.YELLOW}Pricing: {Style.RESET_ALL}{tool.get('pricing')}")
            if tool.get('rating'):
                print(f"   {Fore.YELLOW}Rating: {Style.RESET_ALL}{tool.get('rating')}")
            print(f"   {Fore.YELLOW}Relevance Score: {Style.RESET_ALL}{tool.get('relevance_score', 'N/A')}")
            print(f"   {Fore.YELLOW}Tool ID: {Style.RESET_ALL}{tool.get('tool_id', 'N/A')}")
            if tool.get('tags'):
                print(f"   {Fore.YELLOW}Tags: {Style.RESET_ALL}{', '.join(tool.get('tags', []))}")
            print(f"   {Fore.BLUE}{'-' * 40}")
    
    def save_results_to_file(self, filename: str = None) -> None:
        """
        Save all test results to a JSON file.
        
        Args:
            filename: Name of the file to save results to
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"rag_tools_search_results_{timestamp}.json"
            
        with open(filename, 'w') as f:
            json.dump(self.results_history, f, indent=2)
            
        logger.info(f"Results saved to {filename}")
    
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
            },
            {
                "name": "Search with multiple tags filter",
                "query": "content creation tools",
                "tenant_id": "default",
                "filters": {"tags": ["video", "marketing"]},
                "limit": 5
            },
            {
                "name": "Search with rating filter",
                "query": "high quality AI tools",
                "tenant_id": "default",
                "filters": {"rating": 4.5},
                "limit": 5
            },
            {
                "name": "Search with combined filters",
                "query": "AI development tools",
                "tenant_id": "default",
                "filters": {
                    "category": "Development",
                    "tags": ["coding", "programming"],
                    "rating": 4.0
                },
                "limit": 5
            },
            {
                "name": "Error handling - empty query",
                "query": "",
                "tenant_id": "default",
                "filters": None,
                "limit": 5
            },
            {
                "name": "Error handling - invalid limit",
                "query": "AI tools",
                "tenant_id": "default",
                "filters": None,
                "limit": -1
            },
            {
                "name": "Error handling - very large limit",
                "query": "AI tools",
                "tenant_id": "default",
                "filters": None,
                "limit": 1000
            },
            {
                "name": "Search with non-existent category",
                "query": "AI tools",
                "tenant_id": "default",
                "filters": {"category": "NonExistentCategory"},
                "limit": 5
            },
            {
                "name": "Search with non-default tenant",
                "query": "AI tools",
                "tenant_id": "custom-tenant-123",
                "filters": None,
                "limit": 5
            }
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            logger.info(f"Running test case {i}: {test_case['name']}")
            
            results = self.search_tools(
                query=test_case["query"],
                tenant_id=test_case["tenant_id"],
                filters=test_case["filters"],
                limit=test_case["limit"]
            )
            
            self.print_results(results, test_case["name"])
            
        print(f"\n{Fore.BLUE}{'=' * 60}")
        print(f"{Fore.GREEN}All test cases completed.")
        print(f"{Fore.BLUE}{'=' * 60}")


def main():
    """Main function to run the tests."""
    parser = argparse.ArgumentParser(description="Test the RAG tools search API endpoint.")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL, help="Base URL for the API")
    parser.add_argument("--query", help="Specific query to test (optional)")
    parser.add_argument("--tenant-id", default="default", help="Tenant ID to use")
    parser.add_argument("--limit", type=int, default=5, help="Maximum number of results to return")
    parser.add_argument("--category", help="Filter by category (optional)")
    parser.add_argument("--tags", help="Filter by tags, comma-separated (optional)")
    parser.add_argument("--rating", type=float, help="Filter by minimum rating (optional)")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    parser.add_argument("--save-results", action="store_true", help="Save test results to a JSON file")
    parser.add_argument("--test-case", type=int, help="Run a specific test case by number")
    parser.add_argument("--add-sample-data", action="store_true", help="Add sample data before running tests")
    
    args = parser.parse_args()
    
    # Add sample data if requested
    if args.add_sample_data:
        try:
            print(f"{Fore.YELLOW}Adding sample data before running tests...{Style.RESET_ALL}")
            import add_sample_tools_for_testing
            add_sample_tools_for_testing.add_sample_tools()
            print(f"{Fore.GREEN}Sample data added successfully.{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}Error adding sample data: {str(e)}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Continuing with tests...{Style.RESET_ALL}")
    
    # Create the tester
    tester = RagToolsSearchTester(base_url=args.base_url, verbose=args.verbose)
    
    # If a specific query is provided, run just that query
    if args.query:
        filters = {}
        if args.category:
            filters["category"] = args.category
        if args.tags:
            filters["tags"] = args.tags.split(",")
        if args.rating:
            filters["rating"] = args.rating
            
        print(f"\n{Fore.GREEN}Running single query: {args.query}")
        results = tester.search_tools(
            query=args.query,
            tenant_id=args.tenant_id,
            filters=filters if filters else None,
            limit=args.limit
        )
        
        tester.print_results(results, "Custom Query")
    elif args.test_case:
        # Run a specific test case
        test_cases = tester.run_test_cases.__defaults__[0]  # Get the test_cases list from the method defaults
        if 1 <= args.test_case <= len(test_cases):
            test_case = test_cases[args.test_case - 1]
            print(f"\n{Fore.GREEN}Running test case {args.test_case}: {test_case['name']}")
            results = tester.search_tools(
                query=test_case["query"],
                tenant_id=test_case["tenant_id"],
                filters=test_case["filters"],
                limit=test_case["limit"]
            )
            tester.print_results(results, test_case["name"])
        else:
            print(f"{Fore.RED}Invalid test case number. Please choose a number between 1 and {len(test_cases)}.")
    else:
        # Run all test cases
        tester.run_test_cases()
    
    # Save results if requested
    if args.save_results:
        tester.save_results_to_file()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Test interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Fore.RED}An error occurred: {str(e)}")
        import traceback
        print(f"{Fore.RED}{traceback.format_exc()}{Style.RESET_ALL}")
        print(f"\n{Fore.YELLOW}Suggestion: If you're seeing empty results, try running with --add-sample-data flag:{Style.RESET_ALL}")
        print(f"{Fore.CYAN}python test_rag_tools_search_comprehensive.py --add-sample-data{Style.RESET_ALL}")
        sys.exit(1)