import asyncio
import json
import logging
import requests
from typing import Dict, Any, List

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_rag_query_api():
    """
    Test the RAG query API endpoint.
    
    This function sends a test query to the /api/v1/rag/query endpoint
    and processes the streaming response.
    """
    # API endpoint
    api_url = "http://localhost:8000/api/v1/rag/query"
    
    # Test queries
    test_queries = [
        "What is SynthDrive RAG Service?",
        "How does the ingestion pipeline work?",
        "What are the key features of the system?"
    ]
    
    # Authorization header
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer test-token"
    }
    
    logger.info("Testing RAG query API endpoint")
    logger.info("Note: If you see 'No reasoning available' or similar messages, it means:")
    logger.info("1. The system may not have any data ingested yet")
    logger.info("2. The query processing pipeline might not be generating reasoning")
    logger.info("3. You may need to ingest some documents first using the ingestion endpoints")
    
    for query in test_queries:
        logger.info(f"\nQuery: {query}")
        
        # Prepare request payload
        payload = {
            "query_str": query,
            "tenant_id": "default",
            "top_k": 5
        }
        
        try:
            # Make the request with stream=True to handle SSE
            response = requests.post(api_url, json=payload, headers=headers, stream=True)
            
            # Check if request was successful
            if response.status_code != 200:
                logger.error(f"Error: Received status code {response.status_code}")
                logger.error(f"Response: {response.text}")
                continue
            
            # Process the streaming response
            logger.info("Streaming response:")
            
            answer = None
            citations = []
            reasoning = None
            synthesis = None
            
            for line in response.iter_lines():
                if line:
                    # SSE format: data: {...}
                    line_text = line.decode('utf-8')
                    if line_text.startswith('data: '):
                        data_json = line_text[6:]  # Remove 'data: ' prefix
                        try:
                            data = json.loads(data_json)
                            
                            # Process different parts of the response
                            if 'answer' in data:
                                answer = data['answer']
                                logger.info(f"Answer: {answer}")
                            
                            if 'citations' in data:
                                citations = data['citations']
                                logger.info(f"Citations: {len(citations)} sources")
                                for i, citation in enumerate(citations):
                                    logger.info(f"  Citation {i+1}:")
                                    logger.info(f"    Source: {citation.get('source', 'Unknown')}")
                                    logger.info(f"    Content: {citation.get('content', '')[:100]}...")
                            
                            if 'reasoning' in data:
                                reasoning = data['reasoning']
                                if reasoning:
                                    logger.info(f"Reasoning: {reasoning[:100]}...")
                                else:
                                    logger.info(f"Reasoning: No reasoning provided.")
                            
                            if 'synthesis' in data:
                                synthesis = data['synthesis']
                                if synthesis:
                                    logger.info(f"Synthesis: {synthesis[:100]}...")
                                else:
                                    logger.info(f"Synthesis: No synthesis provided.")
                            
                            if 'error' in data:
                                logger.error(f"Error in response: {data['error']}")
                            
                        except json.JSONDecodeError as e:
                            logger.error(f"Error decoding JSON: {e}")
                            logger.error(f"Raw data: {data_json}")
            
            logger.info("---")
            
        except Exception as e:
            logger.error(f"Error making request: {str(e)}")
    
    logger.info("\nTest completed")

def test_rag_query_sync():
    """
    Synchronous wrapper for the async test function.
    """
    asyncio.run(test_rag_query_api())

if __name__ == "__main__":
    test_rag_query_sync()