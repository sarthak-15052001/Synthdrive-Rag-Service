import requests
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def ingest_sample_document():
    """
    Ingest a sample document to the RAG system to demonstrate how to populate it with data.
    This will help ensure the query endpoint can return meaningful responses.
    """
    # API endpoint
    api_url = "http://localhost:8000/api/v1/rag/ingest/document"
    
    # Authorization header
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer test-token"
    }
    
    # Sample document content about SynthDrive RAG Service
    sample_document = {
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
    
    logger.info("Ingesting sample document about SynthDrive RAG Service")
    
    try:
        # Make the request
        response = requests.post(api_url, json=sample_document, headers=headers)
        
        # Check if request was successful
        if response.status_code == 200 or response.status_code == 202:
            logger.info("Document ingestion request successful")
            logger.info(f"Response: {response.json()}")
            logger.info("Now you can try querying the system with the test scripts")
            logger.info("Note: It may take a moment for the document to be fully processed")
            return True
        else:
            logger.error(f"Error: Received status code {response.status_code}")
            logger.error(f"Response: {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"Error making request: {str(e)}")
        return False

if __name__ == "__main__":
    ingest_sample_document()