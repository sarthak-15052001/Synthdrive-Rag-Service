import requests
import json
import os
from datetime import datetime
import uuid

# Configuration
API_URL = "http://localhost:8000/api/v1/rag/ingest/global/tool"
HEADERS = {"Content-Type": "application/json"}

# Optional: Add authorization if needed
# If you have an API key or token, uncomment and use this
# API_KEY = "your_api_key_here"
# HEADERS["Authorization"] = f"Bearer {API_KEY}"

# Sample data for testing
test_data = {
    "name": "TestAITool",
    "description": "This is a test AI tool for ingestion testing",
    "use_case": "Testing the global tool ingestion API endpoint",
    "url": "https://example.com/test-tool",
    "category": "Testing",
    "pricing": "Free",
    "reviews": "No reviews yet",
    "rating": 4.5,
    "tags": ["test", "api", "ingestion"],
    "tenant_id": "default"  # Using default tenant
}

def test_ingest_global_tool_api():
    """Test the global tool ingestion API endpoint"""
    print("Testing global tool ingestion API...")
    
    try:
        # Send request to the API
        response = requests.post(API_URL, json=test_data, headers=HEADERS)
        
        # Check if request was successful
        if response.status_code == 200:
            result = response.json()
            print("\nAPI Response:")
            print(json.dumps(result, indent=2))
            
            # Verify the response contains expected fields
            assert "job_id" in result, "Missing job_id in response"
            assert "status_code" in result, "Missing status_code in response"
            assert "status_message" in result, "Missing status_message in response"
            
            print(f"\nSuccessfully initiated global tool ingestion with job ID: {result.get('job_id')}")
            print("Test completed successfully!")
            return True
        else:
            print(f"Error: API returned status code {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"Error during API test: {str(e)}")
        return False

if __name__ == "__main__":
    test_ingest_global_tool_api()