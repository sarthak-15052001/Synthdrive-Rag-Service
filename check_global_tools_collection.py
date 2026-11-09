import logging
from src.data_stores.weaviate_client import WeaviateClient

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_global_tools_collection():
    """Check the contents of the Global_Tools collection in Weaviate."""
    try:
        # Initialize Weaviate client
        weaviate_client = WeaviateClient()
        
        # Get schema to check available classes
        schema = weaviate_client.client.schema.get()
        classes = []
        if "classes" in schema:
            for cls in schema["classes"]:
                if "class" in cls:
                    classes.append(cls["class"])
        
        print(f"Available Weaviate classes: {classes}")
        
        # Check if Global_Tools exists
        if "Global_Tools" not in classes:
            logger.error("Global_Tools class not found in schema!")
            # Try to create it if it doesn't exist
            logger.info("Attempting to create Global_Tools class...")
            weaviate_client._create_global_tools_class()
            return
        
        # Count objects in Global_Tools class
        try:
            # Get object count directly
            result = weaviate_client.client.query.aggregate("Global_Tools").with_meta_count().do()
            print(f"Aggregate result for Global_Tools: {result}")
            
            # Extract count
            count = 0
            if result and "data" in result and "Aggregate" in result["data"] and "Global_Tools" in result["data"]["Aggregate"]:
                count = result["data"]["Aggregate"]["Global_Tools"][0]["meta"]["count"]
            
            print(f"Class Global_Tools has {count} objects")
            
            # Get all tools from the collection
            get_result = weaviate_client.client.query.get(
                "Global_Tools",
                ["name", "description", "use_case", "url", "category", "tool_id"]
            ).with_additional(["id"]).with_limit(10).do()
            
            if get_result and "data" in get_result and "Get" in get_result["data"] and "Global_Tools" in get_result["data"]["Get"]:
                objects = get_result["data"]["Get"]["Global_Tools"]
                print(f"\nTools in Global_Tools collection:")
                for i, obj in enumerate(objects):
                    print(f"{i+1}. {obj.get('name')} (ID: {obj.get('_additional', {}).get('id')})")
                    print(f"   Description: {obj.get('description')}")
                    print(f"   Use Case: {obj.get('use_case')}")
                    print(f"   URL: {obj.get('url')}")
                    print(f"   Category: {obj.get('category')}")
                    print(f"   Tool ID: {obj.get('tool_id')}")
                    print()
            else:
                print(f"No tools found in Global_Tools collection")
                
        except Exception as e:
            logger.error(f"Error checking Global_Tools class: {str(e)}")
    
    except Exception as e:
        logger.error(f"Error checking Weaviate collections: {str(e)}")

if __name__ == "__main__":
    check_global_tools_collection()