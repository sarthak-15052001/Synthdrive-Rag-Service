"""LangGraph Studio entry point for query graph."""
from langchain_core.runnables import RunnableConfig
from langgraph.graph import StateGraph
import logging

from src.querying.graph import QueryGraph

logger = logging.getLogger(__name__)


def create_query_graph(config: RunnableConfig) -> StateGraph:
    """
    Factory function to create the query graph for LangGraph Studio.
    
    Args:
        config: Runtime configuration from LangGraph Studio
        
    Returns:
        The compiled query graph
    """
    # Try to initialize clients, but use None if they fail
    # This allows the graph to load in Studio even without database connections
    postgres_client = None
    weaviate_client = None
    neo4j_client = None
    neo4j_graphrag_client = None
    
    try:
        from src.data_stores.postgres_client import PostgresClient
        postgres_client = PostgresClient()
        logger.info("PostgreSQL client initialized successfully")
    except Exception as e:
        logger.warning(f"Could not initialize PostgreSQL client: {e}")
    
    try:
        from src.data_stores.weaviate_client import WeaviateClient
        weaviate_client = WeaviateClient()
        logger.info("Weaviate client initialized successfully")
    except Exception as e:
        logger.warning(f"Could not initialize Weaviate client: {e}")
    
    try:
        from src.data_stores.neo4j_client import Neo4jClient
        neo4j_client = Neo4jClient()
        logger.info("Neo4j client initialized successfully")
    except Exception as e:
        logger.warning(f"Could not initialize Neo4j client: {e}")
    
    try:
        from src.data_stores.neo4j_graphrag_client import Neo4jGraphRAGClient
        neo4j_graphrag_client = Neo4jGraphRAGClient()
        logger.info("Neo4j GraphRAG client initialized successfully")
    except Exception as e:
        logger.warning(f"Could not initialize Neo4j GraphRAG client: {e}")
    
    # Create graph instance
    graph_instance = QueryGraph(
        postgres_client=postgres_client,
        weaviate_client=weaviate_client,
        neo4j_client=neo4j_client,
        neo4j_graphrag_client=neo4j_graphrag_client,
        use_graphrag=True
    )
    
    # Return the compiled graph
    return graph_instance.graph