import requests
import json
import logging
import time

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_rag_query_direct():
    """
    Test the RAG query API endpoint with direct document ingestion and querying.
    This function:
    1. Ingests a sample document
    2. Waits for processing
    3. Queries the system
    """
    base_url = "http://localhost:8000/api/v1/rag"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer test-token"
    }
    
    # Step 1: Ingest a sample document
    logger.info("Step 1: Ingesting sample document")
    
    ingest_payload = {
        "content": """
        SynthDrive RAG Service is a powerful retrieval-augmented generation system designed to enhance AI applications with accurate, contextual information retrieval. 

        The system combines vector search capabilities with knowledge graph technologies to provide comprehensive and relevant responses to user queries. It features multi-tenant architecture for data isolation, supports various document types, and offers semantic chunking for optimal text processing.

        Key features include:
        1. Hybrid retrieval combining vector search and graph-based knowledge retrieval
        2. Semantic chunking for meaningful text segmentation
        3. Entity extraction and relationship mapping
        4. Multi-tenant data isolation
        5. Support for various document types including PDFs, text files, and structured data

        The ingestion pipeline processes documents through several stages:
        - Document loading and parsing
        - Semantic chunking
        - Entity extraction
        - Vector embedding generation
        - Storage in vector and graph databases
        """,
        "metadata": {
            "source": "SynthDrive Documentation",
            "author": "SynthDrive Team",
            "document_type": "documentation",
            "tags": ["rag", "documentation", "overview"]
        },
        "tenant_id": "default"
    }
    
    try:
        ingest_response = requests.post(
            f"{base_url}/ingest/document", 
            json=ingest_payload, 
            headers=headers
        )
        
        if ingest_response.status_code not in [200, 202]:
            logger.error(f"Document ingestion failed: {ingest_response.text}")
            return False
        
        logger.info(f"Document ingestion response: {ingest_response.json()}")
        
        # Step 2: Wait for processing (this is a simplification, in a real scenario you'd check the status)
        logger.info("Step 2: Waiting for document processing (10 seconds)")
        time.sleep(10)  # Give the system some time to process the document
        
        # Step 3: Query the system
        logger.info("Step 3: Querying the system")
        
        test_queries = [
            "What is SynthDrive RAG Service?",
            "How does the ingestion pipeline work?",
            "What are the key features of the system?"
        ]
        
        for query in test_queries:
            logger.info(f"\nSending query: {query}")
            
            query_payload = {
                "query_str": query,
                "tenant_id": "default",
                "top_k": 5
            }
            
            # Make the request with stream=True to handle SSE
            query_response = requests.post(
                f"{base_url}/query", 
                json=query_payload, 
                headers=headers, 
                stream=True
            )
            
            if query_response.status_code != 200:
                logger.error(f"Query failed: {query_response.text}")
                continue
            
            # Process the streaming response
            logger.info("Streaming response:")
            
            for line in query_response.iter_lines():
                if line:
                    line_text = line.decode('utf-8')
                    if line_text.startswith('data: '):
                        data_json = line_text[6:]  # Remove 'data: ' prefix
                        try:
                            data = json.loads(data_json)
                            
                            # Log the data
                            for key, value in data.items():
                                if key == 'citations' and isinstance(value, list):
                                    logger.info(f"Citations: {len(value)} sources")
                                    for i, citation in enumerate(value):
                                        logger.info(f"  Citation {i+1}:")
                                        logger.info(f"    Source: {citation.get('source', 'Unknown')}")
                                        content = citation.get('content', '')
                                        logger.info(f"    Content: {content[:100]}..." if len(content) > 100 else f"    Content: {content}")
                                else:
                                    if isinstance(value, str) and len(value) > 100:
                                        logger.info(f"{key}: {value[:100]}...")
                                    else:
                                        logger.info(f"{key}: {value}")
                            
                        except json.JSONDecodeError as e:
                            logger.error(f"Error decoding JSON: {e}")
                            logger.error(f"Raw data: {data_json}")
            
            logger.info("---")
        
        logger.info("Test completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error during test: {str(e)}")
        return False

if __name__ == "__main__":
    test_rag_query_direct()