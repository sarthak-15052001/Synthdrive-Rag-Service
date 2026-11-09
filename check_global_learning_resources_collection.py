import logging
from src.data_stores.weaviate_client import WeaviateClient

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_global_learning_resources_collection():
    """Check the contents of the Global_LearningResources collection in Weaviate."""
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
        
        # Check if Global_LearningResources exists
        if "Global_LearningResources" not in classes:
            logger.error("Global_LearningResources class not found in schema!")
            # Try to create it if it doesn't exist
            logger.info("Attempting to create Global_LearningResources class...")
            weaviate_client._create_global_learning_resources_class()
            return
        
        # Count objects in Global_LearningResources class
        try:
            # Get object count directly
            result = weaviate_client.client.query.aggregate("Global_LearningResources").with_meta_count().do()
            print(f"Aggregate result for Global_LearningResources: {result}")
            
            # Extract count
            count = 0
            if result and "data" in result and "Aggregate" in result["data"] and "Global_LearningResources" in result["data"]["Aggregate"]:
                count = result["data"]["Aggregate"]["Global_LearningResources"][0]["meta"]["count"]
            
            print(f"Class Global_LearningResources has {count} objects")
            
            # Get all learning resources from the collection
            get_result = weaviate_client.client.query.get(
                "Global_LearningResources",
                ["title", "content", "url", "author", "resource_type", "resource_id", "tags"]
            ).with_additional(["id"]).with_limit(10).do()
            
            if get_result and "data" in get_result and "Get" in get_result["data"] and "Global_LearningResources" in get_result["data"]["Get"]:
                objects = get_result["data"]["Get"]["Global_LearningResources"]
                print(f"\nLearning Resources in Global_LearningResources collection:")
                for i, obj in enumerate(objects):
                    print(f"{i+1}. {obj.get('title')} (ID: {obj.get('_additional', {}).get('id')})")
                    print(f"   Author: {obj.get('author')}")
                    print(f"   Resource Type: {obj.get('resource_type')}")
                    print(f"   URL: {obj.get('url')}")
                    print(f"   Resource ID: {obj.get('resource_id')}")
                    print(f"   Tags: {obj.get('tags')}")
                    print(f"   Content Preview: {obj.get('content')[:100]}...")
                    print()
            else:
                print(f"No learning resources found in Global_LearningResources collection")
                
        except Exception as e:
            logger.error(f"Error checking Global_LearningResources class: {str(e)}")
    
    except Exception as e:
        logger.error(f"Error checking Weaviate collections: {str(e)}")

if __name__ == "__main__":
    check_global_learning_resources_collection()