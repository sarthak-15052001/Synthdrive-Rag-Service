#!/usr/bin/env python3
"""
Enhanced test script for the Conditional Edge Router API using Python requests.
This script tests different scenarios for the conditional-edge-router endpoint
and provides detailed output formatting.
"""

import json
import requests
import sys
from typing import Dict, Any, List
import logging
import argparse
from datetime import datetime
from colorama import Fore, Style, init

# Initialize colorama
init()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Default settings
DEFAULT_BASE_URL = "http://localhost:8000"
DEFAULT_ENDPOINT = "/api/v1/rag/conditional-edge-router"
DEFAULT_HEADERS = {
    "Content-Type": "application/json",
    # "Authorization": "Bearer your-token-here"  # Uncomment if needed
}

class ConditionalEdgeRouterTester:
    """
    A class to test the Conditional Edge Router API.
    """
    
    def __init__(self, base_url: str = DEFAULT_BASE_URL, endpoint: str = DEFAULT_ENDPOINT, 
                 headers: Dict[str, str] = None, save_results: bool = False):
        """
        Initialize the tester with the given parameters.
        
        Args:
            base_url: The base URL of the API.
            endpoint: The endpoint to test.
            headers: The headers to use for the requests.
            save_results: Whether to save the results to a file.
        """
        self.base_url = base_url
        self.endpoint = endpoint
        self.headers = headers or DEFAULT_HEADERS
        self.save_results = save_results
        self.results = []
        
    def run_test(self, scenario_name: str, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run a test with the given scenario name and request data.
        
        Args:
            scenario_name: The name of the scenario.
            request_data: The request data to send.
            
        Returns:
            The response data.
        """
        print(f"\n{Fore.BLUE}{'=' * 20} Test Case: {scenario_name} {'=' * 20}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Request Payload:{Style.RESET_ALL}")
        print(json.dumps(request_data, indent=2))
        
        try:
            response = requests.post(
                f"{self.base_url}{self.endpoint}",
                headers=self.headers,
                json=request_data,
                timeout=30  # 30 seconds timeout
            )
            
            print(f"{Fore.GREEN}Response Status Code: {response.status_code}{Style.RESET_ALL}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"{Fore.GREEN}Response Body:{Style.RESET_ALL}")
                print(json.dumps(result, indent=2))
                
                # Extract key information
                next_node = result.get('next_node')
                reason = result.get('reason')
                
                print(f"{Fore.GREEN}Next Node:{Style.RESET_ALL} {next_node}")
                print(f"{Fore.GREEN}Reason:{Style.RESET_ALL} {reason}")
                
                # Save the result
                test_result = {
                    "scenario": scenario_name,
                    "request": request_data,
                    "response": result,
                    "status_code": response.status_code,
                    "timestamp": datetime.now().isoformat()
                }
                self.results.append(test_result)
                
                return result
            else:
                print(f"{Fore.RED}Error: {response.text}{Style.RESET_ALL}")
                
                # Save the error
                test_result = {
                    "scenario": scenario_name,
                    "request": request_data,
                    "error": response.text,
                    "status_code": response.status_code,
                    "timestamp": datetime.now().isoformat()
                }
                self.results.append(test_result)
                
                return {"error": response.text, "status_code": response.status_code}
                
        except Exception as e:
            print(f"{Fore.RED}Exception: {str(e)}{Style.RESET_ALL}")
            
            # Save the exception
            test_result = {
                "scenario": scenario_name,
                "request": request_data,
                "exception": str(e),
                "timestamp": datetime.now().isoformat()
            }
            self.results.append(test_result)
            
            return {"exception": str(e)}
    
    def save_results_to_file(self, filename: str = "conditional_edge_router_test_results.md") -> None:
        """
        Save the results to a markdown file.
        
        Args:
            filename: The name of the file to save the results to.
        """
        if not self.results:
            print(f"{Fore.YELLOW}No results to save.{Style.RESET_ALL}")
            return
        
        with open(filename, "w") as f:
            f.write("# Conditional Edge Router API Test Results\n\n")
            f.write(f"Test run at: {datetime.now().isoformat()}\n\n")
            
            for i, result in enumerate(self.results, 1):
                f.write(f"## Test Case {i}: {result['scenario']}\n\n")
                
                f.write("### Request\n\n")
                f.write("```json\n")
                f.write(json.dumps(result['request'], indent=2))
                f.write("\n```\n\n")
                
                if "response" in result:
                    f.write("### Response\n\n")
                    f.write(f"Status Code: {result['status_code']}\n\n")
                    f.write("```json\n")
                    f.write(json.dumps(result['response'], indent=2))
                    f.write("\n```\n\n")
                    
                    # Extract key information
                    next_node = result['response'].get('next_node')
                    reason = result['response'].get('reason')
                    
                    f.write("### Key Information\n\n")
                    f.write(f"- Next Node: `{next_node}`\n")
                    f.write(f"- Reason: {reason}\n\n")
                    
                elif "error" in result:
                    f.write("### Error\n\n")
                    f.write(f"Status Code: {result['status_code']}\n\n")
                    f.write("```\n")
                    f.write(result['error'])
                    f.write("\n```\n\n")
                    
                elif "exception" in result:
                    f.write("### Exception\n\n")
                    f.write("```\n")
                    f.write(result['exception'])
                    f.write("\n```\n\n")
                
                f.write("---\n\n")
            
            f.write("## Summary\n\n")
            f.write(f"Total test cases: {len(self.results)}\n")
            f.write(f"Successful test cases: {sum(1 for r in self.results if 'response' in r)}\n")
            f.write(f"Failed test cases: {sum(1 for r in self.results if 'error' in r or 'exception' in r)}\n")
        
        print(f"{Fore.GREEN}Results saved to {filename}{Style.RESET_ALL}")
    
    def run_all_tests(self) -> None:
        """
        Run all the test cases.
        """
        print(f"{Fore.BLUE}Testing Conditional Edge Router API...{Style.RESET_ALL}")
        
        # Test Case 1: Empty state (should route to planner)
        request_data = {
            "original_query": "What AI tools are available for video generation?",
            "organization_id": "test_org",
            "tenant_id": "test_tenant",
            "plan": None,
            "retrieved_docs": [],
            "graph_insights": [],
            "final_answer": None,
            "error_log": []
        }
        self.run_test("Empty state (should route to planner)", request_data)
        
        # Test Case 2: State with plan but no retrieved docs (should continue retrieval)
        request_data = {
            "original_query": "What AI tools are available for video generation?",
            "organization_id": "test_org",
            "tenant_id": "test_tenant",
            "plan": "First search for AI tools in Weaviate, then query Neo4j for relationships between the found tools.",
            "retrieved_docs": [],
            "graph_insights": [],
            "final_answer": None,
            "error_log": []
        }
        self.run_test("State with plan but no retrieved docs (should continue retrieval)", request_data)
        
        # Test Case 3: State with plan and retrieved docs (should proceed to synthesis)
        request_data = {
            "original_query": "What AI tools are available for video generation?",
            "organization_id": "test_org",
            "tenant_id": "test_tenant",
            "plan": "First search for AI tools in Weaviate, then query Neo4j for relationships between the found tools.",
            "retrieved_docs": [
                {
                    "content": "Runway ML is an AI tool for video generation. It allows users to create videos from text prompts.",
                    "source": "weaviate",
                    "citation_id": "doc-1"
                },
                {
                    "content": "Synthesia is an AI video generation platform that creates videos with virtual avatars.",
                    "source": "weaviate",
                    "citation_id": "doc-2"
                },
                {
                    "content": "Descript offers AI-powered video editing tools including text-based editing and overdub features.",
                    "source": "weaviate",
                    "citation_id": "doc-3"
                }
            ],
            "graph_insights": [
                {
                    "content": "Runway ML and Synthesia are both used in the creative industry for video production.",
                    "source": "graph_database",
                    "citation_id": "graph-1"
                }
            ],
            "final_answer": None,
            "error_log": []
        }
        self.run_test("State with plan and retrieved docs (should proceed to synthesis)", request_data)
        
        # Test Case 4: State with error (should route to error handling)
        request_data = {
            "original_query": "What AI tools are available for video generation?",
            "organization_id": "test_org",
            "tenant_id": "test_tenant",
            "plan": "First search for AI tools in Weaviate, then query Neo4j for relationships between the found tools.",
            "retrieved_docs": [],
            "graph_insights": [],
            "final_answer": None,
            "error_log": ["Error connecting to Weaviate: Connection refused"]
        }
        self.run_test("State with error (should route to error handling)", request_data)
        
        # Test Case 5: Custom query with different organization and tenant
        request_data = {
            "original_query": "What are the best AI tools for natural language processing?",
            "organization_id": "custom_org",
            "tenant_id": "custom_tenant",
            "plan": None,
            "retrieved_docs": [],
            "graph_insights": [],
            "final_answer": None,
            "error_log": []
        }
        self.run_test("Custom query with different organization and tenant", request_data)
        
        print(f"\n{Fore.GREEN}Testing completed!{Style.RESET_ALL}")
        
        if self.save_results:
            self.save_results_to_file()

def parse_args():
    """
    Parse command line arguments.
    
    Returns:
        The parsed arguments.
    """
    parser = argparse.ArgumentParser(description="Test the Conditional Edge Router API")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL, help="The base URL of the API")
    parser.add_argument("--endpoint", default=DEFAULT_ENDPOINT, help="The endpoint to test")
    parser.add_argument("--save-results", action="store_true", help="Save the results to a file")
    parser.add_argument("--output-file", default="conditional_edge_router_test_results.md", 
                        help="The file to save the results to")
    
    return parser.parse_args()

def main():
    """
    Run the test script.
    """
    args = parse_args()
    
    try:
        tester = ConditionalEdgeRouterTester(
            base_url=args.base_url,
            endpoint=args.endpoint,
            save_results=args.save_results
        )
        
        tester.run_all_tests()
        
        if args.save_results:
            tester.save_results_to_file(args.output_file)
            
        print(f"{Fore.GREEN}Testing completed successfully!{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}An error occurred during testing: {str(e)}{Style.RESET_ALL}")
        sys.exit(1)

if __name__ == "__main__":
    main()