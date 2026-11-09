import logging
from src.data_stores.weaviate_client import WeaviateClient

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_global_ecosystem_collection():
    """Check the contents of the Global_Ecosystem collection in Weaviate."""
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
        
        # Check if Global_Ecosystem exists
        if "Global_Ecosystem" not in classes:
            logger.error("Global_Ecosystem class not found in schema!")
            # Try to create it if it doesn't exist
            logger.info("Attempting to create Global_Ecosystem class...")
            weaviate_client._create_global_ecosystem_class()
            return
        
        # Count objects in Global_Ecosystem class
        try:
            # Get object count directly
            result = weaviate_client.client.query.aggregate("Global_Ecosystem").with_meta_count().do()
            print(f"Aggregate result for Global_Ecosystem: {result}")
            
            # Extract count
            count = 0
            if result and "data" in result and "Aggregate" in result["data"] and "Global_Ecosystem" in result["data"]["Aggregate"]:
                count = result["data"]["Aggregate"]["Global_Ecosystem"][0]["meta"]["count"]
            
            print(f"Class Global_Ecosystem has {count} objects")
            
            # Get all ecosystem partners from the collection
            get_result = weaviate_client.client.query.get(
                "Global_Ecosystem",
                ["name", "bio", "expertise", "certifications", "case_studies", "website", "contact_info", "budget_tier", "partner_id", "tags", "content"]
            ).with_additional(["id"]).with_limit(10).do()
            
            if get_result and "data" in get_result and "Get" in get_result["data"] and "Global_Ecosystem" in get_result["data"]["Get"]:
                objects = get_result["data"]["Get"]["Global_Ecosystem"]
                print(f"\nEcosystem Partners in Global_Ecosystem collection:")
                for i, obj in enumerate(objects):
                    print(f"{i+1}. {obj.get('name')} (ID: {obj.get('_additional', {}).get('id')})")
                    print(f"   Bio: {obj.get('bio')[:100]}...")
                    print(f"   Expertise: {obj.get('expertise')}")
                    print(f"   Website: {obj.get('website')}")
                    print(f"   Budget Tier: {obj.get('budget_tier')}")
                    print(f"   Partner ID: {obj.get('partner_id')}")
                    print(f"   Tags: {obj.get('tags')}")
                    print()
            else:
                print(f"No ecosystem partners found in Global_Ecosystem collection")
                
        except Exception as e:
            logger.error(f"Error checking Global_Ecosystem class: {str(e)}")
    
    except Exception as e:
        logger.error(f"Error checking Weaviate collections: {str(e)}")

if __name__ == "__main__":
    check_global_ecosystem_collection()