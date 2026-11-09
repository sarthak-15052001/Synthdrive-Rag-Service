import pytest
from unittest.mock import MagicMock, patch
from src.querying.agent import QueryAgent, AgentState

@pytest.fixture
def mock_clients():
    postgres_client = MagicMock()
    weaviate_client = MagicMock()
    neo4j_client = MagicMock()
    return postgres_client, weaviate_client, neo4j_client

@pytest.fixture
def mock_openai_response():
    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(
            message=MagicMock(
                content='{"plan": ["Use vector search for semantic similarity", "Use graph traversal for relationships"], "tools_to_use": ["vector_search", "graph_traversal"]}'
            )
        )
    ]
    return mock_response

@pytest.mark.asyncio
async def test_agent_planning(mock_clients, mock_openai_response):
    postgres, weaviate, neo4j = mock_clients
    
    with patch('openai.OpenAI') as mock_openai:
        mock_openai.return_value.chat.completions.create.return_value = mock_openai_response
        
        agent = QueryAgent(postgres, weaviate, neo4j)
        result = await agent.query_async(
            query="What are the relationships between entities?",
            filters={"tenant_id": "test"},
            top_k=5
        )
        
        # Verify result structure
        assert "query" in result
        assert "answer" in result
        assert "sources" in result
        assert "reasoning" in result
        assert "synthesis" in result
        
        # Verify tool execution history
        assert len(result.get("sources", [])) > 0
        for source in result["sources"]:
            assert "execution_order" in source

@pytest.mark.asyncio
async def test_agent_tool_execution(mock_clients):
    postgres, weaviate, neo4j = mock_clients
    
    # Mock vector search results
    vector_result = {
        "content": "Test document content",
        "metadata": {"page": 1},
        "source": "test.pdf",
        "citation_id": "vector-1"
    }
    weaviate.query_documents.return_value = [vector_result]
    
    # Mock graph traversal results
    graph_result = {
        "document_id": "doc1",
        "content": "Test graph content",
        "source": "graph.pdf",
        "citation_id": "graph-1"
    }
    neo4j.traverse_relations.return_value = [graph_result]
    
    with patch('openai.OpenAI') as mock_openai:
        # Mock planning response
        mock_openai.return_value.chat.completions.create.side_effect = [
            MagicMock(
                choices=[
                    MagicMock(
                        message=MagicMock(
                            content='{"plan": ["Use vector search", "Use graph traversal"], "tools_to_use": ["vector_search", "graph_traversal"]}'
                        )
                    )
                ]
            ),
            # Mock agent decisions
            MagicMock(
                choices=[
                    MagicMock(
                        message=MagicMock(
                            content='{"action": "use_tool", "tool": "vector_search", "input": {"query": "test query"}}'
                        )
                    )
                ]
            ),
            MagicMock(
                choices=[
                    MagicMock(
                        message=MagicMock(
                            content='{"action": "use_tool", "tool": "graph_traversal", "input": {"query": "test query"}}'
                        )
                    )
                ]
            ),
            # Mock synthesis response
            MagicMock(
                choices=[
                    MagicMock(
                        message=MagicMock(
                            content='{"action": "finish"}'
                        )
                    )
                ]
            ),
            MagicMock(
                choices=[
                    MagicMock(
                        message=MagicMock(
                            content="Synthesized answer with citations [vector-1], [graph-1]"
                        )
                    )
                ]
            )
        ]
        
        agent = QueryAgent(postgres, weaviate, neo4j)
        result = await agent.query_async("test query")
        
        # Verify tool execution
        assert result["answer"] is not None
        assert len(result["sources"]) > 0
        
        # Verify tool history
        sources = result["sources"]
        assert any(s["id"] == "vector-1" for s in sources)
        assert any(s["id"] == "graph-1" for s in sources)
        
        # Verify execution order
        vector_source = next(s for s in sources if s["id"] == "vector-1")
        graph_source = next(s for s in sources if s["id"] == "graph-1")
        assert vector_source["execution_order"] < graph_source["execution_order"]

@pytest.mark.asyncio
async def test_agent_error_handling(mock_clients):
    postgres, weaviate, neo4j = mock_clients
    
    # Mock tool error
    weaviate.query_documents.side_effect = Exception("Test error")
    
    with patch('openai.OpenAI') as mock_openai:
        mock_openai.return_value.chat.completions.create.side_effect = [
            MagicMock(
                choices=[
                    MagicMock(
                        message=MagicMock(
                            content='{"plan": ["Use vector search"], "tools_to_use": ["vector_search"]}'
                        )
                    )
                ]
            ),
            MagicMock(
                choices=[
                    MagicMock(
                        message=MagicMock(
                            content='{"action": "use_tool", "tool": "vector_search", "input": {"query": "test query"}}'
                        )
                    )
                ]
            )
        ]
        
        agent = QueryAgent(postgres, weaviate, neo4j)
        with pytest.raises(Exception) as exc:
            await agent.query_async("test query")
        assert "Test error" in str(exc.value)

def test_agent_sync_query(mock_clients, mock_openai_response):
    postgres, weaviate, neo4j = mock_clients
    
    with patch('openai.OpenAI') as mock_openai:
        mock_openai.return_value.chat.completions.create.return_value = mock_openai_response
        
        agent = QueryAgent(postgres, weaviate, neo4j)
        result = agent.query("test query")
        
        assert isinstance(result, dict)
        assert "query" in result
        assert "answer" in result
        assert "sources" in result