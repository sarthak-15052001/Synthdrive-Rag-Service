from typing import Annotated
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import ValidationError
import logging

from src.core.config import settings
from src.core.security import validate_tenant_access
from src.data_stores.postgres_client import PostgresClient
from src.data_stores.weaviate_client import WeaviateClient
from src.data_stores.neo4j_client import Neo4jClient
from src.data_stores.neo4j_graphrag_client import Neo4jGraphRAGClient
from src.ingestion.graph import IngestionGraph
from src.ingestion.ingestion_pipelines import (
    create_document_ingestion_graph,
    create_global_tool_ingestion_graph,
    create_global_learning_resource_ingestion_graph,
    create_global_ecosystem_partner_ingestion_graph,
    create_tenant_file_ingestion_graph,
    create_gcs_file_ingestion_graph,
    create_no_code_template_ingestion_graph,
)
from src.querying.agent import QueryAgent
from src.querying.graph import QueryGraph
from src.querying.tools.vector_search import VectorSearchTool

# Configure logging
logger = logging.getLogger(__name__)

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/token", auto_error=False)


# Database client dependencies
def get_postgres_client(request: Request) -> PostgresClient:
    """
    Dependency to get the PostgreSQL client.
    """
    return request.app.state.postgres_client


def get_weaviate_client(request: Request) -> WeaviateClient:
    """
    Dependency to get the Weaviate client.
    """
    return request.app.state.weaviate_client


def get_neo4j_client(request: Request) -> Neo4jClient:
    """
    Dependency to get the Neo4j client (legacy).
    """
    return request.app.state.neo4j_client


def get_neo4j_graphrag_client(request: Request) -> Neo4jGraphRAGClient:
    """
    Dependency to get the Neo4j GraphRAG client.
    """
    if hasattr(request.app.state, 'neo4j_graphrag_client'):
        return request.app.state.neo4j_graphrag_client
    return None


# Graph dependencies
def _get_ingestion_graph_internal(
    graph_type: str,
    postgres_client: Annotated[PostgresClient, Depends(get_postgres_client)],
    weaviate_client: Annotated[WeaviateClient, Depends(get_weaviate_client)],
    neo4j_client: Annotated[Neo4jClient, Depends(get_neo4j_client)],
    neo4j_graphrag_client: Annotated[Neo4jGraphRAGClient, Depends(get_neo4j_graphrag_client)],
) -> IngestionGraph:
    """
    Internal function to get a specific type of ingestion graph.
    """
    if graph_type == "document_ingestion_graph":
        return create_document_ingestion_graph(
            config={
                "postgres_client": postgres_client,
                "weaviate_client": weaviate_client,
                "neo4j_client": neo4j_client,
                "neo4j_graphrag_client": neo4j_graphrag_client,
                "return_compiled": False  # Get IngestionGraph instance for API
            }
        )
    elif graph_type == "global_tool_ingestion_graph":
        return create_global_tool_ingestion_graph(
            config={
                "postgres_client": postgres_client,
                "weaviate_client": weaviate_client,
                "neo4j_client": neo4j_client,
                "neo4j_graphrag_client": neo4j_graphrag_client,
                "return_compiled": False  # Get IngestionGraph instance for API
            }
        )
    elif graph_type == "global_learning_resource_ingestion_graph":
        return create_global_learning_resource_ingestion_graph(
            config={
                "postgres_client": postgres_client,
                "weaviate_client": weaviate_client,
                "neo4j_client": neo4j_client,
                "neo4j_graphrag_client": neo4j_graphrag_client,
                "return_compiled": False  # Get IngestionGraph instance for API
            }
        )
    elif graph_type == "global_ecosystem_partner_ingestion_graph":
        return create_global_ecosystem_partner_ingestion_graph(
            config={
                "postgres_client": postgres_client,
                "weaviate_client": weaviate_client,
                "neo4j_client": neo4j_client,
                "neo4j_graphrag_client": neo4j_graphrag_client,
                "return_compiled": False  # Get IngestionGraph instance for API
            }
        )
    elif graph_type == "tenant_file_ingestion_graph":
        return create_tenant_file_ingestion_graph(
            config={
                "postgres_client": postgres_client,
                "weaviate_client": weaviate_client,
                "neo4j_client": neo4j_client,
                "neo4j_graphrag_client": neo4j_graphrag_client,
                "return_compiled": False  # Get IngestionGraph instance for API
            }
        )
    elif graph_type == "gcs_file_ingestion_graph":
        return create_gcs_file_ingestion_graph(
            config={
                "postgres_client": postgres_client,
                "weaviate_client": weaviate_client,
                "neo4j_client": neo4j_client,
                "neo4j_graphrag_client": neo4j_graphrag_client,
                "return_compiled": False  # Get IngestionGraph instance for API
            }
        )
    elif graph_type == "no_code_template_ingestion_graph":
        return create_no_code_template_ingestion_graph(
            config={
                "postgres_client": postgres_client,
                "weaviate_client": weaviate_client,
                "neo4j_client": neo4j_client,
                "neo4j_graphrag_client": neo4j_graphrag_client,
                "return_compiled": False  # Get IngestionGraph instance for API
            }
        )
    else:
        # Default to document ingestion graph if type is not specified or recognized
        logger.warning(f"Unknown ingestion graph type: {graph_type}. Defaulting to document ingestion graph.")
        return create_document_ingestion_graph(
            config={
                "postgres_client": postgres_client,
                "weaviate_client": weaviate_client,
                "neo4j_client": neo4j_client,
                "neo4j_graphrag_client": neo4j_graphrag_client,
                "return_compiled": False  # Get IngestionGraph instance for API
            }
        )

def get_ingestion_graph(graph_type: str):
    """
    Dependency factory to get a specific type of ingestion graph.
    """
    def _get_graph(
        postgres_client: Annotated[PostgresClient, Depends(get_postgres_client)],
        weaviate_client: Annotated[WeaviateClient, Depends(get_weaviate_client)],
        neo4j_client: Annotated[Neo4jClient, Depends(get_neo4j_client)],
        neo4j_graphrag_client: Annotated[Neo4jGraphRAGClient, Depends(get_neo4j_graphrag_client)],
    ) -> IngestionGraph:
        return _get_ingestion_graph_internal(
            graph_type=graph_type,
            postgres_client=postgres_client,
            weaviate_client=weaviate_client,
            neo4j_client=neo4j_client,
            neo4j_graphrag_client=neo4j_graphrag_client
        )
    return _get_graph


def get_query_graph(
    postgres_client: Annotated[PostgresClient, Depends(get_postgres_client)],
    weaviate_client: Annotated[WeaviateClient, Depends(get_weaviate_client)],
    neo4j_client: Annotated[Neo4jClient, Depends(get_neo4j_client)],
    neo4j_graphrag_client: Annotated[Neo4jGraphRAGClient, Depends(get_neo4j_graphrag_client)],
) -> QueryGraph:
    """
    Dependency to get the query graph with GraphRAG support.
    """
    return QueryGraph(
        postgres_client,
        weaviate_client,
        neo4j_client,
        neo4j_graphrag_client=neo4j_graphrag_client,
        use_graphrag=True
    )


def get_query_agent(
    postgres_client: Annotated[PostgresClient, Depends(get_postgres_client)],
    weaviate_client: Annotated[WeaviateClient, Depends(get_weaviate_client)],
    neo4j_client: Annotated[Neo4jClient, Depends(get_neo4j_client)],
) -> QueryAgent:
    """
    Dependency to get the query agent (legacy).
    """
    return QueryAgent(postgres_client, weaviate_client, neo4j_client)


# Vector search tool dependency
def get_vector_search_tool(
    weaviate_client: Annotated[WeaviateClient, Depends(get_weaviate_client)],
) -> VectorSearchTool:
    """
    Dependency to get the vector search tool for AI tools search.
    """
    return VectorSearchTool(weaviate_client=weaviate_client)


# Authentication dependencies
async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)] = None):
    """
    Dependency to get the current authenticated user.
    
    Note: For simplicity, we're allowing unauthenticated access in this implementation.
    In a production environment, you would properly validate the token.
    """
    # For development purposes, allow unauthenticated access
    if token is None:
        logger.warning("Unauthenticated access allowed for development")
        return {"username": "dev_user", "tenant_id": "default_tenant"}
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decode the JWT token
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        
        # Extract tenant_id from token if available, otherwise use username as tenant_id
        tenant_id = payload.get("tenant_id", username)
        
        # In a real application, you would validate the user exists in your database
        # For now, we'll return the username and tenant_id
        return {"username": username, "tenant_id": tenant_id}
    except (JWTError, ValidationError):
        logger.warning("Invalid token, falling back to dev_user")
        return {"username": "dev_user", "tenant_id": "default_tenant"}


def get_tenant_id(current_user: Annotated[dict, Depends(get_current_user)]) -> str:
    """
    Dependency to get the tenant ID for multi-tenancy.
    
    Args:
        current_user: The current authenticated user
        
    Returns:
        The tenant ID
    """
    tenant_id = current_user.get("tenant_id", "default_tenant")
    
    # Log tenant access for audit purposes
    logger.info(f"Tenant access: user={current_user.get('username')}, tenant_id={tenant_id}")
    
    return tenant_id


def validate_tenant_access_dependency(
    tenant_id: Annotated[str, Depends(get_tenant_id)],
    current_user: Annotated[dict, Depends(get_current_user)]
) -> str:
    """
    Dependency to validate tenant access.
    
    Args:
        tenant_id: The tenant ID
        current_user: The current authenticated user
        
    Returns:
        The validated tenant ID
        
    Raises:
        HTTPException: If tenant access validation fails
    """
    # Validate that the user has access to this tenant
    validate_tenant_access(tenant_id, current_user)
    
    return tenant_id