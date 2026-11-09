import pytest
import os
from pathlib import Path

from src.data_stores.postgres_client import PostgresClient
from src.data_stores.weaviate_client import WeaviateClient
from src.data_stores.neo4j_client import Neo4jClient
from src.ingestion.graph import IngestionGraph
from src.core.config import settings


@pytest.fixture(scope="session")
def test_data_dir():
    """Get the path to the test data directory."""
    return Path(__file__).parent


@pytest.fixture(scope="session")
def test_data_path(test_data_dir):
    """Get the path to the test data file."""
    return os.path.join(test_data_dir, "test_data.txt")


@pytest.fixture(scope="session")
def postgres_client():
    """Create a PostgreSQL client for testing."""
    client = PostgresClient(
        host=settings.POSTGRES_HOST,
        port=settings.POSTGRES_PORT,
        user=settings.POSTGRES_USER,
        password=settings.POSTGRES_PASSWORD,
        db=settings.POSTGRES_DB
    )
    return client


@pytest.fixture(scope="session")
def weaviate_client():
    """Create a Weaviate client for testing."""
    client = WeaviateClient(
        url=settings.WEAVIATE_URL,
        api_key=settings.WEAVIATE_API_KEY
    )
    return client


@pytest.fixture(scope="session")
def neo4j_client():
    """Create a Neo4j client for testing."""
    client = Neo4jClient(
        uri=settings.NEO4J_URI,
        user=settings.NEO4J_USER,
        password=settings.NEO4J_PASSWORD
    )
    return client


@pytest.fixture(scope="session")
def ingestion_graph(postgres_client, weaviate_client, neo4j_client):
    """Create an ingestion graph for testing."""
    return IngestionGraph(postgres_client, weaviate_client, neo4j_client)


@pytest.fixture(scope="session")
def test_tenant_id():
    """Get a test tenant ID."""
    return "test_tenant_ingestion"