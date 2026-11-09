"""
Test script for the Conditional Edge Router.

This script tests the functionality of the Conditional Edge Router by sending
requests to the API endpoint and verifying the responses.
"""
import asyncio
import json
import logging
import sys
from typing import Dict, Any, List

import httpx
from fastapi import FastAPI, Request, Depends
from fastapi.testclient import TestClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Import the necessary modules
from src.main import app
from src.api.v1.schemas import ConditionalEdgeRouterRequest, ConditionalEdgeRouterResponse

# Create a test client
client = TestClient(app)

async def test_conditional_edge_router():
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
    
    response = client.post(
        "/api/v1/rag/conditional-edge-router",
        json=request_data
    )
    
    logger.info(f"Response status code: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        logger.info(f"Next node: {result.get('next_node')}")
        logger.info(f"Reason: {result.get('reason')}")
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
    
    response = client.post(
        "/api/v1/rag/conditional-edge-router",
        json=request_data
    )
    
    logger.info(f"Response status code: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        logger.info(f"Next node: {result.get('next_node')}")
        logger.info(f"Reason: {result.get('reason')}")
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
    
    response = client.post(
        "/api/v1/rag/conditional-edge-router",
        json=request_data
    )
    
    logger.info(f"Response status code: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        logger.info(f"Next node: {result.get('next_node')}")
        logger.info(f"Reason: {result.get('reason')}")
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
    
    response = client.post(
        "/api/v1/rag/conditional-edge-router",
        json=request_data
    )
    
    logger.info(f"Response status code: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        logger.info(f"Next node: {result.get('next_node')}")
        logger.info(f"Reason: {result.get('reason')}")
    else:
        logger.error(f"Error: {response.text}")

if __name__ == "__main__":
    """
    Run the test script.
    """
    asyncio.run(test_conditional_edge_router())