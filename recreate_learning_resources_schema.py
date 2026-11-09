#!/usr/bin/env python3
"""
Script to delete and recreate the Global_LearningResources class in Weaviate
with the new JSON-based schema that preserves payload structure.
"""

import logging
from src.data_stores.weaviate_client import WeaviateClient
from src.core.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def recreate_schema():
    """Delete and recreate the Global_LearningResources class"""
    try:
        logger.info("=" * 80)
        logger.info("=== RECREATING GLOBAL_LEARNINGRESOURCES SCHEMA ===")
        logger.info("=" * 80)
        
        # Initialize Weaviate client
        client = WeaviateClient()
        
        # Check if the class exists
        schema = client.client.schema.get()
        existing_classes = [cls.get("class") for cls in schema.get("classes", [])]
        
        logger.info(f"Existing classes: {existing_classes}")
        
        if "Global_LearningResources" in existing_classes:
            logger.info("Found Global_LearningResources class - deleting...")
            
            # Delete the class
            client.client.schema.delete_class("Global_LearningResources")
            logger.info("✓ Successfully deleted Global_LearningResources class")
        else:
            logger.info("Global_LearningResources class doesn't exist yet")
        
        # Recreate the class with new schema
        logger.info("Creating Global_LearningResources class with JSON schema...")
        client._create_global_learning_resources_class()
        logger.info("✓ Successfully created Global_LearningResources class with new schema")
        
        # Verify the new schema
        schema = client.client.schema.get()
        for cls in schema.get("classes", []):
            if cls.get("class") == "Global_LearningResources":
                logger.info("\n✓ Verified new schema properties:")
                for prop in cls.get("properties", []):
                    logger.info(f"  - {prop.get('name')}: {prop.get('dataType')}")
        
        logger.info("\n=" * 80)
        logger.info("=== SCHEMA RECREATION COMPLETED ===")
        logger.info("=" * 80)
        logger.info("\nNext steps:")
        logger.info("1. Test the ingestion API with: python test_learning_resource_fix.py")
        logger.info("2. Verify data structure in Weaviate Cloud Console")
        logger.info("3. Check that nested structures are preserved as JSON")
        logger.info("=" * 80)
        
    except Exception as e:
        logger.error(f"✗ Error recreating schema: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        raise

if __name__ == "__main__":
    recreate_schema()
