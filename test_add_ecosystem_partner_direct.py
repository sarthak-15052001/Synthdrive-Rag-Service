import logging
from src.data_stores.weaviate_client import WeaviateClient

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_add_ecosystem_partner_direct():
    """Test adding an ecosystem partner directly to the Global_Ecosystem collection."""
    try:
        # Initialize Weaviate client
        weaviate_client = WeaviateClient()
        
        # Sample ecosystem partner data
        partner_data = {
            "name": "DirectTest Solutions Inc.",
            "bio": "DirectTest Solutions is a leading technology consulting firm specializing in AI integration, cloud migration, and digital transformation services for enterprise clients.",
            "expertise": ["AI Integration", "Cloud Migration", "Digital Transformation", "Enterprise Solutions"],
            "certifications": ["AWS Certified Solutions Architect", "Google Cloud Professional", "Microsoft Azure Expert"],
            "case_studies": "Successfully implemented AI-driven analytics platform for Fortune 500 retail client, resulting in 35% increase in operational efficiency and $2.5M annual cost savings.",
            "website": "https://directtest-example.com",
            "contact_info": "partners@directtest-example.com",
            "budget_tier": "Enterprise",
            "tags": ["AI", "Cloud", "Enterprise", "Digital Transformation"],
            "tenant_id": "global"  # Using global tenant
        }
        
        # Add the ecosystem partner directly
        partner_id = weaviate_client.add_ecosystem_partner(partner_data, tenant_id="global")
        
        logger.info(f"Successfully added ecosystem partner with ID: {partner_id}")
        
        # Verify the partner was added by checking the Global_Ecosystem collection
        try:
            result = weaviate_client.client.query.get(
                "Global_Ecosystem", 
                ["name", "bio", "expertise", "website", "partner_id"]
            ).with_additional(["id"]).with_limit(10).do()
            
            if result and "data" in result and "Get" in result["data"] and "Global_Ecosystem" in result["data"]["Get"]:
                objects = result["data"]["Get"]["Global_Ecosystem"]
                print(f"\nEcosystem Partners in Global_Ecosystem collection:")
                for i, obj in enumerate(objects):
                    print(f"{i+1}. {obj.get('name')} (ID: {obj.get('_additional', {}).get('id')})")
                    print(f"   Bio: {obj.get('bio')[:100]}...")
                    print(f"   Expertise: {obj.get('expertise')}")
                    print(f"   Website: {obj.get('website')}")
                    print(f"   Partner ID: {obj.get('partner_id')}")
                    print()
                
                if not objects:
                    print("No ecosystem partners found in Global_Ecosystem collection")
            else:
                print("No ecosystem partners found in Global_Ecosystem collection")
                
        except Exception as e:
            logger.error(f"Error verifying ecosystem partner: {str(e)}")
        
        return True
    except Exception as e:
        logger.error(f"Error adding ecosystem partner directly: {str(e)}")
        return False

if __name__ == "__main__":
    test_add_ecosystem_partner_direct()