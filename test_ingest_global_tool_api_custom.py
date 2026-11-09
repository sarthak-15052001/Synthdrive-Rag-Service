import requests
import json
import time
import sys
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Configuration
API_URL = "http://localhost:8000/api/v1/rag/ingest/global/tool"
HEADERS = {"Content-Type": "application/json"}

# Sample data for testing with a unique name
test_data = {
    "name": "TestAITool Unique Name",
    "description": "This is a test AI tool with a unique name for verification",
    "use_case": "Testing the global tool ingestion API endpoint with a unique name",
    "url": "https://example.com/test-tool-unique",
    "category": "Testing",
    "pricing": "Free",
    "reviews": "No reviews yet",
    "rating": 4.5,
    "tags": ["test", "api", "ingestion", "unique"],
    "tenant_id": "global"  # Using global tenant
}

def test_ingest_global_tool_api():
    """Test the global tool ingestion API endpoint with a unique name."""
    print("Testing global tool ingestion API with a unique name...")
    
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
            
            job_id = result.get("job_id")
            print(f"\nSuccessfully initiated global tool ingestion with job ID: {job_id}")
            
            # Wait for ingestion to complete
            print("Waiting 10 seconds for ingestion to complete...")
            time.sleep(10)
            
            # Check if the tool was added to the collection
            print("Checking if the tool was added to the Global_Tools collection...")
            from check_global_tools_collection import check_global_tools_collection
            check_global_tools_collection()
            
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