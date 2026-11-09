"""
Test script for the updated RAG Planner API.

This script tests the planner's ability to analyze queries and generate retrieval strategies
using specific Weaviate collections (Tenant_UploadedFiles, Global_Tools, Global_Ecosystem, 
Global_LearningResources) and Neo4j graph database.
"""
import json
import requests
import os
import sys
import logging
from pprint import pprint

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# API configuration
API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000")
API_KEY = os.environ.get("API_KEY", "test-api-key")
PLANNER_ENDPOINT = f"{API_BASE_URL}/api/v1/planner"

# Headers for API requests
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}"
}

def load_test_payloads():
    """Load test payloads from the JSON file."""
    try:
        with open("rag_planner_sample_payloads.json", "r") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading test payloads: {str(e)}")
        sys.exit(1)

def test_planner_api(query_type, payload):
    """Test the planner API with a specific query type and payload."""
    logger.info(f"Testing planner API with {query_type} query")
    
    try:
        # Make the API request
        response = requests.post(PLANNER_ENDPOINT, headers=HEADERS, json=payload)
        
        # Check if the request was successful
        if response.status_code == 200:
            result = response.json()
            
            # Log the response
            logger.info(f"Planner API response for {query_type} query:")
            logger.info(f"Original Query: {result.get('original_query', 'N/A')}")
            logger.info(f"Plan: {result.get('plan', 'No plan generated')}")
            
            # Check if collections_to_search is present and not empty
            collections = result.get('collections_to_search', [])
            if collections:
                logger.info(f"Collections to search: {', '.join(collections)}")
            else:
                logger.warning("No collections identified for searching")
            
            # Save the response to a file
            with open("planner_test_results.json", "a") as f:
                f.write(f"\n\n--- {query_type} Query ---\n")
                f.write(json.dumps(result, indent=2))
            
            # Verify the response contains all expected fields
            expected_fields = [
                "original_query", "organization_id", "plan", 
                "collections_to_search", "retrieved_docs", 
                "graph_insights", "final_answer", "error_log"
            ]
            
            missing_fields = [field for field in expected_fields if field not in result]
            if missing_fields:
                logger.warning(f"Response is missing expected fields: {', '.join(missing_fields)}")
            
            return True, result
        else:
            logger.error(f"Error response from planner API: {response.status_code} - {response.text}")
            return False, None
    
    except Exception as e:
        logger.error(f"Exception during planner API test: {str(e)}")
        return False, None

def main():
    """Main function to run the tests."""
    # Clear previous test results
    with open("planner_test_results.json", "w") as f:
        f.write("# RAG Planner API Test Results\n")
    
    # Load test payloads
    payloads = load_test_payloads()
    
    # Test each query type
    results = {}
    for query_type, payload in payloads.items():
        success, result = test_planner_api(query_type, payload)
        results[query_type] = {
            "success": success,
            "collections_identified": result.get("collections_to_search", []) if result else []
        }
    
    # Print summary
    logger.info("\n--- Test Summary ---")
    for query_type, result in results.items():
        status = "✅ Passed" if result["success"] else "❌ Failed"
        collections = ", ".join(result["collections_identified"]) if result["collections_identified"] else "None"
        logger.info(f"{query_type}: {status} - Collections: {collections}")

if __name__ == "__main__":
    main()