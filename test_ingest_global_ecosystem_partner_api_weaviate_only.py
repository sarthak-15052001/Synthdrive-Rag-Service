import requests
import json
import logging
import uuid
import time
from src.data_stores.weaviate_client import WeaviateClient

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_ingest_global_ecosystem_partner_api():
    """Test the /api/v1/rag/ingest/global/ecosystem-partner API endpoint."""
    try:
        # API endpoint
        api_url = "http://localhost:8000/api/v1/rag/ingest/global/ecosystem-partner"
        
        # Sample ecosystem partner data with unique name
        partner_data = {
            "name": f"API Test Partner Inc. {uuid.uuid4().hex[:8]}",
            "bio": "API Test Partner is a leading technology consulting firm specializing in AI integration, cloud migration, and digital transformation services for enterprise clients.",
            "expertise": ["AI Integration", "Cloud Migration", "Digital Transformation", "Enterprise Solutions"],
            "certifications": ["AWS Certified Solutions Architect", "Google Cloud Professional", "Microsoft Azure Expert"],
            "case_studies": "Successfully implemented AI-driven analytics platform for Fortune 500 retail client, resulting in 35% increase in operational efficiency and $2.5M annual cost savings.",
            "website": "https://apitest-example.com",
            "contact_info": "partners@apitest-example.com",
            "budget_tier": "Enterprise",
            "tags": ["AI", "Cloud", "Enterprise", "Digital Transformation"],
            "tenant_id": "global"  # Using global tenant
        }
        
        # API key for authentication - using empty string for local development server
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer "  # Empty token for local development server
        }
        
        # Make the API request
        logger.info(f"Sending request to {api_url}")
        logger.info(f"Request data: {partner_data}")
        response = requests.post(api_url, json=partner_data, headers=headers)
        
        # Check the response
        if response.status_code == 200:
            result = response.json()
            logger.info(f"API request successful: {result}")
            job_id = result.get("job_id")
            logger.info(f"Job ID: {job_id}")
            
            # Wait for processing to complete
            logger.info("Waiting for processing to complete...")
            time.sleep(10)  # Wait 10 seconds for processing
            
            # Verify the partner was added by checking the Global_Ecosystem collection
            verify_ecosystem_partner_in_weaviate(partner_data["name"])
            
            return True
        else:
            logger.error(f"API request failed with status code {response.status_code}: {response.text}")
            return False
    except Exception as e:
        logger.error(f"Error testing ecosystem partner API: {str(e)}")
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
    test_ingest_global_ecosystem_partner_api()