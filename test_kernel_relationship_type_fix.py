"""
Test script to verify the fix for relationship_type in Kernel of Truth API.
This script specifically tests that relationship types are properly identified
and not returned as "unknown" in the response.
"""

import requests
import json
import logging
import sys

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_relationship_type_fix():
    """
    Test the Kernel of Truth API endpoint with queries that should trigger
    specific relationship types.
    """
    try:
        # API endpoint URL
        url = "http://localhost:8000/api/v1/rag/kernel-of-truth/query"
        
        # Headers
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer test_token"  # Replace with actual token if needed
        }
        
        # Test cases with expected relationship types
        test_cases = [
            {
                "query": "partners with successful AI-driven analytics case studies",
                "expected_type": "case_study"  # Should be case_study or ai_related
            },
            {
                "query": "What workflows did user John create?",
                "expected_type": "creation"
            },
            {
                "query": "How are AI tools used in data analysis?",
                "expected_type": "usage"
            },
            {
                "query": "Which partners collaborate on machine learning projects?",
                "expected_type": "collaboration"
            }
        ]
        
        # Run each test case
        results = []
        for i, test_case in enumerate(test_cases):
            # Prepare payload
            payload = {
                "query": test_case["query"],
                "tenant_id": "default",
                "max_depth": 3,
                "limit": 10
            }
            
            # Send the request
            logger.info(f"Test case {i+1}: Sending request with query: {test_case['query']}")
            response = requests.post(url, json=payload, headers=headers)
            
            # Check the response
            if response.status_code == 200:
                result = response.json()
                
                # Extract relationship_type from the first insight
                if result.get("insights") and len(result["insights"]) > 0:
                    actual_type = result["insights"][0].get("metadata", {}).get("relationship_type", "not_found")
                    
                    # Check if the relationship_type is not "unknown"
                    if actual_type != "unknown":
                        logger.info(f"✅ Test case {i+1} passed: relationship_type is '{actual_type}' (expected: '{test_case['expected_type']}')")
                        results.append({
                            "query": test_case["query"],
                            "expected_type": test_case["expected_type"],
                            "actual_type": actual_type,
                            "passed": True
                        })
                    else:
                        logger.error(f"❌ Test case {i+1} failed: relationship_type is 'unknown'")
                        results.append({
                            "query": test_case["query"],
                            "expected_type": test_case["expected_type"],
                            "actual_type": actual_type,
                            "passed": False
                        })
                else:
                    logger.error(f"❌ Test case {i+1} failed: No insights found in response")
                    results.append({
                        "query": test_case["query"],
                        "expected_type": test_case["expected_type"],
                        "actual_type": "no_insights",
                        "passed": False
                    })
            else:
                logger.error(f"❌ Test case {i+1} failed: Request failed with status code: {response.status_code}")
                logger.error(f"Response: {response.text}")
                results.append({
                    "query": test_case["query"],
                    "expected_type": test_case["expected_type"],
                    "actual_type": "request_failed",
                    "passed": False
                })
        
        # Print summary
        logger.info("\n--- Test Summary ---")
        passed = sum(1 for r in results if r["passed"])
        total = len(results)
        logger.info(f"Passed: {passed}/{total} tests")
        
        # Print detailed results
        logger.info("\n--- Detailed Results ---")
        for i, result in enumerate(results):
            status = "✅ PASSED" if result["passed"] else "❌ FAILED"
            logger.info(f"Test {i+1}: {status}")
            logger.info(f"  Query: {result['query']}")
            logger.info(f"  Expected type: {result['expected_type']}")
            logger.info(f"  Actual type: {result['actual_type']}")
            logger.info("")
        
        return passed == total
    
    except Exception as e:
        logger.error(f"Error testing Kernel of Truth API: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_relationship_type_fix()
    sys.exit(0 if success else 1)