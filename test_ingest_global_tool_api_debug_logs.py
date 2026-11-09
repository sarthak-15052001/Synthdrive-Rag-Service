import requests
import json
import time
import sys
import logging
import os
from src.data_stores.weaviate_client import WeaviateClient

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("global_tool_debug.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def test_ingest_global_tool_api_with_debug():
    """Test the global tool ingestion API endpoint with detailed debugging."""
    logger.info("Starting global tool API test with detailed debugging...")
    
    # Initialize Weaviate client for checking results
    logger.info("Initializing Weaviate client...")
    weaviate_client = WeaviateClient()
    
    # Get initial count of objects in Global_Tools
    logger.info("Getting initial count of objects in Global_Tools...")
    result = weaviate_client.client.query.aggregate("Global_Tools").with_meta_count().do()
    initial_count = 0
    if result and "data" in result and "Aggregate" in result["data"] and "Global_Tools" in result["data"]["Aggregate"]:
        initial_count = result["data"]["Aggregate"]["Global_Tools"][0]["meta"]["count"]
    
    logger.info(f"Initial count of objects in Global_Tools: {initial_count}")
    
    # Create a unique tool name with timestamp
    timestamp = time.time()
    tool_name = f"Debug API Tool {timestamp}"
    
    # Prepare the payload - directly match the GlobalToolIngestionRequest schema
    payload = {
        "tenant_id": "global",
        "name": tool_name,
        "description": "A test tool for API ingestion debugging",
        "use_case": "Debugging the API endpoint",
        "url": "https://example.com/debug-api",
        "category": "Debugging",
        "pricing": "Free",
        "reviews": "No reviews yet",
        "rating": 4.8,
        "tags": ["api", "debug", "test"]
    }
    
    # Print the payload for debugging
    logger.info(f"Request payload: {json.dumps(payload, indent=2)}")
    
    # Send the request to the API
    try:
        logger.info("Sending request to API endpoint...")
        response = requests.post(
            "http://localhost:8000/api/v1/rag/ingest/global/tool",
            json=payload
        )
        
        # Print the response
        logger.info(f"Response status code: {response.status_code}")
        logger.info(f"Response content: {response.text}")
        
        # Check if the request was successful
        if response.status_code == 200:
            logger.info("API request successful!")
            job_id = None
            try:
                response_data = response.json()
                job_id = response_data.get("job_id")
                logger.info(f"Job ID: {job_id}")
            except:
                logger.error("Could not parse response as JSON")
            
            # Wait a moment for the ingestion to complete
            logger.info("Waiting for ingestion to complete...")
            time.sleep(15)  # Increased wait time to ensure ingestion completes
            
            # Now check if the tool was added to Weaviate using the client
            logger.info("Checking if tool was added to Weaviate...")
            result = weaviate_client.client.query.aggregate("Global_Tools").with_meta_count().do()
            new_count = 0
            if result and "data" in result and "Aggregate" in result["data"] and "Global_Tools" in result["data"]["Aggregate"]:
                new_count = result["data"]["Aggregate"]["Global_Tools"][0]["meta"]["count"]
            
            logger.info(f"After API ingestion, Global_Tools has {new_count} objects")
            
            if new_count > initial_count:
                logger.info("API ingestion successful! Object count increased.")
                
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
                logger.error("API ingestion failed! Object count did not increase.")
                
                # Let's try to debug by checking the ingestion logs
                logger.info("\nChecking ingestion logs...")
                
                # Let's try to add a tool directly to see if that works
                logger.info("\nTrying to add a tool directly to Weaviate...")
                direct_tool = {
                    "name": f"Direct Debug Tool {timestamp}",
                    "description": "A test tool added directly via client method for debugging",
                    "use_case": "Debugging the ingestion pipeline",
                    "url": "https://example.com/debug",
                    "category": "Debugging",
                    "pricing": "Free",
                    "reviews": "No reviews yet",
                    "rating": 4.5,
                    "tags": ["test", "debug", "direct"]
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
                        logger.info("Direct addition successful! This suggests an issue with the API endpoint or ingestion pipeline.")
                        
                        # Let's check the ingestion pipeline by examining the source_type and document_type
                        logger.info("\nExamining the ingestion pipeline...")
                        logger.info("API endpoint sets source_type to 'global_tool' and document_type to 'global_tool'")
                        logger.info("Direct client method also uses 'global_tool' for both")
                        logger.info("The issue might be in the async processing of the ingestion pipeline")
                    else:
                        logger.error("Direct addition also failed! This suggests an issue with the Weaviate client or connection.")
                except Exception as e:
                    logger.error(f"Error adding tool directly: {str(e)}")
        else:
            logger.error(f"API request failed with status code: {response.status_code}")
    
    except Exception as e:
        logger.error(f"Error during API test: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    test_ingest_global_tool_api_with_debug()