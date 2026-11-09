import logging
import uuid
from src.data_stores.weaviate_client import WeaviateClient

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_add_ecosystem_partner_direct_weaviate():
    """Test adding an ecosystem partner directly using the Weaviate client."""
    try:
        # Initialize Weaviate client
        weaviate_client = WeaviateClient()
        
        # Sample ecosystem partner data with unique name
        partner_name = f"DirectWeaviateTest Inc. {uuid.uuid4().hex[:8]}"
        
        # Create content for embedding
        content = f"Partner name: {partner_name}\n"
        content += f"Bio: DirectWeaviateTest Inc. is a leading technology consulting firm specializing in AI integration, cloud migration, and digital transformation services for enterprise clients.\n"
        content += f"Expertise: AI Integration, Cloud Migration, Digital Transformation, Enterprise Solutions\n"
        content += f"Case studies: Successfully implemented AI-driven analytics platform for Fortune 500 retail client, resulting in 35% increase in operational efficiency and $2.5M annual cost savings.\n"
        
        # Generate a partner ID
        partner_id = str(uuid.uuid4())
        
        # Prepare partner data
        partner_data = {
            "name": partner_name,
            "bio": "DirectWeaviateTest Inc. is a leading technology consulting firm specializing in AI integration, cloud migration, and digital transformation services for enterprise clients.",
            "expertise": ["AI Integration", "Cloud Migration", "Digital Transformation", "Enterprise Solutions"],
            "certifications": ["AWS Certified Solutions Architect", "Google Cloud Professional", "Microsoft Azure Expert"],
            "case_studies": "Successfully implemented AI-driven analytics platform for Fortune 500 retail client, resulting in 35% increase in operational efficiency and $2.5M annual cost savings.",
            "website": "https://directweaviatetest-example.com",
            "contact_info": "partners@directweaviatetest-example.com",
            "budget_tier": "Enterprise",
            "tags": ["AI", "Cloud", "Enterprise", "Digital Transformation"],
            "partner_id": partner_id,
            "content": content,
            "tenant_id": "global"
        }
        
        # Debug logging
        logger.info(f"Partner data: {partner_data}")
        
        # Add the ecosystem partner directly
        partner_id = weaviate_client.add_ecosystem_partner(partner_data, tenant_id="global")
        
        logger.info(f"Successfully added ecosystem partner with ID: {partner_id}")
        
        # Verify the partner was added by checking the Global_Ecosystem collection
        verify_ecosystem_partner_in_weaviate(partner_name)
        
        return True
    except Exception as e:
        logger.error(f"Error adding ecosystem partner directly: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False

def verify_ecosystem_partner_in_weaviate(partner_name):
    """Verify that the ecosystem partner was added to the Global_Ecosystem collection."""
    try:
        # Initialize Weaviate client
        weaviate_client = WeaviateClient()
        
        # Query the Global_Ecosystem collection
        result = weaviate_client.client.query.get(
            "Global_Ecosystem", 
            ["name", "bio", "expertise", "website", "partner_id"]
        ).with_additional(["id"]).with_limit(10).do()
        
        if result and "data" in result and "Get" in result["data"] and "Global_Ecosystem" in result["data"]["Get"]:
            objects = result["data"]["Get"]["Global_Ecosystem"]
            print(f"\nEcosystem Partners in Global_Ecosystem collection:")
            
            found = False
            for i, obj in enumerate(objects):
                print(f"{i+1}. {obj.get('name')} (ID: {obj.get('_additional', {}).get('id')})")
                print(f"   Bio: {obj.get('bio')[:100]}...")
                print(f"   Expertise: {obj.get('expertise')}")
                print(f"   Website: {obj.get('website')}")
                print(f"   Partner ID: {obj.get('partner_id')}")
                print()
                
                if partner_name in obj.get('name', ''):
                    found = True
                    logger.info(f"Found the partner '{partner_name}' in the Global_Ecosystem collection!")
            
            if not found:
                logger.error(f"Partner '{partner_name}' not found in the Global_Ecosystem collection")
                if not objects:
                    logger.error("No ecosystem partners found in Global_Ecosystem collection")
            
            return found
        else:
            logger.error("No ecosystem partners found in Global_Ecosystem collection")
            return False
            
    except Exception as e:
        logger.error(f"Error verifying ecosystem partner in Weaviate: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    test_add_ecosystem_partner_direct_weaviate()