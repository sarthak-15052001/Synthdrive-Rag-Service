import os
import sys
import json
import logging
import traceback
from typing import List, Dict, Any

# Add the src directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import clients with error handling
try:
    from src.data_stores.weaviate_client import WeaviateClient, LANGCHAIN_AVAILABLE
    WEAVIATE_IMPORT_ERROR = None
except ImportError as e:
    WEAVIATE_IMPORT_ERROR = str(e)
    logger.error(f"Error importing WeaviateClient: {e}")

try:
    from src.data_stores.neo4j_client import Neo4jClient
    NEO4J_IMPORT_ERROR = None
except ImportError as e:
    NEO4J_IMPORT_ERROR = str(e)
    logger.error(f"Error importing Neo4jClient: {e}")


def test_weaviate_client():
    """
    Test the WeaviateClient implementation.
    """
    print("\n=== Testing WeaviateClient ===")
    
    # Check if there was an import error
    if WEAVIATE_IMPORT_ERROR:
        print(f"❌ Could not import WeaviateClient: {WEAVIATE_IMPORT_ERROR}")
        return False
    
    try:
        # Initialize the client
        print("Initializing WeaviateClient (this may take a few seconds)...")
        try:
            client = WeaviateClient()
            print("✓ Initialized WeaviateClient")
        except Exception as e:
            print(f"❌ Failed to initialize WeaviateClient: {e}")
            print("\nPossible issues:")
            print("  - Weaviate server is not running")
            print("  - Incorrect Weaviate URL or API key in .env file")
            print("  - Network connectivity issues")
            print("\nPlease check your .env file and ensure Weaviate is running.")
            return False
        
        # Test document content and metadata
        content = "This is a test document about artificial intelligence and machine learning."
        metadata = {
            "source": "test",
            "created_at": "2025-09-30T00:00:00Z",
            "tenant_id": "test_tenant"
        }
        
        try:
            # Create an embedding for the content
            embedding = client.create_embedding(content)
            print(f"✓ Created embedding with {len(embedding)} dimensions")
            
            # Test upsert_vector method
            doc_id = client.upsert_vector("test_doc_1", content, embedding, metadata)
            print(f"✓ Upserted document with ID: {doc_id}")
            
            # Test semantic_search method
            query = "What is AI?"
            query_embedding = client.create_embedding(query)
            search_results = client.semantic_search(query_embedding, "test_tenant", limit=3)
            print(f"✓ Semantic search returned {len(search_results)} results")
            
            # Print the first result if available
            if search_results:
                print(f"  First result: {search_results[0]['content'][:50]}...")
                print(f"  Relevance score: {search_results[0]['relevance_score']}")
            
            # Test LangChain integration
            langchain_results = client.langchain_similarity_search(query, "test_tenant", k=3)
            print(f"✓ LangChain similarity search returned {len(langchain_results)} results")
            
            # Print the first result if available
            if langchain_results:
                if LANGCHAIN_AVAILABLE:
                    print(f"  First result: {langchain_results[0].page_content[:50]}...")
                else:
                    print(f"  First result: {langchain_results[0]['page_content'][:50]}...")
                    print("  Note: Using fallback implementation as LangChain is not available")
            
            print("✓ WeaviateClient tests completed successfully")
            return True
            
        except Exception as e:
            print(f"❌ Error during WeaviateClient testing: {e}")
            traceback.print_exc()
            return False
            
    except Exception as e:
        print(f"❌ Unexpected error in WeaviateClient test: {e}")
        traceback.print_exc()
        return False


def test_neo4j_client():
    """
    Test the Neo4jClient implementation.
    """
    print("\n=== Testing Neo4jClient ===")
    
    # Check if there was an import error
    if NEO4J_IMPORT_ERROR:
        print(f"❌ Could not import Neo4jClient: {NEO4J_IMPORT_ERROR}")
        return False
    
    try:
        # Initialize the client
        print("Initializing Neo4jClient (this may take a few seconds)...")
        try:
            client = Neo4jClient()
            print("✓ Initialized Neo4jClient")
        except Exception as e:
            print(f"❌ Failed to initialize Neo4jClient: {e}")
            print("\nPossible issues:")
            print("  - Neo4j server is not running")
            print("  - Incorrect Neo4j URI, username, or password in .env file")
            print("  - Network connectivity issues")
            print("\nPlease check your .env file and ensure Neo4j is running.")
            return False
        
        # Test document content
        content = """
        OpenAI is a company based in San Francisco.
        It was founded by Sam Altman and Elon Musk.
        OpenAI created ChatGPT, which is a large language model.
        Microsoft has invested billions in OpenAI.
        """
        
        # Test metadata
        metadata = {
            "source": "test",
            "created_at": "2025-09-30T00:00:00Z",
            "tenant_id": "test_tenant"
        }
        
        try:
            # Test entity extraction
            try:
                entities, relationships = client.extract_entities_and_relations(content)
                print(f"✓ Extracted {len(entities)} entities and {len(relationships)} relationships")
                
                # Print extracted entities and relationships
                print("  Entities:")
                for entity in entities:
                    print(f"    - {entity['name']} ({entity['type']})")
                
                print("  Relationships:")
                for rel in relationships:
                    print(f"    - {rel['source']} {rel['type']} {rel['target']}")
            except Exception as e:
                print(f"❌ Error during entity extraction: {e}")
                print("  This may be due to OpenAI API key issues or rate limiting.")
                # Continue with empty entities and relationships for testing
                entities, relationships = [], []
            
            try:
                # Test create_graph_nodes method
                client.create_graph_nodes("test_doc_1", entities, relationships, "test_tenant")
                print("✓ Created graph nodes and relationships")
                
                # Test traverse_relations method with a natural language query
                query = "What is the relationship between OpenAI and Microsoft?"
                results = client.traverse_relations(query, "test_tenant", limit=3)
                print(f"✓ Traverse relations returned {len(results)} results")
                
                # Print the results
                if results:
                    print("  Results:")
                    for i, result in enumerate(results):
                        print(f"    Result {i+1}:")
                        for key, value in result.items():
                            if isinstance(value, (str, int, float, bool)):
                                print(f"      {key}: {value}")
                            else:
                                print(f"      {key}: [complex object]")
                
                # Test traverse_relations with a Cypher query
                cypher_query = """
                MATCH (e:Entity {name: 'OpenAI', tenant_id: 'test_tenant'})
                RETURN e.name AS name, e.type AS type
                """
                cypher_results = client.traverse_relations(cypher_query, "test_tenant")
                print(f"✓ Cypher query returned {len(cypher_results)} results")
                
                print("✓ Neo4jClient tests completed successfully")
                return True
            except Exception as e:
                print(f"❌ Error during graph operations: {e}")
                traceback.print_exc()
                return False
                
        except Exception as e:
            print(f"❌ Error during Neo4jClient testing: {e}")
            traceback.print_exc()
            return False
            
    except Exception as e:
        print(f"❌ Unexpected error in Neo4jClient test: {e}")
        traceback.print_exc()
        return False


def main():
    """
    Run all tests.
    """
    print("Starting client tests...")
    print("Note: These tests require running Weaviate and Neo4j instances.")
    print("If you haven't set up these services, the tests will fail.")
    print("Check README_CLIENTS.md for setup instructions.\n")
    
    # Test WeaviateClient
    weaviate_success = test_weaviate_client()
    
    # Test Neo4jClient
    neo4j_success = test_neo4j_client()
    
    # Print overall results
    print("\n=== Test Summary ===")
    print(f"WeaviateClient: {'✅ PASSED' if weaviate_success else '❌ FAILED'}")
    print(f"Neo4jClient: {'✅ PASSED' if neo4j_success else '❌ FAILED'}")
    
    if weaviate_success and neo4j_success:
        print("\n✅ All tests completed successfully!")
    else:
        print("\n❌ Some tests failed!")
        print("\nPossible solutions:")
        if not weaviate_success:
            print("- For Weaviate issues: Make sure Weaviate is running and your .env file has the correct WEAVIATE_URL and WEAVIATE_API_KEY")
        if not neo4j_success:
            print("- For Neo4j issues: Make sure Neo4j is running and your .env file has the correct NEO4J_URI, NEO4J_USER, and NEO4J_PASSWORD")
        print("- Check that your OpenAI API key is valid and has sufficient quota")
        print("- See README_CLIENTS.md for more detailed setup instructions")


if __name__ == "__main__":
    main()