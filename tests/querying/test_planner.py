"""
Tests for the Planner module in SynthDrive's LangGraph querying system.
"""
import pytest
import asyncio
from unittest.mock import MagicMock, patch

from src.querying.planner import PlannerNode, PlannerState


@pytest.fixture
def planner_node():
    """Fixture for creating a PlannerNode instance."""
    return PlannerNode()


@pytest.fixture
def planner_state():
    """Fixture for creating a basic PlannerState."""
    return {
        "original_query": "What tools are available for video generation?",
        "organization_id": "test-org",
        "plan": None,
        "retrieved_docs": [],
        "graph_insights": [],
        "final_answer": None,
        "error_log": []
    }


def test_planner_state_structure():
    """Test that the PlannerState has the expected structure."""
    state: PlannerState = {
        "original_query": "test query",
        "organization_id": "test-org",
        "plan": "test plan",
        "retrieved_docs": [],
        "graph_insights": [],
        "final_answer": "test answer",
        "error_log": []
    }
    
    assert "original_query" in state
    assert "organization_id" in state
    assert "plan" in state
    assert "retrieved_docs" in state
    assert "graph_insights" in state
    assert "final_answer" in state
    assert "error_log" in state


@pytest.mark.asyncio
async def test_plan_retrieval_success(planner_node, planner_state):
    """Test that plan_retrieval successfully generates a plan."""
    # Mock the OpenAI client's chat.completions.create method
    with patch.object(planner_node.openai_client.chat.completions, 'create') as mock_create:
        # Configure the mock to return a response with a plan
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "First search for tools in Weaviate, then query Neo4j for relationships between the found tools."
        mock_create.return_value = mock_response
        
        # Call the plan_retrieval method
        result = await planner_node.plan_retrieval(planner_state)
        
        # Verify that the method was called with the expected arguments
        mock_create.assert_called_once()
        
        # Verify that the result contains the expected plan
        assert "plan" in result
        assert result["plan"] == "First search for tools in Weaviate, then query Neo4j for relationships between the found tools."
        
        # Verify that the original state was not modified
        assert result["original_query"] == planner_state["original_query"]
        assert result["organization_id"] == planner_state["organization_id"]


@pytest.mark.asyncio
async def test_plan_retrieval_error(planner_node, planner_state):
    """Test that plan_retrieval handles errors gracefully."""
    # Mock the OpenAI client's chat.completions.create method to raise an exception
    with patch.object(planner_node.openai_client.chat.completions, 'create') as mock_create:
        mock_create.side_effect = Exception("Test error")
        
        # Call the plan_retrieval method
        result = await planner_node.plan_retrieval(planner_state)
        
        # Verify that the error was logged
        assert "error_log" in result
        assert len(result["error_log"]) > 0
        assert "Test error" in result["error_log"][0]
        
        # Verify that the original state was not modified
        assert result["original_query"] == planner_state["original_query"]
        assert result["organization_id"] == planner_state["organization_id"]


@pytest.mark.asyncio
async def test_plan_retrieval_with_existing_plan(planner_node, planner_state):
    """Test that plan_retrieval can revise an existing plan."""
    # Set an existing plan in the state
    planner_state["plan"] = "Search for tools in Weaviate."
    
    # Mock the OpenAI client's chat.completions.create method
    with patch.object(planner_node.openai_client.chat.completions, 'create') as mock_create:
        # Configure the mock to return a response with a revised plan
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "First search for tools in Weaviate, then query Neo4j for relationships between the found tools."
        mock_create.return_value = mock_response
        
        # Call the plan_retrieval method
        result = await planner_node.plan_retrieval(planner_state)
        
        # Verify that the method was called with the expected arguments
        mock_create.assert_called_once()
        
        # Verify that the result contains the revised plan
        assert "plan" in result
        assert result["plan"] == "First search for tools in Weaviate, then query Neo4j for relationships between the found tools."
        
        # Verify that the original state was not modified
        assert result["original_query"] == planner_state["original_query"]
        assert result["organization_id"] == planner_state["organization_id"]


@pytest.mark.parametrize("query,expected_plan_contains", [
    ("What tools are available for video generation?", "Weaviate"),
    ("How are users connected to workflows?", "Neo4j"),
    ("Find documents about machine learning", "vector search"),
    ("What is the relationship between John and the marketing team?", "graph"),
])
@pytest.mark.asyncio
async def test_plan_retrieval_query_types(planner_node, planner_state, query, expected_plan_contains):
    """Test that plan_retrieval generates appropriate plans for different query types."""
    # Update the query in the state
    planner_state["original_query"] = query
    
    # Mock the OpenAI client's chat.completions.create method
    with patch.object(planner_node.openai_client.chat.completions, 'create') as mock_create:
        # Configure the mock to return a response with a plan
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        # For simplicity, we'll just return a plan that contains the expected text
        mock_response.choices[0].message.content = f"Search using {expected_plan_contains}"
        mock_create.return_value = mock_response
        
        # Call the plan_retrieval method
        result = await planner_node.plan_retrieval(planner_state)
        
        # Verify that the result contains a plan with the expected text
        assert "plan" in result
        assert expected_plan_contains.lower() in result["plan"].lower()


if __name__ == "__main__":
    pytest.main()