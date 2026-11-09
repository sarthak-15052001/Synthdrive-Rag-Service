from typing import Optional, Dict, Any, Union
from langgraph.graph import StateGraph
from src.ingestion.graph import IngestionGraph
import logging
from langchain_core.runnables import RunnableConfig
from langgraph.graph import StateGraph

from src.ingestion.graph import IngestionGraph, IngestionState
from src.data_stores.weaviate_client import WeaviateClient
from src.data_stores.neo4j_client import Neo4jClient
from src.data_stores.neo4j_graphrag_client import Neo4jGraphRAGClient

logger = logging.getLogger(__name__)

def _create_base_ingestion_graph(
    config: Optional[RunnableConfig] = None,
    graph_type: str = "document",
    use_graphrag: bool = True
) -> Union[StateGraph, IngestionGraph]:
    """
    Helper function to create a base IngestionGraph instance and return its compiled graph.
    """
    # Create a minimal config if none provided
    if config is None:
        config = RunnableConfig({
            "postgres_client": None,
            "weaviate_client": None,
            "neo4j_client": None,
            "neo4j_graphrag_client": None
        })

    graph = IngestionGraph(
        postgres_client=config.get("postgres_client"),
        weaviate_client=config.get("weaviate_client"),
        neo4j_client=config.get("neo4j_client"),
        neo4j_graphrag_client=config.get("neo4j_graphrag_client"),
        use_graphrag=use_graphrag,
        graph_type=graph_type
    )
    
    # Return either the compiled graph for LangSmith or the IngestionGraph instance for API
    return_compiled = config.get("return_compiled", True) if config else True
    return graph.graph if return_compiled else graph

def create_document_ingestion_graph(
    config: RunnableConfig
) -> Union[StateGraph, IngestionGraph]:
    """
    Creates an ingestion graph for general document, URL, and file ingestion.
    """
    logger.info("Creating document ingestion graph.")
    return _create_base_ingestion_graph(
        config,
        graph_type="document"
    )

def create_global_tool_ingestion_graph(
    config: RunnableConfig
) -> Union[StateGraph, IngestionGraph]:
    """
    Creates an ingestion graph for global AI tool ingestion.
    """
    logger.info("Creating global AI tool ingestion graph.")
    return _create_base_ingestion_graph(
        config,
        graph_type="global_tool"
    )

def create_global_learning_resource_ingestion_graph(
    config: RunnableConfig
) -> Union[StateGraph, IngestionGraph]:
    """
    Creates an ingestion graph for global learning resource ingestion.
    """
    logger.info("Creating global learning resource ingestion graph.")
    return _create_base_ingestion_graph(
        config,
        graph_type="global_learning_resource"
    )

def create_global_ecosystem_partner_ingestion_graph(
    config: RunnableConfig
) -> Union[StateGraph, IngestionGraph]:
    """
    Creates an ingestion graph for global ecosystem partner ingestion.
    """
    logger.info("Creating global ecosystem partner ingestion graph.")
    return _create_base_ingestion_graph(
        config,
        graph_type="global_ecosystem_partner"
    )

def create_tenant_file_ingestion_graph(
    config: RunnableConfig
) -> Union[StateGraph, IngestionGraph]:
    """
    Creates an ingestion graph for tenant-specific file ingestion.
    """
    logger.info("Creating tenant file ingestion graph.")
    return _create_base_ingestion_graph(
        config,
        graph_type="tenant_file"
    )

def create_gcs_file_ingestion_graph(
    config: RunnableConfig
) -> Union[StateGraph, IngestionGraph]:
    """
    Creates an ingestion graph for GCS file ingestion.
    """
    logger.info("Creating GCS file ingestion graph.")
    return _create_base_ingestion_graph(
        config,
        graph_type="gcs_file"
    )

def create_no_code_template_ingestion_graph(
    config: RunnableConfig
) -> Union[StateGraph, IngestionGraph]:
    """
    Creates an ingestion graph for no-code template ingestion.
    """
    logger.info("Creating no-code template ingestion graph.")
    return _create_base_ingestion_graph(
        config,
        graph_type="no_code_template"
    )

def create_pre_made_prompt_ingestion_graph(
    config: RunnableConfig
) -> Union[StateGraph, IngestionGraph]:
    """
    Creates an ingestion graph for pre-made prompt ingestion.
    """
    logger.info("Creating pre-made prompt ingestion graph.")
    return _create_base_ingestion_graph(
        config,
        graph_type="pre_made_prompt"
    )