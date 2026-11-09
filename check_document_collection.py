import logging
from src.data_stores.weaviate_client import WeaviateClient

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_document_collection():
    """Check the contents of the Document collection for ecosystem partner data."""
    try:
        # Initialize Weaviate client
        weaviate_client = WeaviateClient()
        
        # Query the Document collection for our new ecosystem partner data
        result = weaviate_client.client.query.get(
            "Document",
            ["content", "metadata", "source", "tenant_id"]
        ).with_where({
            "path": ["content"],
            "operator": "Like",
            "valueText": "Partner name: DataInnovate Solutions*"
        }).with_additional(["id"]).with_limit(10).do()
        
        print(f"Query result for DataInnovate Solutions: {result}")
        
        if result and "data" in result and "Get" in result["data"] and "Document" in result["data"]["Get"]:
            documents = result["data"]["Get"]["Document"]
            logger.info(f"Found {len(documents)} documents in Document collection")
            
            # Look for ecosystem partner data
            for doc in documents:
                content = doc.get("content", "")
                if "Partner name:" in content:
                    logger.info(f"Found ecosystem partner data in Document collection:")
                    logger.info(f"Content: {content}")
                    logger.info(f"Metadata: {doc.get('metadata', '')}")
                    logger.info(f"ID: {doc.get('_additional', {}).get('id', '')}")
        else:
            logger.info("No documents found in Document collection")
    
    except Exception as e:
        logger.error(f"Error checking Document collection: {str(e)}")

if __name__ == "__main__":
    check_document_collection()