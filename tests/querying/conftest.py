import pytest
import os
from unittest.mock import MagicMock, patch
import json

from src.core.config import settings
from src.data_stores.weaviate_client import WeaviateClient
from src.data_stores.neo4j_client import Neo4jClient
from src.data_stores.postgres_client import PostgresClient
from src.querying.agent import QueryAgent
from src.querying.graph import QueryGraph
from src.querying.tools.vector_search import VectorSearchTool
from src.querying.tools.graph_retrieval import GraphRetrievalTool


@pytest.fixture
def mock_weaviate_client():
    """Create a mock Weaviate client."""
    mock_client = MagicMock(spec=WeaviateClient)
    
    # Mock the query_documents method
    mock_client.query_documents.return_value = [
        {
            "content": "Artificial intelligence (AI) is intelligence demonstrated by machines.",
            "metadata": {"source": "wikipedia", "created_at": "2023-01-01"},
            "source": "wikipedia",
            "relevance_score": 0.95
        },
        {
            "content": "Machine learning is a subset of AI focused on training models to learn from data.",
            "metadata": {"source": "textbook", "created_at": "2023-02-01"},
            "source": "textbook",
            "relevance_score": 0.85
        }
    ]
    
    return mock_client


@pytest.fixture
def mock_neo4j_client():
    """Create a mock Neo4j client."""
    mock_client = MagicMock(spec=Neo4jClient)
    
    # Mock the traverse_relations method
    mock_client.traverse_relations.return_value = [
        {
            "document_id": "doc1",
            "entities": [{"name": "AI", "type": "Concept"}, {"name": "Machine Learning", "type": "Concept"}],
            "score": 0.9
        }
    ]
    
    # Mock the get_document_by_id method
    mock_client.get_document_by_id.return_value = {
        "id": "doc1",
        "content": "AI and Machine Learning are related fields in computer science.",
        "source": "textbook",
        "created_at": "2023-03-01",
        "metadata": {"author": "John Doe"}
    }
    
    return mock_client


@pytest.fixture
def mock_postgres_client():
    """Create a mock PostgreSQL client."""
    return MagicMock(spec=PostgresClient)


@pytest.fixture
def mock_openai_client():
    """Create a mock OpenAI client."""
    mock_client = MagicMock()
    
    # Mock the chat.completions.create method
    mock_completion = MagicMock()
    mock_completion.choices = [MagicMock()]
    mock_completion.choices[0].message.content = json.dumps({
        "plan": ["Use vector search to find relevant documents", "Use graph traversal to find relationships"],
        "tools_to_use": ["vector_search", "graph_traversal"]
    })
    
    mock_client.chat.completions.create.return_value = mock_completion
    
    return mock_client


@pytest.fixture
def query_graph(mock_weaviate_client, mock_neo4j_client, mock_postgres_client):
    """Create a QueryGraph instance with mock clients."""
    with patch('src.querying.graph.OpenAI') as mock_openai:
        # Configure the mock OpenAI client
        mock_openai_instance = MagicMock()
        mock_completion = MagicMock()
        mock_completion.choices = [MagicMock()]
        mock_completion.choices[0].message.content = json.dumps({
            "steps": ["Use vector search", "Use graph traversal"]
        })
        mock_openai_instance.chat.completions.create.return_value = mock_completion
        mock_openai.return_value = mock_openai_instance
        
        # Create the QueryGraph
        graph = QueryGraph(
            postgres_client=mock_postgres_client,
            weaviate_client=mock_weaviate_client,
            neo4j_client=mock_neo4j_client
        )
        
        return graph


@pytest.fixture
def query_agent(mock_weaviate_client, mock_neo4j_client, mock_postgres_client):
    """Create a QueryAgent instance with mock clients."""
    with patch('src.querying.agent.OpenAI') as mock_openai:
        # Configure the mock OpenAI client
        mock_openai_instance = MagicMock()
        
        # Mock for plan creation
        plan_completion = MagicMock()
        plan_completion.choices = [MagicMock()]
        plan_completion.choices[0].message.content = json.dumps({
            "plan": ["Use vector search to find relevant documents", "Use graph traversal to find relationships"],
            "tools_to_use": ["vector_search", "graph_traversal"]
        })
        
        # Mock for synthesis
        synthesis_completion = MagicMock()
        synthesis_completion.choices = [MagicMock()]
        synthesis_completion.choices[0].message.content = "Based on the retrieved information, AI and Machine Learning are related fields in computer science [vector-1][graph-doc-1]."
        
        # Configure the mock to return different responses based on the prompt
        def side_effect(*args, **kwargs):
            prompt = kwargs.get("messages", [{}])[-1].get("content", "")
            if "plan" in prompt.lower():
                return plan_completion
            else:
                return synthesis_completion
        
        mock_openai_instance.chat.completions.create.side_effect = side_effect
        mock_openai.return_value = mock_openai_instance
        
        # Create the QueryAgent
        agent = QueryAgent(
            postgres_client=mock_postgres_client,
            weaviate_client=mock_weaviate_client,
            neo4j_client=mock_neo4j_client
        )
        
        # Mock the graph.ainvoke method
        async def mock_ainvoke(state):
            return {
                "query": state["query"],
                "answer": "Based on the retrieved information, AI and Machine Learning are related fields in computer science [vector-1][graph-doc-1].",
                "citations": [
                    {"id": "vector-1", "source": "wikipedia", "content": "Artificial intelligence (AI) is intelligence demonstrated by machines."},
                    {"id": "graph-doc-1", "source": "textbook", "content": "AI and Machine Learning are related fields in computer science."}
                ],
                "reasoning": "The system retrieved relevant information using multiple tools and synthesized a comprehensive answer with citations."
            }
        
        agent.graph.ainvoke = mock_ainvoke
        
        return agent


@pytest.fixture
def vector_search_tool(mock_weaviate_client):
    """Create a VectorSearchTool instance with a mock client."""
    with patch('src.querying.tools.vector_search.OpenAI') as mock_openai:
        # Configure the mock OpenAI client
        mock_openai_instance = MagicMock()
        mock_completion = MagicMock()
        mock_completion.choices = [MagicMock()]
        mock_completion.choices[0].message.content = json.dumps({
            "queries": ["What is AI?", "Define artificial intelligence", "AI explanation"]
        })
        mock_openai_instance.chat.completions.create.return_value = mock_completion
        mock_openai.return_value = mock_openai_instance
        
        # Create the VectorSearchTool
        tool = VectorSearchTool(mock_weaviate_client)
        
        return tool


@pytest.fixture
def graph_retrieval_tool(mock_neo4j_client):
    """Create a GraphRetrievalTool instance with a mock client."""
    with patch('src.querying.tools.graph_retrieval.OpenAI') as mock_openai:
        # Configure the mock OpenAI client
        mock_openai_instance = MagicMock()
        mock_completion = MagicMock()
        mock_completion.choices = [MagicMock()]
        mock_completion.choices[0].message.content = json.dumps({
            "entities": ["AI", "Machine Learning"]
        })
        mock_openai_instance.chat.completions.create.return_value = mock_completion
        mock_openai.return_value = mock_openai_instance
        
        # Create the GraphRetrievalTool
        tool = GraphRetrievalTool(mock_neo4j_client)
        
        return tool


@pytest.fixture
def sample_test_data():
    """Provide sample test data for queries."""
    return {
        "simple_query": "What is artificial intelligence?",
        "relationship_query": "How are AI and Machine Learning related?",
        "complex_query": "Explain the differences between supervised and unsupervised learning in AI."
    }