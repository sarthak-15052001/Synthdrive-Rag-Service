"""
Test script for the updated Kernel of Truth API endpoint.
"""

import requests
import json
import logging
import sys

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_kernel_of_truth_api():
    """
    Test the Kernel of Truth API endpoint with a sample query.
    """
    try:
        # API endpoint URL (adjust if needed)
        url = "http://localhost:8000/api/v1/rag/kernel-of-truth/query"
        
        # Sample request payload
        payload = {
            "query": "What workflows did user John create?",
            "tenant_id": "default",
            "max_depth": 3,
            "limit": 10
        }
        
        # Headers
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer test_token"  # Replace with actual token if needed
        }
        
        # Send the request
        logger.info(f"Sending request to {url} with payload: {payload}")
        response = requests.post(url, json=payload, headers=headers)
        
        # Check the response
        if response.status_code == 200:
            logger.info("Request successful!")
            result = response.json()
            logger.info(f"Response: {json.dumps(result, indent=2)}")
            return True
        else:
            logger.error(f"Request failed with status code: {response.status_code}")
            logger.error(f"Response: {response.text}")
            return False
    
    except Exception as e:
        logger.error(f"Error testing Kernel of Truth API: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_kernel_of_truth_api()
    sys.exit(0 if success else 1)