"""
Example usage of Neo4j GraphRAG client.

This script demonstrates how to use the Neo4jGraphRAGClient for:
1. Building knowledge graphs from text
2. Performing hybrid retrieval (vector + graph)
3. Traversing graph relationships
4. Getting entity context

Prerequisites:
- Neo4j 5.x+ running (for vector index support)
- OpenAI API key configured
- Required environment variables set in .env file
"""

import os
import sys
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.data_stores.neo4j_graphrag_client import Neo4jGraphRAGClient
from src.core.config import settings


def main():
    print("=" * 80)
    print("Neo4j GraphRAG Client Example")
    print("=" * 80)
    
    # Check for OpenAI API key
    if not settings.OPENAI_API_KEY or settings.OPENAI_API_KEY == "your-openai-api-key":
        print("\n✗ Error: OpenAI API key not configured")
        print("Please set OPENAI_API_KEY in your .env file")
        return
    
    # Initialize the GraphRAG client
    print("\n1. Initializing Neo4j GraphRAG Client...")
    try:
        client = Neo4jGraphRAGClient(
            uri=settings.NEO4J_URI,
            user=settings.NEO4J_USER,
            password=settings.NEO4J_PASSWORD
        )
        print("✓ GraphRAG client initialized successfully")
    except Exception as e:
        print(f"✗ Failed to initialize GraphRAG client: {e}")
        print("\nMake sure Neo4j 5.x+ is running and credentials are correct in .env file")
        return
    
    # Example document about Python and machine learning
    document_text = """
    Python is a high-level, interpreted programming language created by Guido van Rossum
    in 1991. It emphasizes code readability with significant use of whitespace. Python 
    supports multiple programming paradigms including object-oriented, imperative, and 
    functional programming.
    
    Python has become the dominant language for machine learning and artificial intelligence.
    Popular frameworks like TensorFlow, developed by Google, and PyTorch, developed by 
    Meta (formerly Facebook), are built on Python. These frameworks enable developers to 
    build neural networks and deep learning models efficiently.
    
    Scikit-learn is another important Python library that provides simple and efficient 
    tools for data mining and data analysis. It is built on NumPy, SciPy, and matplotlib,
    making it accessible and reusable in various contexts.
    """
    
    # Build knowledge graph
    print("\n2. Building Knowledge Graph from Document...")
    try:
        doc_id = "python-ml-doc-001"
        tenant_id = "demo-tenant"
        
        result = client.build_knowledge_graph(
            text=document_text,
            doc_id=doc_id,
            metadata={
                "source": "example_document",
                "topic": "Programming and Machine Learning",
                "author": "Demo"
            },
            tenant_id=tenant_id
        )
        
        print(f"✓ Knowledge graph built successfully")
        print(f"  - Extracted {len(result.get('entities', []))} entities")
        print(f"  - Created {len(result.get('relationships', []))} relationships")
        
        # Show some extracted entities
        if result.get('entities'):
            print("\n  Sample entities:")
            for entity in result.get('entities', [])[:5]:
                print(f"    - {entity.get('name', 'Unknown')} ({entity.get('type', 'Unknown')})")
        
    except Exception as e:
        import traceback
        print(f"Error building knowledge graph: {e}")
        print(f"✗ Failed to build knowledge graph: {e}")
        if "OPENAI_API_KEY" in str(e) or "api_key" in str(e).lower():
            print("\nThis error may be related to OpenAI API key configuration.")
            print("Please check that OPENAI_API_KEY is set correctly in your .env file")
        print("\nFull traceback:")
        traceback.print_exc()
        client.close()
        return
    
    # Perform vector search
    print("\n3. Performing Vector Search...")
    try:
        query = "What is Python used for?"
        results = client.search_with_vector(
            query=query,
            top_k=3,
            tenant_id=tenant_id
        )
        
        print(f"✓ Found {len(results)} results using vector search")
        if results:
            print(f"\n  Top result (score: {results[0].get('score', 0):.4f}):")
            content = results[0].get('content', '')
            print(f"  {content[:200]}..." if len(content) > 200 else f"  {content}")
        
    except Exception as e:
        print(f"✗ Vector search failed: {e}")
    
    # Perform hybrid search (vector + graph)
    print("\n4. Performing Hybrid Search (Vector + Graph)...")
    try:
        query = "machine learning frameworks"
        results = client.search_with_hybrid(
            query=query,
            top_k=3,
            tenant_id=tenant_id
        )
        
        print(f"✓ Found {len(results)} results using hybrid search")
        if results:
            result = results[0]
            print(f"\n  Top result:")
            print(f"  - Score: {result.get('score', 0):.4f}")
            print(f"  - Entities: {len(result.get('entities', []))} related entities")
            print(f"  - Related docs: {len(result.get('related_docs', []))} documents")
            
            # Show related entities
            if result.get('entities'):
                print("\n  Related entities:")
                for entity in result.get('entities', [])[:3]:
                    print(f"    - {entity.get('name', 'Unknown')}")
        
    except Exception as e:
        print(f"✗ Hybrid search failed: {e}")
    
    # Get entity context
    print("\n5. Getting Entity Context...")
    try:
        # Try to get context for Python entity
        context = client.get_entity_context(
            entity_name="Python",
            tenant_id=tenant_id
        )
        
        if context:
            print(f"✓ Retrieved context for 'Python' entity")
            print(f"  - Type: {context.get('type', 'Unknown')}")
            print(f"  - Mentioned in {len(context.get('documents', []))} documents")
            print(f"  - Has {len(context.get('relationships', []))} relationships")
            
            # Show some relationships
            if context.get('relationships'):
                print("\n  Sample relationships:")
                for rel in context.get('relationships', [])[:3]:
                    print(f"    - {rel.get('type', 'UNKNOWN')} -> {rel.get('entity', 'Unknown')}")
        else:
            print("  No context found for 'Python' entity (it may not have been extracted)")
        
    except Exception as e:
        print(f"✗ Failed to get entity context: {e}")
    
    # Traverse the graph
    print("\n6. Traversing Graph from Entity...")
    try:
        # Traverse from Python entity
        traversal = client.traverse_graph(
            entity_name="Python",
            max_depth=2,
            tenant_id=tenant_id
        )
        
        if traversal:
            print(f"✓ Found {len(traversal)} connected entities")
            print("\n  Sample connected entities:")
            for item in traversal[:5]:
                print(f"    - {item.get('entity_name', 'Unknown')} "
                      f"({item.get('entity_type', 'Unknown')}) "
                      f"- distance: {item.get('distance', 0)}")
        else:
            print("  No connected entities found")
        
    except Exception as e:
        print(f"✗ Graph traversal failed: {e}")
    
    # Create a custom retriever
    print("\n7. Creating Custom Vector Retriever...")
    try:
        retriever = client.create_vector_retriever(
            index_name="document_embeddings",
            tenant_id=tenant_id
        )
        print("✓ Custom vector retriever created successfully")
        print("  This retriever can be used for specialized vector search operations")
        
    except Exception as e:
        print(f"✗ Failed to create retriever: {e}")
    
    # Cleanup
    print("\n8. Closing Connection...")
    try:
        client.close()
        print("✓ Connection closed successfully")
    except Exception as e:
        print(f"✗ Failed to close connection: {e}")
    
    print("\n" + "=" * 80)
    print("Example completed successfully!")
    print("=" * 80)
    print("\nKey takeaways:")
    print("1. Knowledge graphs are automatically built from text")
    print("2. Hybrid retrieval combines vector similarity with graph relationships")
    print("3. Entity context provides rich information about entities")
    print("4. Graph traversal enables discovery of related information")
    print("\nFor more information, see NEO4J_GRAPHRAG_INTEGRATION.md")


if __name__ == "__main__":
    main()