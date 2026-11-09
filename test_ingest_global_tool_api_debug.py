import requests
import json
import time
import sys
import logging
from src.data_stores.weaviate_client import WeaviateClient

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

# Sample data for testing
test_data = {
    "name": "TestAITool API Debug",
    "description": "This is a test AI tool for debugging the ingestion pipeline",
    "use_case": "Debugging the global tool ingestion API endpoint",
    "url": "https://example.com/test-tool-debug",
    "category": "Debugging",
    "pricing": "Free",
    "reviews": "No reviews yet",
    "rating": 4.5,
    "tags": ["test", "api", "debug", "ingestion"],
    "tenant_id": "global"  # Using global tenant
}

def check_weaviate_before_after():
    """Check Weaviate before and after API call to see if objects are added."""
    # Initialize Weaviate client
    print("Initializing Weaviate client...")
    weaviate_client = WeaviateClient()
    print("Weaviate client initialized successfully")
    
    # Check initial count
    print("Checking initial count of objects in Global_Tools...")
    result = weaviate_client.client.query.aggregate("Global_Tools").with_meta_count().do()
    print(f"Initial aggregate result: {result}")
    
    initial_count = 0
    if result and "data" in result and "Aggregate" in result["data"] and "Global_Tools" in result["data"]["Aggregate"]:
        initial_count = result["data"]["Aggregate"]["Global_Tools"][0]["meta"]["count"]
    
    print(f"Initial count of objects in Global_Tools: {initial_count}")
    
    # Make the API call
    print("Making API call to ingest global tool...")
    try:
        response = requests.post(API_URL, json=test_data, headers=HEADERS)
        print(f"API response status code: {response.status_code}")
        print(f"API response content: {response.text}")
        
        # Check if request was successful
        if response.status_code == 200:
            result = response.json()
            print(f"API Response JSON: {json.dumps(result, indent=2)}")
            
            # Verify the response contains expected fields
            if "job_id" in result:
                job_id = result.get("job_id")
                print(f"Successfully initiated global tool ingestion with job ID: {job_id}")
                
                # Wait a bit for the ingestion to complete
                print("Waiting for ingestion to complete...")
                time.sleep(5)
                
                # Check final count
                print("Checking final count of objects in Global_Tools...")
                result = weaviate_client.client.query.aggregate("Global_Tools").with_meta_count().do()
                print(f"Final aggregate result: {result}")
                
                final_count = 0
                if result and "data" in result and "Aggregate" in result["data"] and "Global_Tools" in result["data"]["Aggregate"]:
                    final_count = result["data"]["Aggregate"]["Global_Tools"][0]["meta"]["count"]
                
                print(f"Final count of objects in Global_Tools: {final_count}")
                
                if final_count > initial_count:
                    print("API ingestion successful! Object count increased.")
                    
                    # Get the added tool to verify its contents
                    print("Getting objects from Global_Tools...")
                    get_result = weaviate_client.client.query.get(
                        "Global_Tools",
                        ["name", "description", "use_case", "url", "category", "tool_id"]
                    ).with_additional(["id"]).with_limit(5).do()
                    
                    print(f"Get result: {get_result}")
                    
                    if get_result and "data" in get_result and "Get" in get_result["data"] and "Global_Tools" in get_result["data"]["Get"]:
                        objects = get_result["data"]["Get"]["Global_Tools"]
                        print(f"Sample objects from Global_Tools:")
                        for obj in objects:
                            print(f"  - {obj.get('name')} (ID: {obj.get('_additional', {}).get('id')})")
                    else:
                        print(f"No sample objects found in Global_Tools despite count increase")
                else:
                    print("API ingestion failed! Object count did not increase.")
                    print("Let's try to debug the ingestion pipeline...")
                    
                    # Debug the ingestion pipeline
                    debug_ingestion_pipeline(job_id)
            else:
                print("Missing job_id in response")
        else:
            print(f"Error: API returned status code {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"Exception during API call: {str(e)}")
        import traceback
        print(traceback.format_exc())

def debug_ingestion_pipeline(job_id):
    """Debug the ingestion pipeline to identify where the issue might be."""
    print(f"Debugging ingestion pipeline for job ID: {job_id}")
    
    # Check the ingestion graph implementation
    print("Analyzing ingestion pipeline code...")
    
    # Key areas to check:
    # 1. The API endpoint in src/api/v1/endpoints/ingest.py
    print("1. API Endpoint (ingest.py):")
    print("   - Receives request at /ingest/global/tool")
    print("   - Prepares input_data with content and metadata")
    print("   - Calls ingestion_graph.ingest_document_async with tenant_id='global'")
    
    # 2. The ingestion graph in src/ingestion/graph.py
    print("2. Ingestion Graph (graph.py):")
    print("   - Receives input_data and tenant_id")
    print("   - Runs through nodes: load_document -> chunk_and_embed -> extract_entities -> route_to_stores -> store_in_weaviate")
    
    # 3. The nodes in src/ingestion/nodes.py
    print("3. Ingestion Nodes (nodes.py):")
    print("   - load_document: Processes global_tool data")
    print("   - chunk_and_embed: Creates chunks and embeddings")
    print("   - store_in_weaviate: Stores in Weaviate")
    
    # 4. The Weaviate client in src/data_stores/weaviate_client.py
    print("4. Weaviate Client (weaviate_client.py):")
    print("   - add_document method with class_name='Global_Tools'")
    
    # Potential issues:
    print("\nPotential issues:")
    print("1. The source_type 'global_tool' might not be properly handled in the ingestion pipeline")
    print("2. The document_type might not be set correctly for routing to Global_Tools class")
    print("3. The store_in_weaviate function might not be correctly determining the class_name")
    print("4. There might be an error in the ingestion pipeline that's being caught but not logged")
    
    # Let's try to add a tool directly to verify the Weaviate client works
    print("\nTesting direct tool addition to verify Weaviate client...")
    try:
        weaviate_client = WeaviateClient()
        
        # Create a test tool
        test_tool = {
            "name": "Test Tool Direct from Debug",
            "description": "A test tool added directly via client method during debugging",
            "use_case": "Debugging the ingestion pipeline",
            "url": "https://example.com/debug",
            "category": "Debugging",
            "pricing": "Free",
            "reviews": "No reviews yet",
            "rating": 4.5,
            "tags": ["test", "debug"]
        }
        
        # Add the tool directly using the client method
        print("Adding test tool directly...")
        tool_id = weaviate_client.add_global_tool(test_tool, tenant_id="global")
        print(f"Added test tool directly with ID: {tool_id}")
        
        # Check if it was added successfully
        print("Checking if tool was added successfully...")
        result = weaviate_client.client.query.aggregate("Global_Tools").with_meta_count().do()
        print(f"Aggregate result after direct addition: {result}")
        
        # Recommendation:
        print("\nRecommendation:")
        print("Check the store_in_weaviate function in nodes.py to ensure it correctly identifies global tools")
        print("and routes them to the Global_Tools class in Weaviate.")
        print("The issue is likely in how the source_type or document_type is being handled in the ingestion pipeline.")
    except Exception as e:
        print(f"Error during direct tool addition: {str(e)}")
        import traceback
        print(traceback.format_exc())

if __name__ == "__main__":
    check_weaviate_before_after()