#!/usr/bin/env python3
"""
Test script for the Conditional Edge Router API using Python requests.
This script tests different scenarios for the conditional-edge-router endpoint.
"""

import json
import requests
import sys
from typing import Dict, Any, List
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Set the base URL
BASE_URL = "http://localhost:8000"

# Set the API endpoint
ENDPOINT = "/api/v1/rag/conditional-edge-router"

# Set the headers
HEADERS = {
    "Content-Type": "application/json",
    # "Authorization": "Bearer your-token-here"  # Uncomment if needed
}

def test_conditional_edge_router():
    """
    Test the Conditional Edge Router with different scenarios.
    """
    logger.info("Testing Conditional Edge Router...")
    
    # Test Case 1: Empty state (should route to planner)
    logger.info("Test Case 1: Empty state (should route to planner)")
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
    
    response = requests.post(
        f"{BASE_URL}{ENDPOINT}",
        headers=HEADERS,
        json=request_data
    )
    
    logger.info(f"Response status code: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        logger.info(f"Next node: {result.get('next_node')}")
        logger.info(f"Reason: {result.get('reason')}")
        logger.info(f"Updated state: {json.dumps(result.get('updated_state'), indent=2)}")
    else:
        logger.error(f"Error: {response.text}")
    
    # Test Case 2: State with plan but no retrieved docs (should continue retrieval)
    logger.info("Test Case 2: State with plan but no retrieved docs (should continue retrieval)")
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
    
    response = requests.post(
        f"{BASE_URL}{ENDPOINT}",
        headers=HEADERS,
        json=request_data
    )
    
    logger.info(f"Response status code: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        logger.info(f"Next node: {result.get('next_node')}")
        logger.info(f"Reason: {result.get('reason')}")
        logger.info(f"Updated state: {json.dumps(result.get('updated_state'), indent=2)}")
    else:
        logger.error(f"Error: {response.text}")
    
    # Test Case 3: State with plan and retrieved docs (should proceed to synthesis)
    logger.info("Test Case 3: State with plan and retrieved docs (should proceed to synthesis)")
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
    
    response = requests.post(
        f"{BASE_URL}{ENDPOINT}",
        headers=HEADERS,
        json=request_data
    )
    
    logger.info(f"Response status code: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        logger.info(f"Next node: {result.get('next_node')}")
        logger.info(f"Reason: {result.get('reason')}")
        logger.info(f"Updated state: {json.dumps(result.get('updated_state'), indent=2)}")
    else:
        logger.error(f"Error: {response.text}")
    
    # Test Case 4: State with error (should route to error handling)
    logger.info("Test Case 4: State with error (should route to error handling)")
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
    
    response = requests.post(
        f"{BASE_URL}{ENDPOINT}",
        headers=HEADERS,
        json=request_data
    )
    
    logger.info(f"Response status code: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        logger.info(f"Next node: {result.get('next_node')}")
        logger.info(f"Reason: {result.get('reason')}")
        logger.info(f"Updated state: {json.dumps(result.get('updated_state'), indent=2)}")
    else:
        logger.error(f"Error: {response.text}")

def main():
    """
    Run the test script.
    """
    try:
        test_conditional_edge_router()
        logger.info("Testing completed successfully!")
    except Exception as e:
        logger.error(f"An error occurred during testing: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()