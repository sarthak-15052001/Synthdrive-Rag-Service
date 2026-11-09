#!/usr/bin/env python3
"""
Script to recreate the Document collection in Weaviate with the fixed schema.
This removes the duplicate fields (source, created_at) that were both in properties 
and inside the metadata JSON.

WARNING: This will delete all existing documents in the Document collection!
Make sure to backup your data before running this script.
"""

import logging
from src.data_stores.weaviate_client import WeaviateClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Recreate the Document collection with the fixed schema."""
    try:
        # Initialize Weaviate client
        logger.info("Connecting to Weaviate...")
        client = WeaviateClient()
        
        # Check if Document class exists
        if client.client.schema.exists("Document"):
            logger.warning("Document collection exists. It will be deleted and recreated.")
            response = input("Are you sure you want to continue? This will delete all documents! (yes/no): ")
            
            if response.lower() != "yes":
                logger.info("Operation cancelled by user.")
                return
            
            # Delete the existing Document class
            logger.info("Deleting existing Document collection...")
            client.client.schema.delete_class("Document")
            logger.info("✓ Document collection deleted successfully")
        
        # Manually create the new Document class with fixed schema
        logger.info("Creating new Document collection with fixed schema...")
        document_class = {
            "class": "Document",
            "description": "A document in the RAG system",
            "vectorizer": "text2vec-openai",
            "moduleConfig": {
                "text2vec-openai": {
                    "model": "ada",
                    "modelVersion": "002",
                    "type": "text"
                }
            },
            "properties": [
                {
                    "name": "content",
                    "description": "The content of the document",
                    "dataType": ["text"],
                    "moduleConfig": {
                        "text2vec-openai": {
                            "skip": False,
                            "vectorizePropertyName": False
                        }
                    }
                },
                {
                    "name": "metadata",
                    "description": "Metadata about the document (JSON string containing all metadata fields)",
                    "dataType": ["text"],
                    "moduleConfig": {
                        "text2vec-openai": {
                            "skip": True
                        }
                    }
                },
                {
                    "name": "tenant_id",
                    "description": "ID of the tenant that owns this document",
                    "dataType": ["string"],
                    "moduleConfig": {
                        "text2vec-openai": {
                            "skip": True
                        }
                    }
                }
            ]
        }
        
        client.client.schema.create_class(document_class)
        logger.info("✓ Document collection created successfully with fixed schema")
        
        # Verify the new schema
        logger.info("\nVerifying new schema...")
        schema = client.client.schema.get("Document")
        properties = [prop["name"] for prop in schema.get("properties", [])]
        logger.info(f"Properties in Document collection: {properties}")
        
        logger.info("\n" + "=" * 80)
        logger.info("✓ SUCCESS: Document collection recreated with fixed schema")
        logger.info("=" * 80)
        logger.info("\nFixed issues:")
        logger.info("  1. Removed duplicate 'source' field (now only in metadata JSON)")
        logger.info("  2. Removed duplicate 'created_at' field (now only in metadata JSON)")
        logger.info("  3. Kept 'tenant_id' at top level for filtering")
        logger.info("\nNew schema properties:")
        logger.info("  - content (text)")
        logger.info("  - metadata (text/JSON) - contains source, created_at, and other metadata")
        logger.info("  - tenant_id (string)")
        logger.info("=" * 80)
        
    except Exception as e:
        logger.error(f"Error recreating Document schema: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        raise

if __name__ == "__main__":
    main()
