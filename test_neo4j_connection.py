from neo4j import GraphDatabase
import os
from dotenv import load_dotenv

def test_connection():
    # Load environment variables
    load_dotenv()
    
    # Get Neo4j connection details
    uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    user = os.getenv("NEO4J_USER", "neo4j")
    password = os.getenv("NEO4J_PASSWORD", "password123")
    
    try:
        # Initialize the driver
        driver = GraphDatabase.driver(uri, auth=(user, password))
        
        # Verify connectivity
        driver.verify_connectivity()
        print("Successfully connected to Neo4j!")
        
        # Close the driver
        driver.close()
        return True
        
    except Exception as e:
        print(f"Failed to connect to Neo4j: {str(e)}")
        return False

if __name__ == "__main__":
    test_connection()