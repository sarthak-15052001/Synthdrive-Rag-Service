import logging
import sys
from src.data_stores.weaviate_client import WeaviateClient

# Configure logging to output to console
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

def test_add_global_tool_direct():
    """Test adding a global tool directly using the WeaviateClient."""
    print("Starting test_add_global_tool_direct...")
    try:
        # Initialize Weaviate client
        print("Initializing Weaviate client...")
        weaviate_client = WeaviateClient()
        print("Weaviate client initialized successfully")
        
        # Check initial count
        print("Checking initial count of objects in Global_Tools...")
        result = weaviate_client.client.query.aggregate("Global_Tools").with_meta_count().do()
        print(f"Aggregate result: {result}")
        
        initial_count = 0
        if result and "data" in result and "Aggregate" in result["data"] and "Global_Tools" in result["data"]["Aggregate"]:
            initial_count = result["data"]["Aggregate"]["Global_Tools"][0]["meta"]["count"]
        
        print(f"Initial count of objects in Global_Tools: {initial_count}")
        
        # Create a test tool
        test_tool = {
            "name": "Test Tool Direct",
            "description": "A test tool added directly via client method",
            "use_case": "Testing direct tool addition",
            "url": "https://example.com/test",
            "category": "Testing",
            "pricing": "Free",
            "reviews": "No reviews yet",
            "rating": 4.5,
            "tags": ["test", "direct"]
        }
        
        # Add the tool directly using the client method
        print("Adding test tool directly...")
        tool_id = weaviate_client.add_global_tool(test_tool, tenant_id="global")
        print(f"Added test tool directly with ID: {tool_id}")
        
        # Check if it was added successfully
        print("Checking if tool was added successfully...")
        result = weaviate_client.client.query.aggregate("Global_Tools").with_meta_count().do()
        print(f"Aggregate result after addition: {result}")
        
        new_count = 0
        if result and "data" in result and "Aggregate" in result["data"] and "Global_Tools" in result["data"]["Aggregate"]:
            new_count = result["data"]["Aggregate"]["Global_Tools"][0]["meta"]["count"]
        
        print(f"After direct addition, Global_Tools has {new_count} objects")
        
        if new_count > initial_count:
            print("Direct addition successful! The issue is likely in the ingestion pipeline.")
            
            # Get the added tool to verify its contents
            print("Getting added tool to verify contents...")
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
            print("Direct addition failed. There might be an issue with the Weaviate client.")
    
    except Exception as e:
        print(f"Error testing direct tool addition: {str(e)}")
        import traceback
        print(traceback.format_exc())

if __name__ == "__main__":
    test_add_global_tool_direct()