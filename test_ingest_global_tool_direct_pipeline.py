import logging
import time
import sys
import json
from src.data_stores.weaviate_client import WeaviateClient
from src.ingestion.graph import IngestionGraph
from src.data_stores.postgres_client import PostgresClient
from src.data_stores.neo4j_client import Neo4jClient
from src.core.config import settings

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

async def test_ingest_global_tool_direct_pipeline():
    """Test the global tool ingestion pipeline directly."""
    logger.info("Testing global tool ingestion pipeline directly...")
    
    # Initialize clients
    logger.info("Initializing clients...")
    weaviate_client = WeaviateClient()
    postgres_client = PostgresClient(settings.POSTGRES_URI)
    neo4j_client = Neo4jClient(
        uri=settings.NEO4J_URI,
        user=settings.NEO4J_USER,
        password=settings.NEO4J_PASSWORD
    )
    
    # Initialize ingestion graph
    logger.info("Initializing ingestion graph...")
    ingestion_graph = IngestionGraph(
        postgres_client=postgres_client,
        weaviate_client=weaviate_client,
        neo4j_client=neo4j_client
    )
    
    # Get initial count of objects in Global_Tools
    logger.info("Getting initial count of objects in Global_Tools...")
    result = weaviate_client.client.query.aggregate("Global_Tools").with_meta_count().do()
    initial_count = 0
    if result and "data" in result and "Aggregate" in result["data"] and "Global_Tools" in result["data"]["Aggregate"]:
        initial_count = result["data"]["Aggregate"]["Global_Tools"][0]["meta"]["count"]
    
    logger.info(f"Initial count of objects in Global_Tools: {initial_count}")
    
    # Create a unique tool name with timestamp
    timestamp = time.time()
    tool_name = f"Pipeline Test Tool {timestamp}"
    
    # Prepare the input data for the ingestion pipeline
    # This should match what the API endpoint would create
    input_data = {
        "content": f"Tool name: {tool_name}\nDescription: A test tool for pipeline testing\nUse case: Testing the ingestion pipeline directly\nCategory: Testing",
        "metadata": {
            "name": tool_name,
            "description": "A test tool for pipeline testing",
            "use_case": "Testing the ingestion pipeline directly",
            "url": "https://example.com/pipeline-test",
            "category": "Testing",
            "pricing": "Free",
            "reviews": "No reviews yet",
            "rating": 4.7,
            "tags": ["pipeline", "test", "direct"],
            "document_type": "global_tool"
        },
        "job_id": "test-job-id",
        "source_type": "global_tool"
    }
    
    # Print the input data for debugging
    logger.info(f"Input data: {json.dumps(input_data, indent=2)}")
    
    try:
        # Call the ingestion pipeline directly
        logger.info("Calling ingestion pipeline directly...")
        result = await ingestion_graph.ingest_document_async(
            input_data=input_data,
            tenant_id="global"
        )
        
        # Print the result
        logger.info(f"Ingestion result: {result}")
        
        # Wait a moment for the ingestion to complete
        logger.info("Waiting for ingestion to complete...")
        time.sleep(5)
        
        # Check if the tool was added to Weaviate
        logger.info("Checking if tool was added to Weaviate...")
        result = weaviate_client.client.query.aggregate("Global_Tools").with_meta_count().do()
        new_count = 0
        if result and "data" in result and "Aggregate" in result["data"] and "Global_Tools" in result["data"]["Aggregate"]:
            new_count = result["data"]["Aggregate"]["Global_Tools"][0]["meta"]["count"]
        
        logger.info(f"After direct pipeline ingestion, Global_Tools has {new_count} objects")
        
        if new_count > initial_count:
            logger.info("Direct pipeline ingestion successful! Object count increased.")
            
            # Try to find our specific tool by name
            logger.info(f"Searching for tool with name: {tool_name}")
            get_result = weaviate_client.client.query.get(
                "Global_Tools", 
                ["name", "description", "use_case", "url", "category", "tool_id"]
            ).with_additional(["id"]).with_limit(20).do()
            
            if get_result and "data" in get_result and "Get" in get_result["data"] and "Global_Tools" in get_result["data"]["Get"]:
                objects = get_result["data"]["Get"]["Global_Tools"]
                found = False
                
                for obj in objects:
                    if obj.get("name") == tool_name:
                        found = True
                        logger.info(f"Found our tool! Details:")
                        logger.info(f"  Name: {obj.get('name')}")
                        logger.info(f"  Description: {obj.get('description')}")
                        logger.info(f"  Use Case: {obj.get('use_case')}")
                        logger.info(f"  URL: {obj.get('url')}")
                        logger.info(f"  Category: {obj.get('category')}")
                        logger.info(f"  Tool ID: {obj.get('tool_id')}")
                        logger.info(f"  Weaviate ID: {obj.get('_additional', {}).get('id')}")
                        break
                
                if not found:
                    logger.warning("Could not find our specific tool in the collection.")
                    logger.info("Here are the most recent tools in the collection:")
                    for i, obj in enumerate(objects[-5:]):  # Show the last 5 tools
                        logger.info(f"{i+1}. {obj.get('name')} (ID: {obj.get('_additional', {}).get('id')})")
            else:
                logger.error("Could not retrieve tools from Global_Tools collection.")
        else:
            logger.error("Direct pipeline ingestion failed! Object count did not increase.")
            
            # Let's try to add a tool directly to see if that works
            logger.info("\nTrying to add a tool directly to Weaviate...")
            direct_tool = {
                "name": f"Direct Test Tool {timestamp}",
                "description": "A test tool added directly via client method",
                "use_case": "Testing direct tool addition",
                "url": "https://example.com/test",
                "category": "Testing",
                "pricing": "Free",
                "reviews": "No reviews yet",
                "rating": 4.5,
                "tags": ["test", "direct"]
            }
            
            try:
                tool_id = weaviate_client.add_global_tool(direct_tool, tenant_id="global")
                logger.info(f"Successfully added tool directly with ID: {tool_id}")
                
                # Check if the count increased
                result = weaviate_client.client.query.aggregate("Global_Tools").with_meta_count().do()
                direct_count = 0
                if result and "data" in result and "Aggregate" in result["data"] and "Global_Tools" in result["data"]["Aggregate"]:
                    direct_count = result["data"]["Aggregate"]["Global_Tools"][0]["meta"]["count"]
                
                logger.info(f"After direct addition, Global_Tools has {direct_count} objects")
                
                if direct_count > new_count:
                    logger.info("Direct addition successful! This suggests an issue with the ingestion pipeline.")
                else:
                    logger.error("Direct addition also failed! This suggests an issue with the Weaviate client or connection.")
            except Exception as e:
                logger.error(f"Error adding tool directly: {str(e)}")
    
    except Exception as e:
        logger.error(f"Error during direct pipeline test: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_ingest_global_tool_direct_pipeline())