import time
from src.data_stores.weaviate_client import WeaviateClient

def test_add_global_tool_direct_verify():
    """Test adding a global tool directly using the WeaviateClient and verify it was added."""
    try:
        print("Starting direct verification test...")
        
        # Initialize Weaviate client
        weaviate_client = WeaviateClient()
        print("Weaviate client initialized")
        
        # Check initial count
        result = weaviate_client.client.query.aggregate("Global_Tools").with_meta_count().do()
        initial_count = 0
        if result and "data" in result and "Aggregate" in result["data"] and "Global_Tools" in result["data"]["Aggregate"]:
            initial_count = result["data"]["Aggregate"]["Global_Tools"][0]["meta"]["count"]
        
        print(f"Initial count of objects in Global_Tools: {initial_count}")
        print(f"Initial query result: {result}")
        
        # Create a test tool with a unique name
        test_tool = {
            "name": f"Test Tool Verification {time.time()}",
            "description": "A test tool for verification",
            "use_case": "Testing direct tool addition and verification",
            "url": "https://example.com/test-verify",
            "category": "Verification",
            "pricing": "Free",
            "reviews": "No reviews yet",
            "rating": 4.5,
            "tags": ["test", "verify"]
        }
        
        # Add the tool directly using the client method
        print("Adding test tool directly...")
        tool_id = weaviate_client.add_global_tool(test_tool, tenant_id="global")
        print(f"Added test tool directly with ID: {tool_id}")
        
        # Wait a moment for the operation to complete
        print("Waiting for the operation to complete...")
        time.sleep(2)
        
        # Check if it was added successfully
        result = weaviate_client.client.query.aggregate("Global_Tools").with_meta_count().do()
        new_count = 0
        if result and "data" in result and "Aggregate" in result["data"] and "Global_Tools" in result["data"]["Aggregate"]:
            new_count = result["data"]["Aggregate"]["Global_Tools"][0]["meta"]["count"]
        
        print(f"After direct addition, Global_Tools has {new_count} objects")
        print(f"Updated query result: {result}")
        
        if new_count > initial_count:
            print("Direct addition successful! Object count increased.")
            
            # Get the added tool to verify its contents
            get_result = weaviate_client.client.query.get(
                "Global_Tools",
                ["name", "description", "use_case", "url", "category", "tool_id"]
            ).with_additional(["id"]).with_limit(10).do()
            
            print(f"Get query result: {get_result}")
            
            if get_result and "data" in get_result and "Get" in get_result["data"] and "Global_Tools" in get_result["data"]["Get"]:
                objects = get_result["data"]["Get"]["Global_Tools"]
                print(f"Sample objects from Global_Tools:")
                for i, obj in enumerate(objects):
                    print(f"{i+1}. {obj.get('name')} (ID: {obj.get('_additional', {}).get('id')})")
                    print(f"   Description: {obj.get('description')}")
                    print(f"   Use Case: {obj.get('use_case')}")
                    print(f"   URL: {obj.get('url')}")
                    print(f"   Category: {obj.get('category')}")
                    print(f"   Tool ID: {obj.get('tool_id')}")
                    print("")
            else:
                print(f"No sample objects found in Global_Tools despite count increase")
        else:
            print("Direct addition failed! Object count did not increase.")
    
    except Exception as e:
        print(f"Error testing direct tool addition: {str(e)}")
        import traceback
        print(traceback.format_exc())

if __name__ == "__main__":
    test_add_global_tool_direct_verify()