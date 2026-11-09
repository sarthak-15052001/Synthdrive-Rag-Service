import requests
import json
import logging
import time

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def ingest_sample_data():
    """
    Ingest sample data into the SynthDrive RAG Service for testing purposes.
    This function ingests multiple documents with different content and metadata
    to ensure comprehensive testing of the RAG query API.
    """
    base_url = "http://localhost:8000/api/v1/rag"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer test-token"
    }
    
    # Sample documents to ingest
    sample_documents = [
        {
            "content": """
            SynthDrive RAG Service is a powerful retrieval-augmented generation system designed to enhance AI applications with accurate, contextual information retrieval. 

            The system combines vector search capabilities with knowledge graph technologies to provide comprehensive and relevant responses to user queries. It features multi-tenant architecture for data isolation, supports various document types, and offers semantic chunking for optimal text processing.

            Key features include:
            1. Hybrid retrieval combining vector search and graph-based knowledge retrieval
            2. Semantic chunking for meaningful text segmentation
            3. Entity extraction and relationship mapping
            4. Multi-tenant data isolation
            5. Support for various document types including PDFs, text files, and structured data
            """,
            "metadata": {
                "source": "SynthDrive Documentation",
                "author": "SynthDrive Team",
                "document_type": "documentation",
                "tags": ["rag", "overview", "features"]
            },
            "tenant_id": "default"
        },
        {
            "content": """
            The ingestion pipeline in SynthDrive RAG Service processes documents through several stages:
            
            1. Document Loading and Parsing: The system accepts various document formats (PDF, DOCX, TXT, etc.) and extracts their text content while preserving structural information.
            
            2. Semantic Chunking: Instead of using arbitrary fixed-size chunks, the system employs AI-powered semantic chunking that respects natural boundaries in the text, such as paragraphs, sections, and topics.
            
            3. Entity Extraction: The system identifies entities (people, organizations, concepts, etc.) within the text and their relationships to each other.
            
            4. Vector Embedding Generation: Each semantic chunk is converted into a vector embedding using state-of-the-art embedding models.
            
            5. Storage: The processed data is stored in both vector databases (Weaviate) for similarity search and graph databases (Neo4j) for relationship queries.
            
            This multi-stage pipeline ensures that documents are processed in a way that maximizes the effectiveness of both vector search and graph-based retrieval.
            """,
            "metadata": {
                "source": "SynthDrive Technical Documentation",
                "author": "SynthDrive Team",
                "document_type": "documentation",
                "tags": ["rag", "ingestion", "pipeline"]
            },
            "tenant_id": "default"
        },
        {
            "content": """
            GraphRAG (Graph-enhanced Retrieval Augmented Generation) is a key innovation in SynthDrive's approach to information retrieval and generation. Unlike traditional RAG systems that rely solely on vector similarity search, GraphRAG incorporates knowledge graph technologies to enhance retrieval with relationship awareness.

            How GraphRAG works in SynthDrive:

            1. Dual Storage: Information is stored in both vector databases (Weaviate) and graph databases (Neo4j).
            
            2. Entity and Relationship Extraction: During ingestion, the system identifies entities and their relationships, creating a knowledge graph.
            
            3. Hybrid Retrieval: When a query is received, the system performs both vector similarity search and graph traversal.
            
            4. Context Enhancement: Graph-based insights are used to enhance the context retrieved from vector search.
            
            5. Relationship-Aware Responses: The final response incorporates both direct content matches and relationship insights.

            This approach allows SynthDrive to answer complex queries that require understanding relationships between entities, multi-hop reasoning, and connecting information across different documents.
            """,
            "metadata": {
                "source": "SynthDrive Architecture Guide",
                "author": "SynthDrive Team",
                "document_type": "technical",
                "tags": ["graphrag", "architecture", "neo4j", "graph"]
            },
            "tenant_id": "default"
        },
        {
            "content": """
            Entity extraction and relationship mapping in SynthDrive is a sophisticated process that forms the foundation of the GraphRAG approach:

            Entity Extraction:
            - Named Entity Recognition (NER): Identifies people, organizations, locations, dates, and other named entities.
            - Concept Extraction: Identifies abstract concepts, technical terms, and domain-specific entities.
            - Custom Entity Detection: Supports custom entity types based on the specific domain.

            Relationship Mapping:
            - Direct Relationships: Identifies explicit relationships mentioned in the text (e.g., "John works for Acme Corp").
            - Co-occurrence Analysis: Establishes potential relationships based on entity co-occurrence patterns.
            - Semantic Role Labeling: Determines the roles entities play in relation to each other.
            - Cross-document Relationships: Connects entities across different documents.

            The extracted entities and relationships are stored in Neo4j, a graph database that allows for efficient storage and querying of complex relationship networks. This graph structure enables:
            - Multi-hop traversals to find indirect connections
            - Relationship-based filtering and ranking
            - Context enrichment for retrieved documents
            - Inference of implicit relationships

            This approach significantly enhances the system's ability to provide contextually rich and accurate responses to complex queries.
            """,
            "metadata": {
                "source": "SynthDrive Technical Specifications",
                "author": "SynthDrive Team",
                "document_type": "technical",
                "tags": ["entity-extraction", "relationship-mapping", "neo4j", "graph"]
            },
            "tenant_id": "default"
        },
        {
            "content": """
            SynthDrive RAG Service uses Neo4j as its graph database for storing and querying knowledge graphs. Neo4j is particularly well-suited for this purpose due to its native graph storage, efficient query capabilities, and support for complex relationship patterns.

            Implementation details:

            1. Graph Schema: SynthDrive implements a flexible graph schema with various node types (Document, Chunk, Entity, Concept) and relationship types (CONTAINS, MENTIONS, RELATES_TO, etc.).

            2. Cypher Queries: The system uses Cypher, Neo4j's query language, to perform complex graph traversals and pattern matching.

            3. Integration with Vector Search: Results from Neo4j are combined with vector search results from Weaviate to provide comprehensive responses.

            4. GraphRAG Client: SynthDrive includes a Neo4jGraphRAGClient that provides specialized methods for building and querying knowledge graphs.

            5. Relationship Weighting: Relationships between entities are weighted based on confidence scores and frequency of co-occurrence.

            6. Multi-hop Reasoning: The system can traverse multiple relationship hops to find indirect connections between entities.

            This implementation allows SynthDrive to leverage the power of graph databases for relationship-aware information retrieval, significantly enhancing the contextual understanding of the system.
            """,
            "metadata": {
                "source": "SynthDrive Implementation Guide",
                "author": "SynthDrive Team",
                "document_type": "technical",
                "tags": ["neo4j", "implementation", "graph", "graphrag"]
            },
            "tenant_id": "default"
        },
        {
            "content": """
            SynthDrive RAG Service offers a multi-tenant architecture that ensures complete data isolation between different tenants. This is crucial for organizations that need to maintain separate knowledge bases for different departments, projects, or clients.

            Key aspects of the multi-tenant implementation:

            1. Tenant Identification: Each request includes a tenant_id parameter that identifies the specific tenant.

            2. Data Isolation: Documents and their derived data (chunks, embeddings, entities) are tagged with the tenant ID.

            3. Query Scoping: All queries are automatically scoped to the specified tenant, ensuring that results only include data from that tenant.

            4. Custom Configurations: Each tenant can have custom configurations for chunking, embedding, and retrieval parameters.

            5. Tenant-specific Collections: In Weaviate, tenant-specific collections ensure physical separation of vector data.

            6. Graph Partitioning: In Neo4j, tenant data is partitioned using tenant properties and constraints.

            This architecture allows SynthDrive to serve multiple clients or departments from a single deployment while maintaining strict data isolation and security.
            """,
            "metadata": {
                "source": "SynthDrive Architecture Guide",
                "author": "SynthDrive Team",
                "document_type": "documentation",
                "tags": ["multi-tenant", "architecture", "data-isolation"]
            },
            "tenant_id": "default"
        },
        {
            "content": """
            GraphRAG is an innovative approach that enhances traditional Retrieval Augmented Generation (RAG) with graph-based knowledge representation and querying. This approach is particularly effective for complex queries that require understanding relationships between entities and concepts.

            In a traditional RAG system, documents are chunked, embedded, and retrieved based on vector similarity to the query. While effective for finding relevant content, this approach has limitations:
            - It treats documents as independent units, missing connections between them
            - It cannot easily answer questions that require connecting information across documents
            - It struggles with relationship-based queries

            GraphRAG addresses these limitations by:
            1. Building a knowledge graph during document ingestion
            2. Extracting entities and their relationships
            3. Connecting information across document boundaries
            4. Enabling relationship-based and multi-hop queries

            When a user queries a GraphRAG system, both vector search and graph traversal are performed. The vector search finds relevant content based on semantic similarity, while the graph traversal uncovers relationships and connections that provide additional context.

            This hybrid approach results in more comprehensive, accurate, and contextually rich responses, especially for complex queries that require understanding relationships between different pieces of information.
            """,
            "metadata": {
                "source": "GraphRAG Whitepaper",
                "author": "SynthDrive Research Team",
                "document_type": "research",
                "tags": ["graphrag", "research", "rag"]
            },
            "tenant_id": "custom_tenant"
        }
    ]
    
    logger.info(f"Ingesting {len(sample_documents)} sample documents for testing")
    
    # Ingest each document
    for i, doc in enumerate(sample_documents):
        logger.info(f"Ingesting document {i+1}/{len(sample_documents)}: {doc['metadata']['source']}")
        
        try:
            # Make the request to ingest the document
            response = requests.post(
                f"{base_url}/ingest/document", 
                json=doc, 
                headers=headers
            )
            
            # Check if the request was successful
            if response.status_code in [200, 202]:
                logger.info(f"Successfully ingested document {i+1}: {response.json()}")
            else:
                logger.error(f"Failed to ingest document {i+1}: {response.text}")
                
        except Exception as e:
            logger.error(f"Error ingesting document {i+1}: {str(e)}")
    
    # Wait for processing to complete
    logger.info("Waiting for document processing to complete (30 seconds)")
    time.sleep(30)
    
    logger.info("Sample data ingestion completed")

if __name__ == "__main__":
    ingest_sample_data()