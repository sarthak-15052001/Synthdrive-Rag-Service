#!/usr/bin/env python3
"""
Comprehensive test script for the /api/v1/rag/learning-resources/search API endpoint.

This script tests the RAG learning resources search API with both Weaviate and Neo4j,
including various query types, filter combinations, and relationship queries.

Usage:
    python test_rag_learning_resources_search_comprehensive.py [options]
"""

import requests
import json
import time
import argparse
import sys
from datetime import datetime
import logging
import colorama
from colorama import Fore, Style
from typing import Dict, List, Any, Optional, Union

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


class RagLearningResourcesTester:
    """Class to test the RAG learning resources search API endpoint with both Weaviate and Neo4j."""
    
    def __init__(self, base_url: str = DEFAULT_BASE_URL, verbose: bool = False):
        """
        Initialize the tester with the base URL.
        
        Args:
            base_url: Base URL for the API
            verbose: Enable verbose output
        """
        self.base_url = base_url
        self.learning_resources_endpoint = "rag/learning-resources/search"
        self.kernel_of_truth_endpoint = "kernel-of-truth/query"
        self.verbose = verbose
        self.results_history = []
        
    def search_learning_resources(self, 
                    query: str, 
                    tenant_id: str = "default", 
                    filters: Optional[Dict[str, Any]] = None, 
                    limit: int = 5) -> Dict[str, Any]:
        """
        Search for learning resources using the API (Weaviate).
        
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
            logger.info(f"Request URL: {self.base_url}/{self.learning_resources_endpoint}")
            logger.info(f"Request payload: {json.dumps(payload, indent=2)}")
            
        # Make the request
        start_time = time.time()
        try:
            response = requests.post(
                f"{self.base_url}/{self.learning_resources_endpoint}",
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
                    "request_payload": payload,
                    "data_store": "weaviate"
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
                        "request_payload": payload,
                        "data_store": "weaviate"
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
                    "request_payload": payload,
                    "data_store": "weaviate"
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
    
    def query_kernel_of_truth(self, 
                    query: str, 
                    tenant_id: str = "default", 
                    max_depth: int = 3,
                    limit: int = 10) -> Dict[str, Any]:
        """
        Query the Kernel of Truth for relationship insights (Neo4j).
        
        Args:
            query: Natural language query
            tenant_id: Tenant ID (default: "default")
            max_depth: Maximum path depth for relationships
            limit: Maximum number of results to return
            
        Returns:
            API response as a dictionary
        """
        # Create the request payload
        payload = {
            "query": query,
            "tenant_id": tenant_id,
            "max_depth": max_depth,
            "limit": limit
        }
            
        # Log the request details if verbose
        if self.verbose:
            logger.info(f"Request URL: {self.base_url}/{self.kernel_of_truth_endpoint}")
            logger.info(f"Request payload: {json.dumps(payload, indent=2)}")
            
        # Make the request
        start_time = time.time()
        try:
            response = requests.post(
                f"{self.base_url}/{self.kernel_of_truth_endpoint}",
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
                    "request_payload": payload,
                    "data_store": "neo4j"
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
                        "request_payload": payload,
                        "data_store": "neo4j"
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
                    "request_payload": payload,
                    "data_store": "neo4j"
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
    
    def print_learning_resources_results(self, results: Dict[str, Any], test_name: str = None) -> None:
        """
        Print the learning resources search results in a formatted way.
        
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
            print(f"{Fore.CYAN}Data Store: {metadata.get('data_store', 'N/A')}")
            
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
        
        # Print resources
        resources = results.get('resources', [])
        if not resources:
            print(f"\n{Fore.YELLOW}No learning resources found. This could be because:")
            print(f"{Fore.YELLOW}1. No resources match the search criteria")
            print(f"{Fore.YELLOW}2. The database doesn't contain any learning resources yet")
            print(f"{Fore.YELLOW}3. The API is working correctly but returning empty results")
            return
            
        print(f"\n{Fore.GREEN}Found {len(resources)} learning resources:")
        
        for i, resource in enumerate(resources, 1):
            print(f"\n{Fore.CYAN}{i}. {Fore.WHITE}{resource.get('title', 'Unnamed Resource')}")
            print(f"   {Fore.YELLOW}Content: {Style.RESET_ALL}{resource.get('content', 'No content')[:100]}...")
            if resource.get('url'):
                print(f"   {Fore.YELLOW}URL: {Style.RESET_ALL}{resource.get('url')}")
            if resource.get('author'):
                print(f"   {Fore.YELLOW}Author: {Style.RESET_ALL}{resource.get('author')}")
            if resource.get('resource_type'):
                print(f"   {Fore.YELLOW}Type: {Style.RESET_ALL}{resource.get('resource_type')}")
            if resource.get('tags'):
                print(f"   {Fore.YELLOW}Tags: {Style.RESET_ALL}{', '.join(resource.get('tags', []))}")
            print(f"   {Fore.YELLOW}Relevance Score: {Style.RESET_ALL}{resource.get('relevance_score', 'N/A')}")
            print(f"   {Fore.YELLOW}Resource ID: {Style.RESET_ALL}{resource.get('resource_id', 'N/A')}")
            print(f"   {Fore.BLUE}{'-' * 40}")
    
    def print_kernel_of_truth_results(self, results: Dict[str, Any], test_name: str = None) -> None:
        """
        Print the Kernel of Truth query results in a formatted way.
        
        Args:
            results: Query results from the API
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
            print(f"{Fore.CYAN}Data Store: {metadata.get('data_store', 'N/A')}")
            
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
        
        # Print insights
        insights = results.get('insights', [])
        if not insights:
            print(f"\n{Fore.YELLOW}No relationship insights found. This could be because:")
            print(f"{Fore.YELLOW}1. No relationships match the search criteria")
            print(f"{Fore.YELLOW}2. The database doesn't contain any relationships yet")
            print(f"{Fore.YELLOW}3. The API is working correctly but returning empty results")
            return
            
        print(f"\n{Fore.GREEN}Found {len(insights)} relationship insights:")
        
        for i, insight in enumerate(insights, 1):
            print(f"\n{Fore.CYAN}{i}. {Fore.WHITE}Insight {insight.get('citation_id', 'Unknown')}")
            print(f"   {Fore.YELLOW}Content: {Style.RESET_ALL}{insight.get('content', 'No content')}")
            print(f"   {Fore.YELLOW}Source: {Style.RESET_ALL}{insight.get('source', 'Unknown')}")
            if insight.get('metadata'):
                print(f"   {Fore.YELLOW}Metadata: {Style.RESET_ALL}{json.dumps(insight.get('metadata', {}), indent=2)}")
            print(f"   {Fore.BLUE}{'-' * 40}")
    
    def save_results_to_file(self, filename: str = None) -> None:
        """
        Save all test results to a JSON file.
        
        Args:
            filename: Name of the file to save results to
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"rag_learning_resources_search_test_results_{timestamp}.json"
            
        with open(filename, 'w') as f:
            json.dump(self.results_history, f, indent=2)
            
        logger.info(f"Results saved to {filename}")
    
    def run_weaviate_test_cases(self) -> None:
        """Run a series of test cases for Weaviate."""
        test_cases = [
            {
                "name": "[Weaviate] Basic search for machine learning resources",
                "query": "machine learning tutorials",
                "tenant_id": "default",
                "filters": None,
                "limit": 5
            },
            {
                "name": "[Weaviate] Search for deep learning resources",
                "query": "deep learning examples",
                "tenant_id": "default",
                "filters": None,
                "limit": 3
            },
            {
                "name": "[Weaviate] Search with resource_type filter",
                "query": "AI tutorials",
                "tenant_id": "default",
                "filters": {"resource_type": "tutorial"},
                "limit": 5
            },
            {
                "name": "[Weaviate] Search with tags filter",
                "query": "python programming",
                "tenant_id": "default",
                "filters": {"tags": ["python"]},
                "limit": 5
            },
            {
                "name": "[Weaviate] Search with multiple tags filter",
                "query": "data science",
                "tenant_id": "default",
                "filters": {"tags": ["python", "data-science"]},
                "limit": 5
            },
            {
                "name": "[Weaviate] Search with combined filters",
                "query": "machine learning for beginners",
                "tenant_id": "default",
                "filters": {
                    "resource_type": "tutorial",
                    "tags": ["beginner", "machine-learning"]
                },
                "limit": 5
            }
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            logger.info(f"Running Weaviate test case {i}: {test_case['name']}")
            
            results = self.search_learning_resources(
                query=test_case["query"],
                tenant_id=test_case["tenant_id"],
                filters=test_case["filters"],
                limit=test_case["limit"]
            )
            
            self.print_learning_resources_results(results, test_case["name"])
    
    def run_neo4j_test_cases(self) -> None:
        """Run a series of test cases for Neo4j."""
        test_cases = [
            {
                "name": "[Neo4j] Find relationships between learning resources",
                "query": "Find relationships between machine learning tutorials",
                "tenant_id": "default",
                "max_depth": 3,
                "limit": 5
            },
            {
                "name": "[Neo4j] Find authors of learning resources",
                "query": "Who are the authors of deep learning resources?",
                "tenant_id": "default",
                "max_depth": 2,
                "limit": 5
            },
            {
                "name": "[Neo4j] Find related topics in learning resources",
                "query": "What topics are related to machine learning?",
                "tenant_id": "default",
                "max_depth": 3,
                "limit": 5
            },
            {
                "name": "[Neo4j] Find learning paths between topics",
                "query": "What is the learning path from basic programming to advanced machine learning?",
                "tenant_id": "default",
                "max_depth": 4,
                "limit": 5
            }
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            logger.info(f"Running Neo4j test case {i}: {test_case['name']}")
            
            results = self.query_kernel_of_truth(
                query=test_case["query"],
                tenant_id=test_case["tenant_id"],
                max_depth=test_case["max_depth"],
                limit=test_case["limit"]
            )
            
            self.print_kernel_of_truth_results(results, test_case["name"])


def main():
    """Main function to run the tests."""
    parser = argparse.ArgumentParser(description="Test the RAG learning resources search API endpoint with both Weaviate and Neo4j.")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL, help="Base URL for the API")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    parser.add_argument("--save-results", action="store_true", help="Save test results to a JSON file")
    parser.add_argument("--weaviate-only", action="store_true", help="Run only Weaviate tests")
    parser.add_argument("--neo4j-only", action="store_true", help="Run only Neo4j tests")
    parser.add_argument("--output-file", help="Output file for test results (optional)")
    
    args = parser.parse_args()
    
    # Create the tester
    tester = RagLearningResourcesTester(base_url=args.base_url, verbose=args.verbose)
    
    # Run the tests
    if args.neo4j_only:
        print(f"\n{Fore.GREEN}Running Neo4j tests only")
        tester.run_neo4j_test_cases()
    elif args.weaviate_only:
        print(f"\n{Fore.GREEN}Running Weaviate tests only")
        tester.run_weaviate_test_cases()
    else:
        print(f"\n{Fore.GREEN}Running both Weaviate and Neo4j tests")
        tester.run_weaviate_test_cases()
        tester.run_neo4j_test_cases()
    
    # Save results if requested
    if args.save_results:
        tester.save_results_to_file(args.output_file)
    
    print(f"\n{Fore.BLUE}{'=' * 60}")
    print(f"{Fore.GREEN}All test cases completed.")
    print(f"{Fore.BLUE}{'=' * 60}")


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
        sys.exit(1)