import asyncio
import json
import logging
import requests
from typing import Dict, Any, List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_rag_query_api():
    """
    Test the RAG query API endpoint with GraphRAG features.
    
    This function sends test queries to the /api/v1/rag/query endpoint
    and processes the streaming response.
    """
    # API endpoint
    api_url = "http://localhost:8000/api/v1/rag/query"
    
    # Authorization header
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer test-token"
    }
    
    logger.info("Testing RAG query API endpoint with GraphRAG features")
    logger.info("Note: If you see 'No reasoning available' or similar messages, it means:")
    logger.info("1. The system may not have any data ingested yet")
    logger.info("2. The query processing pipeline might not be generating reasoning")
    logger.info("3. You may need to ingest some documents first using the ingestion endpoints")
    
    # Test cases with different parameters
    test_cases = [
        {
            "name": "Basic query with default parameters",
            "payload": {
                "query_str": "What is SynthDrive RAG Service?",
                "tenant_id": "default",
                "top_k": 5
            }
        },
        {
            "name": "Query with specific filters",
            "payload": {
                "query_str": "How does the ingestion pipeline work?",
                "tenant_id": "default",
                "top_k": 5,
                "filters": {
                    "document_type": "documentation",
                    "tags": ["rag", "ingestion"]
                }
            }
        },
        {
            "name": "Query with higher top_k value",
            "payload": {
                "query_str": "What are the key features of the system?",
                "tenant_id": "default",
                "top_k": 10
            }
        },
        {
            "name": "Query with custom tenant ID",
            "payload": {
                "query_str": "Explain how GraphRAG works in SynthDrive",
                "tenant_id": "custom_tenant",
                "top_k": 5
            }
        },
        {
            "name": "Complex query with multiple filters",
            "payload": {
                "query_str": "How does SynthDrive handle entity extraction and relationship mapping?",
                "tenant_id": "default",
                "top_k": 7,
                "filters": {
                    "document_type": "technical",
                    "tags": ["neo4j", "graph", "entity-extraction"],
                    "author": "SynthDrive Team"
                }
            }
        }
    ]
    
    for test_case in test_cases:
        logger.info(f"\n{'='*60}")
        logger.info(f"TEST CASE: {test_case['name']}")
        logger.info(f"{'='*60}")
        logger.info(f"Query: {test_case['payload']['query_str']}")
        logger.info(f"Parameters: {json.dumps(test_case['payload'], indent=2)}")
        
        try:
            # Make the request with stream=True to handle SSE
            response = requests.post(api_url, json=test_case['payload'], headers=headers, stream=True)
            
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
                                    if 'metadata' in citation and citation['metadata']:
                                        logger.info(f"    Metadata: {citation['metadata']}")
                            
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
            
            logger.info(f"{'='*60}")
            
        except Exception as e:
            logger.error(f"Error making request: {str(e)}")
    
    logger.info("\nTest completed")

def save_sample_payloads():
    """
    Save sample payloads to files for reference and testing.
    """
    sample_payloads = [
        {
            "filename": "basic_query.json",
            "payload": {
                "query_str": "What is SynthDrive RAG Service?",
                "tenant_id": "default",
                "top_k": 5
            }
        },
        {
            "filename": "filtered_query.json",
            "payload": {
                "query_str": "How does the ingestion pipeline work?",
                "tenant_id": "default",
                "top_k": 5,
                "filters": {
                    "document_type": "documentation",
                    "tags": ["rag", "ingestion"]
                }
            }
        },
        {
            "filename": "high_topk_query.json",
            "payload": {
                "query_str": "What are the key features of the system?",
                "tenant_id": "default",
                "top_k": 10
            }
        },
        {
            "filename": "custom_tenant_query.json",
            "payload": {
                "query_str": "Explain how GraphRAG works in SynthDrive",
                "tenant_id": "custom_tenant",
                "top_k": 5
            }
        },
        {
            "filename": "complex_query.json",
            "payload": {
                "query_str": "How does SynthDrive handle entity extraction and relationship mapping?",
                "tenant_id": "default",
                "top_k": 7,
                "filters": {
                    "document_type": "technical",
                    "tags": ["neo4j", "graph", "entity-extraction"],
                    "author": "SynthDrive Team"
                }
            }
        }
    ]
    
    # Create directory for sample payloads
    import os
    os.makedirs("sample_payloads", exist_ok=True)
    
    # Save each payload to a file
    for sample in sample_payloads:
        filepath = os.path.join("sample_payloads", sample["filename"])
        with open(filepath, "w") as f:
            json.dump(sample["payload"], f, indent=2)
        logger.info(f"Saved sample payload to {filepath}")

def test_rag_query_sync():
    """
    Synchronous wrapper for the async test function.
    """
    # Save sample payloads first
    save_sample_payloads()
    
    # Run the tests
    asyncio.run(test_rag_query_api())

if __name__ == "__main__":
    test_rag_query_sync()