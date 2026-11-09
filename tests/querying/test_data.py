"""
Sample test data for querying tests.
This data can be used to seed test databases for integration tests.
"""

# Sample documents for vector store
VECTOR_DOCUMENTS = [
    {
        "id": "doc1",
        "content": "Artificial intelligence (AI) is intelligence demonstrated by machines, as opposed to natural intelligence displayed by animals including humans. AI research has been defined as the field of study of intelligent agents, which refers to any system that perceives its environment and takes actions that maximize its chance of achieving its goals.",
        "metadata": {
            "source": "wikipedia",
            "created_at": "2023-01-01T00:00:00Z",
            "author": "Wikipedia Contributors"
        },
        "source": "wikipedia",
        "tenant_id": "default"
    },
    {
        "id": "doc2",
        "content": "Machine learning is a subset of artificial intelligence that focuses on the development of algorithms and statistical models that enable computers to improve their performance on a specific task through experience, without being explicitly programmed.",
        "metadata": {
            "source": "textbook",
            "created_at": "2023-02-01T00:00:00Z",
            "author": "John Smith"
        },
        "source": "textbook",
        "tenant_id": "default"
    },
    {
        "id": "doc3",
        "content": "Deep learning is a subset of machine learning that uses neural networks with multiple layers (hence 'deep') to analyze various factors of data. Deep learning is a key technology behind driverless cars, enabling them to recognize a stop sign or distinguish a pedestrian from a lamppost.",
        "metadata": {
            "source": "research_paper",
            "created_at": "2023-03-01T00:00:00Z",
            "author": "Jane Doe"
        },
        "source": "research_paper",
        "tenant_id": "default"
    },
    {
        "id": "doc4",
        "content": "Natural Language Processing (NLP) is a field of AI that focuses on the interaction between computers and humans through natural language. The ultimate objective of NLP is to enable computers to understand, interpret, and generate human language in a valuable way.",
        "metadata": {
            "source": "blog",
            "created_at": "2023-04-01T00:00:00Z",
            "author": "Tech Blogger"
        },
        "source": "blog",
        "tenant_id": "default"
    },
    {
        "id": "doc5",
        "content": "Supervised learning is a type of machine learning where the algorithm is trained on labeled data. The algorithm learns to map input data to known outputs, allowing it to predict outputs for new, unseen inputs.",
        "metadata": {
            "source": "course_material",
            "created_at": "2023-05-01T00:00:00Z",
            "author": "University Professor"
        },
        "source": "course_material",
        "tenant_id": "default"
    },
    {
        "id": "doc6",
        "content": "Unsupervised learning is a type of machine learning where the algorithm is trained on unlabeled data. The algorithm learns patterns and relationships in the data without explicit guidance, often used for clustering and dimensionality reduction.",
        "metadata": {
            "source": "course_material",
            "created_at": "2023-05-02T00:00:00Z",
            "author": "University Professor"
        },
        "source": "course_material",
        "tenant_id": "default"
    }
]

# Sample entities and relationships for graph database
GRAPH_ENTITIES = [
    {"name": "Artificial Intelligence", "type": "Concept"},
    {"name": "Machine Learning", "type": "Concept"},
    {"name": "Deep Learning", "type": "Concept"},
    {"name": "Natural Language Processing", "type": "Concept"},
    {"name": "Supervised Learning", "type": "Concept"},
    {"name": "Unsupervised Learning", "type": "Concept"},
    {"name": "Neural Networks", "type": "Technology"},
    {"name": "Computer Vision", "type": "Field"},
    {"name": "Reinforcement Learning", "type": "Concept"}
]

GRAPH_RELATIONSHIPS = [
    {"source": "Machine Learning", "target": "Artificial Intelligence", "type": "SUBSET_OF"},
    {"source": "Deep Learning", "target": "Machine Learning", "type": "SUBSET_OF"},
    {"source": "Natural Language Processing", "target": "Artificial Intelligence", "type": "FIELD_OF"},
    {"source": "Supervised Learning", "target": "Machine Learning", "type": "TYPE_OF"},
    {"source": "Unsupervised Learning", "target": "Machine Learning", "type": "TYPE_OF"},
    {"source": "Neural Networks", "target": "Deep Learning", "type": "USED_IN"},
    {"source": "Computer Vision", "target": "Artificial Intelligence", "type": "FIELD_OF"},
    {"source": "Reinforcement Learning", "target": "Machine Learning", "type": "TYPE_OF"}
]

# Sample document-entity relationships
DOCUMENT_ENTITY_RELATIONSHIPS = [
    {"doc_id": "doc1", "entity_name": "Artificial Intelligence"},
    {"doc_id": "doc2", "entity_name": "Machine Learning"},
    {"doc_id": "doc2", "entity_name": "Artificial Intelligence"},
    {"doc_id": "doc3", "entity_name": "Deep Learning"},
    {"doc_id": "doc3", "entity_name": "Machine Learning"},
    {"doc_id": "doc3", "entity_name": "Neural Networks"},
    {"doc_id": "doc4", "entity_name": "Natural Language Processing"},
    {"doc_id": "doc4", "entity_name": "Artificial Intelligence"},
    {"doc_id": "doc5", "entity_name": "Supervised Learning"},
    {"doc_id": "doc5", "entity_name": "Machine Learning"},
    {"doc_id": "doc6", "entity_name": "Unsupervised Learning"},
    {"doc_id": "doc6", "entity_name": "Machine Learning"}
]

# Sample test queries with expected results
TEST_QUERIES = [
    {
        "query": "What is artificial intelligence?",
        "expected_tools": ["vector_search"],
        "expected_sources": ["doc1"],
        "expected_entities": ["Artificial Intelligence"]
    },
    {
        "query": "How are machine learning and deep learning related?",
        "expected_tools": ["vector_search", "graph_traversal"],
        "expected_sources": ["doc2", "doc3"],
        "expected_entities": ["Machine Learning", "Deep Learning"]
    },
    {
        "query": "Explain the difference between supervised and unsupervised learning.",
        "expected_tools": ["vector_search"],
        "expected_sources": ["doc5", "doc6"],
        "expected_entities": ["Supervised Learning", "Unsupervised Learning"]
    },
    {
        "query": "What fields are part of artificial intelligence?",
        "expected_tools": ["graph_traversal"],
        "expected_sources": [],
        "expected_entities": ["Natural Language Processing", "Computer Vision"]
    }
]


def seed_vector_database(weaviate_client):
    """
    Seed the Weaviate vector database with test documents.
    
    Args:
        weaviate_client: The Weaviate client
    """
    for doc in VECTOR_DOCUMENTS:
        # Create embedding for the document
        embedding = weaviate_client.create_embedding(doc["content"])
        
        # Upsert the document with its embedding
        weaviate_client.upsert_vector(
            doc_id=doc["id"],
            content=doc["content"],
            embedding=embedding,
            metadata=doc["metadata"]
        )


def seed_graph_database(neo4j_client):
    """
    Seed the Neo4j graph database with test entities and relationships.
    
    Args:
        neo4j_client: The Neo4j client
    """
    # Add documents to Neo4j
    for doc in VECTOR_DOCUMENTS:
        neo4j_client.add_document(
            document_id=doc["id"],
            content=doc["content"],
            metadata=doc["metadata"]
        )
    
    # Create entity nodes
    tenant_id = "default"
    for entity in GRAPH_ENTITIES:
        neo4j_client.create_graph_nodes(
            doc_id="seed",  # Placeholder document ID
            entities=[entity],
            relationships=[],
            tenant_id=tenant_id
        )
    
    # Create relationships between entities
    for rel in GRAPH_RELATIONSHIPS:
        neo4j_client.create_graph_nodes(
            doc_id="seed",  # Placeholder document ID
            entities=[],
            relationships=[rel],
            tenant_id=tenant_id
        )
    
    # Create document-entity relationships
    for doc_entity in DOCUMENT_ENTITY_RELATIONSHIPS:
        # Find the entity type
        entity_type = next((e["type"] for e in GRAPH_ENTITIES if e["name"] == doc_entity["entity_name"]), "Concept")
        
        # Create the relationship
        neo4j_client.create_graph_nodes(
            doc_id=doc_entity["doc_id"],
            entities=[{"name": doc_entity["entity_name"], "type": entity_type}],
            relationships=[],
            tenant_id=tenant_id
        )