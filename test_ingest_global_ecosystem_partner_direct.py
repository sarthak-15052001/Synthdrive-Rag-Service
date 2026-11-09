import logging
import asyncio
import uuid
from src.ingestion.graph import IngestionGraph
from src.data_stores.weaviate_client import WeaviateClient

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_ingest_global_ecosystem_partner_direct():
    """Test the ecosystem partner ingestion directly using the ingestion graph."""
    try:
        # Initialize the ingestion graph
        ingestion_graph = IngestionGraph()
        
        # Generate a job ID for tracking
        job_id = str(uuid.uuid4())
        
        # Sample ecosystem partner data with unique name
        partner_name = f"DirectTest Solutions Inc. {uuid.uuid4().hex[:8]}"
        
        # Create content for embedding
        content = f"Partner name: {partner_name}\n"
        content += f"Bio: DirectTest Solutions is a leading technology consulting firm specializing in AI integration, cloud migration, and digital transformation services for enterprise clients.\n"
        content += f"Expertise: AI Integration, Cloud Migration, Digital Transformation, Enterprise Solutions\n"
        content += f"Case studies: Successfully implemented AI-driven analytics platform for Fortune 500 retail client, resulting in 35% increase in operational efficiency and $2.5M annual cost savings.\n"
        
        # Generate a partner ID
        partner_id = str(uuid.uuid4())
        
        # Prepare input data
        input_data = {
            "content": content,
            "metadata": {
                "name": partner_name,
                "bio": "DirectTest Solutions is a leading technology consulting firm specializing in AI integration, cloud migration, and digital transformation services for enterprise clients.",
                "expertise": ["AI Integration", "Cloud Migration", "Digital Transformation", "Enterprise Solutions"],
                "certifications": ["AWS Certified Solutions Architect", "Google Cloud Professional", "Microsoft Azure Expert"],
                "case_studies": "Successfully implemented AI-driven analytics platform for Fortune 500 retail client, resulting in 35% increase in operational efficiency and $2.5M annual cost savings.",
                "website": "https://directtest-example.com",
                "contact_info": "partners@directtest-example.com",
                "budget_tier": "Enterprise",
                "tags": ["AI", "Cloud", "Enterprise", "Digital Transformation"],
                "document_type": "ecosystem_partner",
                "partner_id": partner_id
            },
            "job_id": job_id,
            "source_type": "global_ecosystem_partner"
        }
        
        # Debug logging
        logger.info(f"Input data: {input_data}")
        
        # Start async ingestion
        result = await ingestion_graph.ingest_document_async(
            input_data=input_data,
            tenant_id="global"  # Use global tenant for global knowledge
        )
        
        if isinstance(result, Exception):
            logger.error(f"Error ingesting ecosystem partner: {str(result)}")
            return False
            
        logger.info(f"Ecosystem partner ingestion started with job ID: {job_id}")
        
        # Wait for processing to complete
        logger.info("Waiting for processing to complete...")
        await asyncio.sleep(10)  # Wait 10 seconds for processing
        
        # Verify the partner was added by checking the Global_Ecosystem collection
        verify_ecosystem_partner_in_weaviate(partner_name)
        
        return True
    except Exception as e:
        logger.error(f"Error testing ecosystem partner direct ingestion: {str(e)}")
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
    asyncio.run(test_ingest_global_ecosystem_partner_direct())