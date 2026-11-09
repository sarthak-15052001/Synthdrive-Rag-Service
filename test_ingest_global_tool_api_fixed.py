import requests
import json
import time
import sys
from src.data_stores.weaviate_client import WeaviateClient

def test_ingest_global_tool_api():
    """Test the global tool ingestion API endpoint with our fix."""
    print("Testing global tool ingestion API endpoint...")
    
    # Initialize Weaviate client for checking results
    weaviate_client = WeaviateClient()
    
    # Get initial count of objects in Global_Tools
    result = weaviate_client.client.query.aggregate("Global_Tools").with_meta_count().do()
    initial_count = 0
    if result and "data" in result and "Aggregate" in result["data"] and "Global_Tools" in result["data"]["Aggregate"]:
        initial_count = result["data"]["Aggregate"]["Global_Tools"][0]["meta"]["count"]
    
    print(f"Initial count of objects in Global_Tools: {initial_count}")
    
    # Create a unique tool name with timestamp
    timestamp = time.time()
    tool_name = f"API Test Tool {timestamp}"
    
    # Prepare the payload - directly match the GlobalToolIngestionRequest schema
    payload = {
        "tenant_id": "global",
        "name": tool_name,
        "description": "A test tool for API ingestion",
        "use_case": "Testing the fixed API endpoint",
        "url": "https://example.com/api-test",
        "category": "API Testing",
        "pricing": "Free",
        "reviews": "No reviews yet",
        "rating": 4.8,
        "tags": ["api", "test", "fixed"]
    }
    
    # Print the payload for debugging
    print(f"Request payload: {json.dumps(payload, indent=2)}")
    
    # Send the request to the API
    try:
        response = requests.post(
            "http://localhost:8000/api/v1/rag/ingest/global/tool",
            json=payload
        )
        
        # Print the response
        print(f"Response status code: {response.status_code}")
        print(f"Response content: {response.text}")
        
        # Check if the request was successful
        if response.status_code == 200:
            print("API request successful!")
            
            # Wait a moment for the ingestion to complete
            print("Waiting for ingestion to complete...")
            time.sleep(10)  # Increased wait time to ensure ingestion completes
            
            # Now check if the tool was added to Weaviate using the client
            result = weaviate_client.client.query.aggregate("Global_Tools").with_meta_count().do()
            new_count = 0
            if result and "data" in result and "Aggregate" in result["data"] and "Global_Tools" in result["data"]["Aggregate"]:
                new_count = result["data"]["Aggregate"]["Global_Tools"][0]["meta"]["count"]
            
            print(f"After API ingestion, Global_Tools has {new_count} objects")
            
            if new_count > initial_count:
                print("API ingestion successful! Object count increased.")
                
                # Try to find our specific tool by name
                get_result = weaviate_client.client.query.get(
                    "Global_Tools",
                    ["name", "description", "use_case", "url", "category", "tool_id"]
                ).with_additional(["id"]).with_limit(20).do()
                
                if get_result and "data" in get_result and "Get" in get_result["data"] and "Global_Tools" in get_result["data"]["Get"]:
                    objects = get_result["data"]["Get"]["Global_Tools"]
                    found = False
                    
                    print(f"Searching for tool with name: {tool_name}")
                    for obj in objects:
                        if obj.get("name") == tool_name:
                            found = True
                            print(f"Found our tool! Details:")
                            print(f"  Name: {obj.get('name')}")
                            print(f"  Description: {obj.get('description')}")
                            print(f"  Use Case: {obj.get('use_case')}")
                            print(f"  URL: {obj.get('url')}")
                            print(f"  Category: {obj.get('category')}")
                            print(f"  Tool ID: {obj.get('tool_id')}")
                            print(f"  Weaviate ID: {obj.get('_additional', {}).get('id')}")
                            break
                    
                    if not found:
                        print("Could not find our specific tool in the collection.")
                        print("This might indicate the tool was added with a different name or the ingestion is still in progress.")
                        print("Here are the most recent tools in the collection:")
                        for i, obj in enumerate(objects[-5:]):  # Show the last 5 tools
                            print(f"{i+1}. {obj.get('name')} (ID: {obj.get('_additional', {}).get('id')})")
                else:
                    print("Could not retrieve tools from Global_Tools collection.")
            else:
                print("API ingestion failed! Object count did not increase.")
        else:
            print(f"API request failed with status code: {response.status_code}")
    
    except Exception as e:
        print(f"Error during API test: {str(e)}")
        import traceback
        print(traceback.format_exc())

if __name__ == "__main__":
    test_ingest_global_tool_api()

if __name__ == "__main__":
    test_ingest_global_tool_api()