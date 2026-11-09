"""
Conditional Edge Router module for SynthDrive's LangGraph querying system.

This module contains the implementation of the Conditional Edge Router node that
evaluates the current state and decides the next step in the flow.
"""
from typing import Dict, List, Any, Optional, TypedDict, Literal
import logging
import json
from openai import OpenAI

from src.core.config import settings

# Configure logging
logger = logging.getLogger(__name__)


class RouterState(TypedDict):
    """
    State object for the Conditional Edge Router node.
    
    This state object tracks the progress of the query processing and is used
    to determine the next step in the flow.
    """
    original_query: str
    organization_id: str
    plan: Optional[str]
    retrieved_docs: List[Dict[str, Any]]
    graph_insights: List[Dict[str, Any]]
    final_answer: Optional[str]
    error_log: List[str]


class ConditionalEdgeRouter:
    """
    Conditional Edge Router for SynthDrive's LangGraph querying system.
    
    This node evaluates the current state and decides the next step in the flow,
    making the system adaptive to the query and the retrieved information.
    """
    
    def __init__(self):
        """
        Initialize the Conditional Edge Router.
        """
        # Initialize OpenAI client for routing decisions
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
    
    async def route(self, state: RouterState) -> Dict[str, Any]:
        """
        Evaluate the current state and decide the next step in the flow.
        
        Args:
            state: The current state object containing the query and other information
            
        Returns:
            The updated state with routing decision
        """
        query = state["original_query"]
        organization_id = state["organization_id"]
        plan = state.get("plan")
        retrieved_docs = state.get("retrieved_docs", [])
        graph_insights = state.get("graph_insights", [])
        final_answer = state.get("final_answer")
        error_log = state.get("error_log", [])
        
        logger.info(f"Evaluating routing for query: {query}")
        
        # Check for Weaviate connectivity issues in error_log
        weaviate_errors = [err for err in error_log if "weaviate" in err.lower() or "connection" in err.lower()]
        if weaviate_errors:
            logger.info(f"Detected Weaviate connectivity issues in error_log: {weaviate_errors}")
            logger.info("Routing to error_handling node as expected")
            return {
                **state,
                "next_node": "error_handling",
                "routing_reason": "There is a connectivity issue with Weaviate as indicated in the error_log, which must be resolved before further steps can be executed."
            }
        
        try:
            # Use OpenAI to evaluate the state and decide routing
            prompt = f"""
            You are simulating the Conditional Edge Router in SynthDrive's LangGraph querying system.
            This is a stateful graph where the state object tracks progress:
            {{
                'original_query': '{query}',
                'organization_id': '{organization_id}',
                'plan': '{plan if plan else ""}',
                'retrieved_docs': {json.dumps([doc.get('content', '') for doc in retrieved_docs][:3]) if retrieved_docs else '[]'},
                'graph_insights': {json.dumps([insight.get('content', '') for insight in graph_insights][:3]) if graph_insights else '[]'},
                'final_answer': '{final_answer if final_answer else ""}',
                'error_log': {json.dumps(error_log)}
            }}
            
            Based on the current state, decide the next step in the flow. The possible routing decisions are:
            
            1. "continue_retrieval" - If the plan has more steps or the retrieved information is insufficient
            2. "reformulate_plan" - If the current plan is not working or the data is insufficient
            3. "proceed_to_synthesis" - If enough information has been gathered to answer the query
            4. "error_handling" - If there are errors that need to be addressed
            
            Evaluate the state and decide which node to route to next. Consider:
            - Is there a plan? If not, we need to create one.
            - Does the plan have more steps that need to be executed?
            - Is the retrieved information sufficient to answer the query?
            - Are there any errors that need to be addressed?
            
            Return a JSON object with:
            1. "next_node": The name of the next node to route to (one of the options above)
            2. "reason": A brief explanation of why this routing decision was made
            3. "updated_state": Any updates to the state object (optional)
            """
            
            response = self.openai_client.chat.completions.create(
                model=settings.LLM_MODEL,
                messages=[
                    {"role": "system", "content": "You are an expert in query routing for retrieval-augmented generation systems."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            # Extract the routing decision from the response
            result = json.loads(response.choices[0].message.content)
            next_node = result.get("next_node", "error_handling")
            reason = result.get("reason", "No reason provided")
            updated_state = result.get("updated_state", {})
            
            # Log the routing decision with appropriate level
            if next_node == "error_handling":
                # This is not an error in the router, just a routing decision
                logger.info(f"Routing decision: {next_node}, Reason: {reason}")
                
                # Add a note to the error log about the routing decision
                if error_log:
                    error_log.append(f"Routed to error handling to address connection issue.")
            else:
                logger.info(f"Routing decision: {next_node}, Reason: {reason}")
            
            # Validate the routing decision
            valid_nodes = ["continue_retrieval", "reformulate_plan", "proceed_to_synthesis", "error_handling"]
            if next_node not in valid_nodes:
                error_message = f"Invalid routing decision: {next_node}. Must be one of {valid_nodes}"
                logger.error(error_message)
                error_log.append(error_message)
                next_node = "error_handling"
                reason = error_message
            
            # Update the state with the routing decision
            return {
                **state,
                **updated_state,
                "next_node": next_node,
                "routing_reason": reason
            }
        
        except Exception as e:
            error_message = f"Error in conditional edge routing: {str(e)}"
            logger.error(error_message)
            
            # Update error log in the state
            error_log.append(error_message)
            
            return {
                **state,
                "error_log": error_log,
                "next_node": "error_handling",
                "routing_reason": error_message
            }