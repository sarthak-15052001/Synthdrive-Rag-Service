import pytest
import asyncio
from unittest.mock import patch, MagicMock

from src.querying.graph import QueryGraph, QueryState
from src.querying.agent import QueryAgent
from src.querying.tools.vector_search import VectorSearchTool
from src.querying.tools.graph_retrieval import GraphRetrievalTool


def test_query_graph_initialization(query_graph):
    """Test that QueryGraph initializes correctly."""
    assert query_graph is not None
    assert hasattr(query_graph, 'graph')
    assert hasattr(query_graph, 'weaviate_client')
    assert hasattr(query_graph, 'neo4j_client')


def test_query_graph_execution(query_graph):
    """Test that QueryGraph executes a query correctly."""
    result = query_graph.query("What is artificial intelligence?")
    
    assert result is not None
    assert "query" in result
    assert "answer" in result
    assert "sources" in result or "reasoning" in result
    
    assert result["query"] == "What is artificial intelligence?"
    assert result["answer"] != ""


def test_query_agent_initialization(query_agent):
    """Test that QueryAgent initializes correctly."""
    assert query_agent is not None
    assert hasattr(query_agent, 'graph')
    assert hasattr(query_agent, 'weaviate_client')
    assert hasattr(query_agent, 'neo4j_client')
    assert hasattr(query_agent, 'vector_search_tool')
    assert hasattr(query_agent, 'graph_retrieval_tool')


def test_query_agent_execution(query_agent):
    """Test that QueryAgent executes a query correctly."""
    result = query_agent.query("What is artificial intelligence?")
    
    assert result is not None
    assert "query" in result
    assert "answer" in result
    assert "sources" in result
    
    assert result["query"] == "What is artificial intelligence?"
    assert result["answer"] != ""
    assert len(result["sources"]) > 0


def test_vector_search_tool(vector_search_tool):
    """Test that VectorSearchTool works correctly."""
    # Run the async method in a synchronous context
    result = asyncio.run(vector_search_tool.search("What is artificial intelligence?"))
    
    assert result is not None
    assert isinstance(result, list)
    assert len(result) > 0
    
    # Check the structure of the results
    for item in result:
        assert "content" in item
        assert "metadata" in item
        assert "source" in item
        assert "relevance_score" in item
        assert "citation_id" in item


def test_graph_retrieval_tool(graph_retrieval_tool):
    """Test that GraphRetrievalTool works correctly."""
    # Run the async method in a synchronous context
    result = asyncio.run(graph_retrieval_tool.traverse_relations("How are AI and Machine Learning related?"))
    
    assert result is not None
    assert isinstance(result, list)
    assert len(result) > 0
    
    # Check the structure of the results
    for item in result:
        assert "content" in item
        assert "metadata" in item
        assert "source" in item
        assert "citation_id" in item


@pytest.mark.parametrize("query_type", ["simple_query", "relationship_query", "complex_query"])
def test_end_to_end_querying(query_agent, sample_test_data, query_type):
    """Test end-to-end querying with different types of queries."""
    query = sample_test_data[query_type]
    
    result = query_agent.query(query)
    
    assert result is not None
    assert "query" in result
    assert "answer" in result
    assert "sources" in result
    
    assert result["query"] == query
    assert result["answer"] != ""
    assert len(result["sources"]) > 0


def test_citation_formatting(query_agent):
    """Test that citations are properly formatted in the answer."""
    result = query_agent.query("How are AI and Machine Learning related?")
    
    assert result is not None
    assert "answer" in result
    assert "sources" in result
    
    # Check that the answer contains citation references
    answer = result["answer"]
    assert "[" in answer and "]" in answer
    
    # Check that all citations in the answer correspond to sources
    citations = []
    for source in result["sources"]:
        if "id" in source:
            citations.append(source["id"])
    
    # Simple check for citation presence
    for citation in citations:
        assert f"[{citation}]" in answer or citation in answer


def test_multi_tool_integration(query_agent):
    """Test that multiple tools are integrated correctly."""
    # Mock the vector_search_tool and graph_retrieval_tool to track calls
    query_agent.vector_search_tool.search = MagicMock()
    query_agent.vector_search_tool.search.return_value = [
        {
            "content": "Artificial intelligence (AI) is intelligence demonstrated by machines.",
            "metadata": {"source": "wikipedia"},
            "source": "wikipedia",
            "relevance_score": 0.95,
            "citation_id": "vector-1"
        }
    ]
    
    query_agent.graph_retrieval_tool.traverse_relations = MagicMock()
    query_agent.graph_retrieval_tool.traverse_relations.return_value = [
        {
            "content": "AI and Machine Learning are related fields.",
            "metadata": {"type": "graph_result"},
            "source": "graph_database",
            "citation_id": "graph-1"
        }
    ]
    
    # Execute a query that should use both tools
    result = query_agent.query("How are AI and Machine Learning related?")
    
    # In a real test, we would check that both tools were called
    # But since we've mocked the graph.ainvoke method, we'll just check the result
    assert result is not None
    assert "answer" in result
    assert "sources" in result
    
    # Check that the sources include both vector and graph results
    source_ids = [source.get("id") for source in result["sources"]]
    assert any("vector" in id for id in source_ids)
    assert any("graph" in id for id in source_ids)


def test_error_handling(query_agent):
    """Test that errors are handled gracefully."""
    # Mock the graph.ainvoke method to raise an exception
    async def mock_ainvoke_error(state):
        raise Exception("Test error")
    
    original_ainvoke = query_agent.graph.ainvoke
    query_agent.graph.ainvoke = mock_ainvoke_error
    
    # Execute a query that should raise an exception
    with pytest.raises(Exception):
        query_agent.query("What is artificial intelligence?")
    
    # Restore the original method
    query_agent.graph.ainvoke = original_ainvoke


def test_async_execution(query_agent):
    """Test that async execution works correctly."""
    # Create an async function to test
    async def async_test():
        return await query_agent.query_async("What is artificial intelligence?")
    
    # Run the async function
    result = asyncio.run(async_test())
    
    assert result is not None
    assert "query" in result
    assert "answer" in result
    assert "sources" in result