import pytest
import asyncio
from unittest.mock import MagicMock, patch
from tests.mock_test_clients import MockWeaviateClient, MockNeo4jClient
from src.querying.agent import QueryAgent
from src.querying.graph import QueryGraph
from tests.querying.test_data import seed_vector_database, seed_graph_database, TEST_QUERIES

# These tests now use mock clients, so we don't need to skip them


@pytest.fixture(scope="module")
def weaviate_client():
    """Create a mock Weaviate client for testing."""
    client = MockWeaviateClient()
    yield client


@pytest.fixture(scope="module")
def neo4j_client():
    """Create a mock Neo4j client for testing."""
    client = MockNeo4jClient()
    yield client


@pytest.fixture(scope="module")
def postgres_client():
    """Create a mock PostgreSQL client for testing."""
    client = MagicMock()
    yield client


@pytest.fixture(scope="module")
def seeded_databases(weaviate_client, neo4j_client):
    """Seed the databases with test data."""
    # Seed Weaviate
    seed_vector_database(weaviate_client)
    
    # Seed Neo4j
    seed_graph_database(neo4j_client)
    
    return True


@pytest.fixture(scope="module")
@patch('src.querying.graph.OpenAI')
def query_graph(mock_openai, weaviate_client, neo4j_client, postgres_client, seeded_databases):
    """Create a QueryGraph instance with mock clients."""
    # Configure mock OpenAI
    mock_openai_instance = MagicMock()
    mock_completion = MagicMock()
    mock_completion.choices = [MagicMock()]
    mock_completion.choices[0].message.content = '{"steps": ["Use vector search", "Use graph traversal"]}'
    mock_openai_instance.chat.completions.create.return_value = mock_completion
    mock_openai.return_value = mock_openai_instance
    
    return QueryGraph(
        postgres_client=postgres_client,
        weaviate_client=weaviate_client,
        neo4j_client=neo4j_client
    )


@pytest.fixture(scope="module")
@patch('src.querying.agent.OpenAI')
def query_agent(mock_openai, weaviate_client, neo4j_client, postgres_client, seeded_databases):
    """Create a QueryAgent instance with mock clients."""
    # Configure mock OpenAI
    mock_openai_instance = MagicMock()
    mock_completion = MagicMock()
    mock_completion.choices = [MagicMock()]
    mock_completion.choices[0].message.content = '{"action": "finish"}'
    mock_openai_instance.chat.completions.create.return_value = mock_completion
    mock_openai.return_value = mock_openai_instance
    
    agent = QueryAgent(
        postgres_client=postgres_client,
        weaviate_client=weaviate_client,
        neo4j_client=neo4j_client
    )
    
    # Mock the graph.ainvoke method
    async def mock_ainvoke(state):
        return {
            "query": state["query"],
            "answer": "This is a mock answer",
            "citations": [{"id": "doc1", "source": "test", "content": "Test content"}],
            "reasoning": "Mock reasoning"
        }
    
    agent.graph.ainvoke = mock_ainvoke
    return agent


def test_query_graph_integration(query_graph):
    """Test QueryGraph integration with mock databases."""
    for test_case in TEST_QUERIES:
        query = test_case["query"]
        expected_tools = test_case["expected_tools"]
        expected_sources = test_case["expected_sources"]
        
        result = query_graph.query(query)
        
        # Basic structure checks
        assert result is not None
        assert "query" in result
        assert "answer" in result
        assert "sources" in result
        assert "reasoning" in result
        assert "synthesis" in result
        assert result["query"] == query
        assert isinstance(result["answer"], str)
        
        # Check if we got results when expected
        if expected_tools:
            assert result["answer"] != "I apologize, but I don't have enough information in my knowledge base to provide a complete answer to this question."
            
            # Verify sources are present when expected
            if expected_sources:
                assert len(result["sources"]) > 0
                result_sources = [source.get("source", "").split("/")[-1] for source in result["sources"]]
                for expected_source in expected_sources:
                    assert any(source == expected_source for source in result_sources), \
                        f"Expected source {expected_source} not found in results. Got {result_sources}"


def test_query_agent_integration(query_agent):
    """Test QueryAgent integration with mock databases."""
    for test_case in TEST_QUERIES:
        query = test_case["query"]
        
        result = query_agent.query(query)
        
        assert result is not None
        assert "query" in result
        assert "answer" in result
        assert "sources" in result
        assert result["query"] == query
        assert result["answer"] == "This is a mock answer"
        assert len(result["sources"]) == 1
        assert result["sources"][0]["id"] == "doc1"


@patch('src.querying.tools.vector_search.OpenAI')
@pytest.mark.asyncio
async def test_vector_search_integration(mock_openai, weaviate_client, seeded_databases):
    """Test vector search integration with mock Weaviate."""
    # Configure mock OpenAI
    mock_openai_instance = MagicMock()
    mock_completion = MagicMock()
    mock_completion.choices = [MagicMock()]
    mock_completion.choices[0].message.content = '{"queries": ["test query", "alternative query"]}'
    mock_openai_instance.chat.completions.create.return_value = mock_completion
    mock_openai.return_value = mock_openai_instance
    from src.querying.tools.vector_search import VectorSearchTool
    
    tool = VectorSearchTool(weaviate_client)
    
    for test_case in TEST_QUERIES:
        query = test_case["query"]
        
        result = await tool.search(query)
        
        assert result is not None
        assert isinstance(result, list)
        
        # If vector search is expected for this query
        if "vector_search" in test_case["expected_tools"]:
            assert len(result) > 0
            
            # Check that expected sources are in the results
            result_sources = [doc.get("source") for doc in result]
            for expected_source in test_case["expected_sources"]:
                # Check if the expected source ID is in the results
                assert any(source == expected_source for source in result_sources), \
                    f"Expected source {expected_source} not found in results. Got {result_sources}"


@patch('src.querying.tools.graph_retrieval.OpenAI')
def test_graph_traversal_integration(mock_openai, neo4j_client, seeded_databases):
    """Test graph traversal integration with mock Neo4j."""
    # Configure mock OpenAI
    mock_openai_instance = MagicMock()
    mock_completion = MagicMock()
    mock_completion.choices = [MagicMock()]
    mock_completion.choices[0].message.content = '{"entities": ["Entity1", "Entity2"]}'
    mock_openai_instance.chat.completions.create.return_value = mock_completion
    mock_openai.return_value = mock_openai_instance
    from src.querying.tools.graph_retrieval import GraphRetrievalTool
    
    tool = GraphRetrievalTool(neo4j_client)
    
    for test_case in TEST_QUERIES:
        query = test_case["query"]
        
        # Only test queries that are expected to use graph traversal
        if "graph_traversal" in test_case["expected_tools"]:
            result = asyncio.run(tool.traverse_relations(query))
            
            assert result is not None
            assert isinstance(result, list)
            
            # Check that expected entities are in the results
            # This is a simplified check - in a real test, you'd have more specific assertions
            result_text = str(result)
            for expected_entity in test_case["expected_entities"]:
                assert expected_entity in result_text


def test_end_to_end_integration(query_agent, seeded_databases):
    """Test end-to-end integration with mock components."""
    query = "How are machine learning and deep learning related, and what are their applications?"
    
    result = query_agent.query(query)
    
    assert result is not None
    assert "query" in result
    assert "answer" in result
    assert "sources" in result
    
    assert result["query"] == query
    assert result["answer"] == "This is a mock answer"
    assert len(result["sources"]) == 1
    assert result["sources"][0]["id"] == "doc1"
    assert result["sources"][0]["source"] == "test"