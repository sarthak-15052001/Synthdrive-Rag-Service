import logging
from src.data_stores.weaviate_client import WeaviateClient

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_weaviate_collections():
    """Check the contents of Weaviate collections."""
    try:
        # Initialize Weaviate client
        weaviate_client = WeaviateClient()
        
        # Get schema to check available classes
        schema = weaviate_client.client.schema.get()
        print(f"Schema: {schema}")
        classes = []
        if "classes" in schema:
            for cls in schema["classes"]:
                if "class" in cls:
                    classes.append(cls["class"])
        
        print(f"Available Weaviate classes: {classes}")
        
        # Check if Global_Ecosystem exists
        if "Global_Ecosystem" not in classes:
            logger.error("Global_Ecosystem class not found in schema!")
            return
        
        # Count objects in each class
        for class_name in classes:
            try:
                # Get object count directly
                result = weaviate_client.client.query.aggregate(class_name).with_meta_count().do()
                print(f"Aggregate result for {class_name}: {result}")
                
                # Extract count
                count = 0
                if result and "data" in result and "Aggregate" in result["data"] and class_name in result["data"]["Aggregate"]:
                    count = result["data"]["Aggregate"][class_name][0]["meta"]["count"]
                
                print(f"Class {class_name} has {count} objects")
                
                # If it's the Global_Ecosystem class, get some sample objects
                if class_name == "Global_Ecosystem" and count > 0:
                    # Get sample objects
                    get_result = weaviate_client.client.query.get(
                        class_name,
                        ["name", "bio", "expertise", "partner_id"]
                    ).with_additional(["id"]).with_limit(5).do()
                    
                    if get_result and "data" in get_result and "Get" in get_result["data"] and class_name in get_result["data"]["Get"]:
                        objects = get_result["data"]["Get"][class_name]
                        logger.info(f"Sample objects from {class_name}:")
                        for obj in objects:
                            logger.info(f"  - {obj.get('name')} (ID: {obj.get('_additional', {}).get('id')})")
                    else:
                        logger.info(f"No sample objects found in {class_name}")
                
            except Exception as e:
                logger.error(f"Error checking class {class_name}: {str(e)}")
    
    except Exception as e:
        logger.error(f"Error checking Weaviate collections: {str(e)}")

if __name__ == "__main__":
    check_weaviate_collections()