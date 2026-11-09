import weaviate
from neo4j import GraphDatabase
import logging
from src.core.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_weaviate_data():
    try:
        # Initialize Weaviate client
        auth_config = weaviate.auth.AuthApiKey(api_key=settings.WEAVIATE_API_KEY)
        client = weaviate.Client(
            url=settings.WEAVIATE_URL,
            auth_client_secret=auth_config
        )
        
        # Query all documents
        query = client.query.get("Document", ["content", "source", "tenant_id"]).do()
        
        if query and "data" in query and "Get" in query["data"] and "Document" in query["data"]["Get"]:
            documents = query["data"]["Get"]["Document"]
            logger.info(f"\nWeaviate Data ({len(documents)} documents):")
            for doc in documents:
                logger.info(f"Content: {doc.get('content')[:100]}...")
                logger.info(f"Source: {doc.get('source')}")
                logger.info(f"Tenant ID: {doc.get('tenant_id')}\n")
        else:
            logger.info("No documents found in Weaviate")
            
    except Exception as e:
        logger.error(f"Error checking Weaviate data: {str(e)}")

def check_neo4j_data():
    try:
        # Initialize Neo4j client
        driver = GraphDatabase.driver(
            settings.NEO4J_URI,
            auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
        )
        
        with driver.session() as session:
            # Query all documents and relationships
            result = session.run("""
                MATCH (d:Document)
                OPTIONAL MATCH (d)-[r]->(e)
                RETURN d, collect(type(r) + '->' + e.name) as relationships
            """)
            
            logger.info("\nNeo4j Data:")
            for record in result:
                doc = record["d"]
                rels = record["relationships"]
                logger.info(f"Document ID: {doc.get('id')}")
                logger.info(f"Content: {doc.get('content', '')[:100]}...")
                logger.info(f"Relationships: {rels}\n")
                
        driver.close()
            
    except Exception as e:
        logger.error(f"Error checking Neo4j data: {str(e)}")

if __name__ == "__main__":
    logger.info("Checking data in both databases...")
    check_weaviate_data()
    check_neo4j_data()