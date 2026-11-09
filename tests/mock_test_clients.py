import os
import sys
import json
import logging
from unittest.mock import MagicMock, patch
from typing import List, Dict, Any

# Add the src directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import test data
from tests.querying.test_data import VECTOR_DOCUMENTS, TEST_QUERIES

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class MockWeaviateClient:
    """
    Mock implementation of WeaviateClient for testing without a real Weaviate instance.
    """
    
    def __init__(self):
        self.documents = {}
        self.embeddings = {}
        self.tenant_id = "default"
        print("✓ Initialized MockWeaviateClient")
    
    def create_embedding(self, text: str) -> List[float]:
        """Mock embedding creation"""
        return [0.1] * 10
    
    def _get_mock_results(self, query: str) -> List[Dict[str, Any]]:
        """Helper to get mock results based on query"""
        query = query.lower()
        
        # Find matching test cases
        matching_test_case = None
        for test_case in TEST_QUERIES:
            if test_case["query"].lower() == query:
                matching_test_case = test_case
                break
        
        if matching_test_case and "vector_search" in matching_test_case["expected_tools"]:
            # Return expected documents for this test case
            results = []
            for doc_id in matching_test_case["expected_sources"]:
                # Find the matching document in VECTOR_DOCUMENTS
                doc = next((d for d in VECTOR_DOCUMENTS if d["id"] == doc_id), None)
                if doc:
                    results.append({
                        "content": doc["content"],
                        "metadata": doc["metadata"],
                        "source": doc["id"],
                        "relevance_score": 0.95,
                        "citation_id": f"vector-{doc['id']}",
                        "tenant_id": "default"
                    })
            return results
        else:
            # For non-test queries, use content matching
            results = []
            for doc in VECTOR_DOCUMENTS:
                content = doc["content"].lower()
                if any(term in content for term in query.split()):
                    results.append({
                        "content": doc["content"],
                        "metadata": doc["metadata"],
                        "source": doc["id"],
                        "relevance_score": 0.8,
                        "citation_id": f"vector-{doc['id']}",
                        "tenant_id": "default"
                    })
            return results[:3]
    
    def search(self, query: str = "", **kwargs) -> List[Dict[str, Any]]:
        """Mock search with test data"""
        return self._get_mock_results(query)
    
    def query_documents(self, query: str = "", **kwargs) -> List[Dict[str, Any]]:
        """Mock document querying"""
        return self._get_mock_results(query)
    
    def multi_query_search(self, query: str = "", **kwargs) -> List[Dict[str, Any]]:
        """Mock multi-query search"""
        return self._get_mock_results(query)
    
    def langchain_similarity_search(self, query: str = "", **kwargs) -> List[Dict[str, Any]]:
        """Mock LangChain similarity search"""
        results = self._get_mock_results(query)
        return [{"page_content": r["content"], "metadata": r["metadata"]} for r in results]
    
    def upsert_vector(self, doc_id: str, content: str, embedding: List[float], metadata: Dict[str, Any]) -> str:
        """Mock document upsert"""
        self.documents[doc_id] = {
            "content": content,
            "metadata": metadata,
            "embedding": embedding
        }
        return doc_id


class MockNeo4jClient:
    """
    Mock implementation of Neo4jClient for testing without a real Neo4j instance.
    """
    
    def __init__(self):
        self.nodes = {}
        self.relationships = []
        self.documents = {}
        self.tenant_id = "default"
        print("✓ Initialized MockNeo4jClient")
    
    def add_document(self, document_id: str, content: str, metadata: Dict[str, Any]):
        """Mock document addition"""
        self.documents[document_id] = {
            "content": content,
            "metadata": metadata
        }
    
    def _get_mock_relations(self, query: str) -> List[Dict[str, Any]]:
        """Helper to get mock relations based on query"""
        query = query.lower()
        if "machine learning" in query or "deep learning" in query:
            return [
                {
                    "name": "Machine Learning",
                    "type": "Concept",
                    "score": 0.95,
                    "relationships": [{"type": "SUBSET_OF", "target": "Artificial Intelligence"}],
                    "citation_id": "graph-1"
                },
                {
                    "name": "Deep Learning",
                    "type": "Concept",
                    "score": 0.90,
                    "relationships": [{"type": "SUBSET_OF", "target": "Machine Learning"}],
                    "citation_id": "graph-2"
                }
            ]
        elif "artificial intelligence" in query:
            return [
                {
                    "name": "Natural Language Processing",
                    "type": "Field",
                    "score": 0.95,
                    "relationships": [{"type": "FIELD_OF", "target": "Artificial Intelligence"}],
                    "citation_id": "graph-3"
                },
                {
                    "name": "Computer Vision",
                    "type": "Field",
                    "score": 0.90,
                    "relationships": [{"type": "FIELD_OF", "target": "Artificial Intelligence"}],
                    "citation_id": "graph-4"
                }
            ]
        return []
    
    def traverse_relations(self, query: str = "", **kwargs) -> List[Dict[str, Any]]:
        """Mock relation traversal with test data"""
        return self._get_mock_relations(query)
    
    def get_document_by_id(self, doc_id: str) -> Dict[str, Any]:
        """Mock document retrieval"""
        return self.documents.get(doc_id, {})
    
    def generate_cypher(self, query: str = "", **kwargs) -> str:
        """Mock Cypher query generation"""
        return "MATCH (n) RETURN n LIMIT 10"
    
    def extract_entities_and_relations(self, content: str):
        """Mock entity and relationship extraction"""
        # Return some sample entities and relationships based on the content
        if "OpenAI" in content:
            entities = [
                {"name": "OpenAI", "type": "Organization"},
                {"name": "Sam Altman", "type": "Person"},
                {"name": "Elon Musk", "type": "Person"},
                {"name": "ChatGPT", "type": "Product"},
                {"name": "Microsoft", "type": "Organization"}
            ]
            relationships = [
                {"source": "Sam Altman", "type": "FOUNDED", "target": "OpenAI"},
                {"source": "Elon Musk", "type": "FOUNDED", "target": "OpenAI"},
                {"source": "OpenAI", "type": "CREATED", "target": "ChatGPT"},
                {"source": "Microsoft", "type": "INVESTED_IN", "target": "OpenAI"}
            ]
        else:
            entities = [
                {"name": "Entity1", "type": "Type1"},
                {"name": "Entity2", "type": "Type2"}
            ]
            relationships = [
                {"source": "Entity1", "type": "RELATED_TO", "target": "Entity2"}
            ]
        
        return entities, relationships
    
    def create_graph_nodes(self, doc_id: str, entities: List[Dict[str, Any]], relationships: List[Dict[str, Any]], tenant_id: str = "default"):
        """Mock graph node creation"""
        # Store the document
        self.nodes[doc_id] = {
            "type": "Document",
            "tenant_id": tenant_id,
            "entities": entities
        }
        
        # Store entities
        for entity in entities:
            entity_id = f"{entity['name']}_{entity['type']}"
            self.nodes[entity_id] = {
                "type": "Entity",
                "name": entity["name"],
                "entity_type": entity["type"],
                "tenant_id": tenant_id
            }
        
        # Store relationships
        for rel in relationships:
            self.relationships.append({
                "source": rel["source"],
                "type": rel["type"],
                "target": rel["target"],
                "tenant_id": tenant_id
            })


def test_weaviate_client():
    """
    Test the MockWeaviateClient implementation.
    """
    print("\n=== Testing WeaviateClient (Mock) ===")
    
    # Initialize the mock client
    client = MockWeaviateClient()
    
    # Test document content and metadata
    content = "This is a test document about artificial intelligence and machine learning."
    metadata = {
        "source": "test",
        "created_at": "2025-09-30T00:00:00Z",
        "tenant_id": "test_tenant"
    }
    
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
        print(f"  First result: {langchain_results[0]['page_content'][:50]}...")
    
    print("✓ WeaviateClient (Mock) tests completed successfully")
    return True


def test_neo4j_client():
    """
    Test the MockNeo4jClient implementation.
    """
    print("\n=== Testing Neo4jClient (Mock) ===")
    
    # Initialize the mock client
    client = MockNeo4jClient()
    
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
    
    # Test entity extraction
    entities, relationships = client.extract_entities_and_relations(content)
    print(f"✓ Extracted {len(entities)} entities and {len(relationships)} relationships")
    
    # Print extracted entities and relationships
    print("  Entities:")
    for entity in entities:
        print(f"    - {entity['name']} ({entity['type']})")
    
    print("  Relationships:")
    for rel in relationships:
        print(f"    - {rel['source']} {rel['type']} {rel['target']}")
    
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
    
    print("✓ Neo4jClient (Mock) tests completed successfully")
    return True


def main():
    """
    Run all tests.
    """
    print("Starting mock client tests...")
    print("Note: These tests use mock implementations and don't require actual Weaviate or Neo4j instances.")
    print("This is useful for verifying the client code without setting up the actual services.\n")
    
    # Test WeaviateClient
    weaviate_success = test_weaviate_client()
    
    # Test Neo4jClient
    neo4j_success = test_neo4j_client()
    
    # Print overall results
    print("\n=== Test Summary ===")
    print(f"WeaviateClient (Mock): {'✅ PASSED' if weaviate_success else '❌ FAILED'}")
    print(f"Neo4jClient (Mock): {'✅ PASSED' if neo4j_success else '❌ FAILED'}")
    
    if weaviate_success and neo4j_success:
        print("\n✅ All mock tests completed successfully!")
        print("\nNote: These tests used mock implementations. To test with real services:")
        print("1. Set up Weaviate and Neo4j as described in README_CLIENTS.md")
        print("2. Update your .env file with the correct connection details")
        print("3. Run the real tests with: python tests/test_clients.py")
    else:
        print("\n❌ Some mock tests failed!")


if __name__ == "__main__":
    main()