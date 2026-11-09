"""
Script to create sample data in Neo4j for testing the Kernel of Truth API.
This script creates entities and relationships that match our test queries.
"""

import logging
import os
import sys
from dotenv import load_dotenv

# Add the project root to the Python path to fix import issues
sys.path.insert(0, os.path.abspath('.'))

# Import the Neo4j client
from src.data_stores.neo4j_client import Neo4jClient

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def create_sample_data():
    """
    Create sample data in Neo4j for testing the Kernel of Truth API.
    """
    logger.info("Creating sample data in Neo4j for testing")
    
    # Initialize Neo4j client
    neo4j_client = Neo4jClient()
    
    # Define the tenant ID
    tenant_id = "default"
    
    try:
        # Define entities and relationships
        entities = [
            # Users
            {"name": "John", "type": "User", "tenant_id": tenant_id},
            {"name": "Alice", "type": "User", "tenant_id": tenant_id},
            {"name": "Bob", "type": "User", "tenant_id": tenant_id},
            
            # Workflows
            {"name": "Workflow X", "type": "Workflow", "tenant_id": tenant_id},
            {"name": "Workflow Y", "type": "Workflow", "tenant_id": tenant_id},
            {"name": "Workflow Z", "type": "Workflow", "tenant_id": tenant_id},
            
            # Meetings
            {"name": "Meeting X", "type": "Meeting", "tenant_id": tenant_id},
            {"name": "Meeting Y", "type": "Meeting", "tenant_id": tenant_id},
            
            # Documents
            {"name": "Document Z", "type": "Document", "tenant_id": tenant_id},
            {"name": "Document Y", "type": "Document", "tenant_id": tenant_id},
            
            # Projects
            {"name": "Project Alpha", "type": "Project", "tenant_id": tenant_id},
            {"name": "Project Beta", "type": "Project", "tenant_id": tenant_id}
        ]
        
        relationships = [
            # John created Workflow Y
            {
                "start_name": "John",
                "end_name": "Workflow Y",
                "relationship_type": "CREATED",
                "tenant_id": tenant_id
            },
            
            # Alice attended Meeting X
            {
                "start_name": "Alice",
                "end_name": "Meeting X",
                "relationship_type": "ATTENDED",
                "tenant_id": tenant_id
            },
            
            # Meeting X used Workflow X
            {
                "start_name": "Meeting X",
                "end_name": "Workflow X",
                "relationship_type": "USED",
                "tenant_id": tenant_id
            },
            
            # Project Alpha used Document Z
            {
                "start_name": "Project Alpha",
                "end_name": "Document Z",
                "relationship_type": "USED",
                "tenant_id": tenant_id
            },
            
            # Bob created Document Y
            {
                "start_name": "Bob",
                "end_name": "Document Y",
                "relationship_type": "CREATED",
                "tenant_id": tenant_id
            },
            
            # Document Y used in Project Beta
            {
                "start_name": "Document Y",
                "end_name": "Project Beta",
                "relationship_type": "USED_IN",
                "tenant_id": tenant_id
            }
        ]
        
        # Use Neo4j session directly to create entities and relationships
        with neo4j_client.driver.session() as session:
            # Create entities
            for entity in entities:
                # Use MERGE to avoid duplicates
                query = """
                MERGE (e:Entity {name: $name, tenant_id: $tenant_id})
                ON CREATE SET e.type = $type
                """
                session.run(query, entity)
                logger.info(f"Created entity: {entity['name']} ({entity['type']})")
            
            # Create relationships
            for rel in relationships:
                # Use MERGE to avoid duplicates
                query = f"""
                MATCH (start:Entity {{name: $start_name, tenant_id: $tenant_id}})
                MATCH (end:Entity {{name: $end_name, tenant_id: $tenant_id}})
                MERGE (start)-[r:{rel['relationship_type']}]->(end)
                """
                session.run(query, rel)
                logger.info(f"Created relationship: {rel['start_name']} {rel['relationship_type']} {rel['end_name']}")
        
        logger.info("Sample data creation completed successfully")
        
    except Exception as e:
        logger.error(f"Error creating sample data: {str(e)}")
        raise

if __name__ == "__main__":
    create_sample_data()