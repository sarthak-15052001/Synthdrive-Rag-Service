from typing import Dict, List, Any, Optional, TypedDict, Annotated, Literal, Union, Tuple
import logging
import json
import asyncio
from openai import OpenAI
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_core.tools import Tool, BaseTool
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, FunctionMessage, BaseMessage

from src.core.config import settings
from src.data_stores.postgres_client import PostgresClient
from src.data_stores.weaviate_client import WeaviateClient
from src.data_stores.neo4j_client import Neo4jClient
from src.querying.tools.vector_search import VectorSearchTool
from src.querying.tools.graph_retrieval import GraphRetrievalTool
from src.querying.tools.kernel_of_truth import KernelOfTruthTool
from src.querying.planner import PlannerNode, PlannerState

# Configure logging
logger = logging.getLogger(__name__)


# Define the agent state
class AgentState(TypedDict):
    query: Annotated[str, "The user's query"]
    filters: Optional[Dict[str, Any]]
    top_k: int
    chat_history: List[BaseMessage]  # Using LangChain message types
    messages: List[BaseMessage]  # For ToolNode communication
    retrieved_docs: Dict[str, List[Dict[str, Any]]]
    plan: Optional[List[str]]
    retrieval_strategy: Optional[str]  # Added for the planner node
    tools_to_use: Optional[List[str]]
    current_tool: Optional[str]
    tool_input: Optional[Dict[str, Any]]  # Current tool input
    tool_results: Dict[str, Any]  # Historical results
    tool_history: List[Dict[str, Any]]  # Ordered history of tool executions
    synthesis: Optional[str]
    citations: List[Dict[str, Any]]
    answer: Optional[str]
    reasoning: Optional[str]
    error: Optional[str]
    organization_id: Optional[str]  # Added for the planner node


class QueryAgent:
    """
    Agent for querying the RAG system using LangGraph.
    """

    def __init__(
        self,
        postgres_client: PostgresClient,
        weaviate_client: WeaviateClient,
        neo4j_client: Neo4jClient
    ):
        """
        Initialize the query agent.
        
        Args:
            postgres_client: The PostgreSQL client
            weaviate_client: The Weaviate client
            neo4j_client: The Neo4j client
        """
        self.postgres_client = postgres_client
        self.weaviate_client = weaviate_client
        self.neo4j_client = neo4j_client
        
        # Initialize OpenAI client
        # Handle both standard and project-based API keys
        api_key = settings.OPENAI_API_KEY
        
        # Configure the OpenAI client with additional options for project-based API keys
        self.openai_client = OpenAI(
            api_key=api_key,
            organization=settings.OPENAI_ORGANIZATION if hasattr(settings, 'OPENAI_ORGANIZATION') else None,
            project=api_key.startswith('sk-proj-') if api_key else None
        )
        
        # Initialize tools
        self.vector_search_tool = VectorSearchTool(weaviate_client)
        self.graph_retrieval_tool = GraphRetrievalTool(neo4j_client)
        self.kernel_of_truth_tool = KernelOfTruthTool(neo4j_client)
        self.planner_node = PlannerNode()
        
        # Build the agent graph
        self.graph = self._build_graph()
        
    def _get_state_config(self) -> Dict[str, Any]:
        """Get the state configuration for the graph."""
        return {
            "query": "query",  # Annotated key for query
            "filters": None,
            "top_k": 5,
            "chat_history": [],
            "messages": [],
            "retrieved_docs": {},
            "plan": None,
            "retrieval_strategy": None,  # Added for the planner node
            "tools_to_use": None,
            "current_tool": None,
            "tool_input": None,
            "tool_results": {},
            "tool_history": [],
            "synthesis": None,
            "citations": [],
            "answer": None,
            "reasoning": None,
            "error": None,
            "organization_id": "default"  # Added for the planner node
        }
        
    
    def _build_graph(self) -> StateGraph:
        """
        Build the agent graph.
        
        Returns:
            The agent graph
        """
        # Create tool objects
        tools = [
            Tool(
                name="vector_search",
                description="Search for documents using vector similarity",
                func=lambda **kwargs: asyncio.run(self.vector_search_tool.search(**kwargs))
            ),
            Tool(
                name="graph_traversal",
                description="Traverse the graph to find relationships",
                func=lambda **kwargs: asyncio.run(self.graph_retrieval_tool.traverse_relations(**kwargs))
            ),
            Tool(
                name="generate_cypher",
                description="Generate a Cypher query from natural language",
                func=lambda **kwargs: asyncio.run(self.graph_retrieval_tool.generate_cypher(**kwargs))
            ),
            Tool(
                name="multi_query_search",
                description="Perform search with multiple query variations",
                func=lambda **kwargs: asyncio.run(self.vector_search_tool.multi_query_search(**kwargs))
            ),
            Tool(
                name="kernel_of_truth",
                description="Perform multi-hop graph queries to uncover relationships between entities",
                func=lambda **kwargs: asyncio.run(self.kernel_of_truth_tool.query_relationships(**kwargs))
            )
        ]
        
        # Tools are now handled by ToolNode
        
        # Create tool node with our tools and custom configuration
        tool_node = ToolNode(
            tools=tools,
            handle_tool_errors=True,  # Enable error handling
            messages_key="messages"  # Use messages key from state
        )

        
        # Define a custom agent node
        async def agent_node(state: AgentState) -> AgentState:
            """
            Custom agent node that uses OpenAI to decide which tool to use.
            """
            query = state["query"]
            chat_history = state.get("chat_history", [])
            tool_history = state.get("tool_history", [])
            current_tool = state.get("current_tool")
            
            # Get the plan and tools to use
            plan = state.get("plan", [])
            tools_to_use = state.get("tools_to_use", [])
            
            # Format tool execution history for the prompt
            tool_results_str = ""
            for execution in tool_history:
                tool_name = execution["tool"]
                result = execution["result"]
                order = execution.get("order", 0)
                tool_results_str += f"\n\nStep {order}: Tool {tool_name}\nResult: {json.dumps(result, indent=2)}"
            
            # Create the prompt
            prompt = f"""
            You are an expert RAG system agent that helps users find information.
            You have access to multiple tools for retrieving information:
            - vector_search: For semantic similarity search
            - graph_traversal: For finding relationships in the knowledge graph
            - generate_cypher: For generating Cypher queries for complex graph patterns
            - multi_query_search: For searching with multiple query variations
            - kernel_of_truth: For performing multi-hop graph queries to uncover relationships between entities
            
            Query: {query}
            
            Plan: {json.dumps(plan, indent=2)}
            
            Tools to use: {json.dumps(tools_to_use, indent=2)}
            
            Tool results so far: {tool_results_str}
            
            Based on the query and the plan, decide which tool to use next, or if you have enough information to provide an answer.
            If you need to use a tool, respond with a JSON object with the following structure:
            {{"action": "use_tool", "tool": "tool_name", "input": {{"param1": "value1", "param2": "value2"}}}}
            
            If you have enough information to provide an answer, respond with:
            {{"action": "finish"}}
            """
            
            # Call OpenAI
            response = self.openai_client.chat.completions.create(
                model=settings.LLM_MODEL,
                messages=[
                    {"role": "system", "content": "You are an expert RAG system agent that helps users find information."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            # Parse the response
            result = json.loads(response.choices[0].message.content)
            action = result.get("action", "")
            
            if action == "use_tool":
                tool_name = result.get("tool", "")
                tool_input = result.get("input", {})
                
                # Create tool call message using LangChain message types
                tool_message = AIMessage(
                    content="",
                    additional_kwargs={
                        "tool_calls": [{
                            "id": f"{tool_name}-{len(state.get('tool_results', {}))}",
                            "type": "function",
                            "function": {
                                "name": tool_name,
                                "arguments": json.dumps(tool_input)
                            }
                        }]
                    }
                )
                
                # Update chat history with LangChain message types
                chat_history = state.get("chat_history", [])
                chat_history.extend([
                    SystemMessage(content="You are an expert RAG system agent that helps users find information."),
                    HumanMessage(content=query),
                    AIMessage(content=f"I'll use the {tool_name} tool to find relevant information.")
                ])
                
                # Update tool history before execution
                tool_history = state.get("tool_history", [])
                current_order = len(tool_history) + 1
                tool_history.append({
                    "tool": tool_name,
                    "input": tool_input,
                    "order": current_order,
                    "result": None  # Will be updated after execution
                })
                
                # Update the state
                return {
                    **state,
                    "current_tool": tool_name,
                    "tool_input": tool_input,
                    "chat_history": chat_history,
                    "tool_history": tool_history,
                    "messages": [tool_message]  # LangGraph ToolNode expects a list with a single tool call
                }
            elif action == "finish":
                # Update chat history before finishing
                chat_history.append({
                    "role": "assistant",
                    "content": "I have gathered all the necessary information. Let me synthesize the results."
                })
                
                # We're done, move to synthesis
                return {
                    **state,
                    "current_tool": "FINISH",
                    "chat_history": chat_history
                }
            else:
                # Invalid action
                return {
                    **state,
                    "error": f"Invalid action: {action}"
                }
        
        # Define the agent state
        workflow = StateGraph(AgentState)
        
        # Create nodes
        tool_node = ToolNode(
            tools=tools,
            handle_tool_errors=True,
            messages_key="messages"
        )
        
        # Add nodes
        workflow.add_node("agent_node", agent_node)
        workflow.add_node("tool_node", tool_node)
        workflow.add_node("plan_node", self._create_plan)  # Changed name to avoid conflict
        workflow.add_node("retrieval_planner", self._plan_retrieval_strategy)  # Added for the planner node
        workflow.add_node("synthesize_node", self._synthesize_results)  # Changed name to avoid conflict
        
        # Add edges
        workflow.add_edge("plan_node", "retrieval_planner")  # Plan node now goes to retrieval planner
        workflow.add_edge("retrieval_planner", "agent_node")  # Retrieval planner goes to agent node
        workflow.add_edge("agent_node", "tool_node")
        workflow.add_edge("tool_node", "agent_node")
        workflow.add_edge("agent_node", "synthesize_node")
        workflow.add_edge("synthesize_node", END)
        
        # Set the entry point
        workflow.set_entry_point("plan_node")
        
        # Conditional edges
        def should_end(state: AgentState) -> Literal["agent_node", "synthesize_node"]:
            """Determine if the agent should continue or synthesize results."""
            if state.get("current_tool") == "FINISH":
                return "synthesize_node"
            return "agent_node"
        
        workflow.add_conditional_edges(
            "agent_node",
            should_end
        )
        
        # Add nodes
        workflow.add_node("agent", agent_node)
        workflow.add_node("tools", tool_node)
        workflow.add_node("planner", self._create_plan)  # Changed from "plan" to "planner"
        workflow.add_node("retrieval_strategy", self._plan_retrieval_strategy)  # Added for the planner node
        workflow.add_node("synthesizer", self._synthesize_results)  # Changed from "synthesize" to "synthesizer"
        
        # Add edges
        workflow.add_edge("planner", "retrieval_strategy")  # Planner now goes to retrieval strategy
        workflow.add_edge("retrieval_strategy", "agent")  # Retrieval strategy goes to agent
        workflow.add_edge("agent", "tools")
        workflow.add_edge("tools", "agent")
        workflow.add_edge("agent", "synthesizer")
        workflow.add_edge("synthesizer", END)
        
        # Set the entry point
        workflow.set_entry_point("planner")
        
        # Conditional edges
        def should_end(state: AgentState) -> Literal["agent", "synthesizer"]:
            """Determine if the agent should continue or synthesize results."""
            if state.get("current_tool") == "FINISH":
                return "synthesizer"
            return "agent"
        
        workflow.add_conditional_edges(
            "agent",
            should_end
        )
        
        return workflow.compile()
    
    async def _create_plan(self, state: AgentState) -> AgentState:
        """
        Create a plan for answering the query.
        
        Args:
            state: The current state
            
        Returns:
            The updated state with a plan
        """
        query = state["query"]
        
        try:
            # Use OpenAI to create a plan
            prompt = f"""
            Analyze the following query and create a plan for retrieving information.
            Determine which retrieval methods would be most effective (vector search, graph traversal, etc.).
            
            Query: {query}
            
            Return a JSON object with:
            1. "plan": An array of steps, where each step is a string describing the retrieval action.
            2. "tools_to_use": An array of tool names that should be used (vector_search, graph_traversal, generate_cypher, multi_query_search).
            """
            
            response = self.openai_client.chat.completions.create(
                model=settings.LLM_MODEL,
                messages=[
                    {"role": "system", "content": "You are an expert in query planning for retrieval-augmented generation systems."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            # Parse the response
            result = json.loads(response.choices[0].message.content)
            plan = result.get("plan", [])
            tools_to_use = result.get("tools_to_use", [])
            
            logger.info(f"Created plan with {len(plan)} steps using {len(tools_to_use)} tools")
            
            # Initialize chat history with LangChain message types
            chat_history = [
                SystemMessage(content="You are an expert RAG system agent that helps users find information."),
                HumanMessage(content=query)
            ]
            
            # Add the plan to the chat history
            plan_message = "I'll help you answer this query. Here's my plan:\n"
            for i, step in enumerate(plan):
                plan_message += f"{i+1}. {step}\n"
            
            chat_history.append(AIMessage(content=plan_message))
            
            # Get organization_id from filters if available
            organization_id = state.get("filters", {}).get("organization_id", "default")
            if not organization_id:
                organization_id = "default"
            
            return {
                **state,
                "plan": plan,
                "tools_to_use": tools_to_use,
                "chat_history": chat_history,
                "retrieved_docs": {},
                "tool_results": {},
                "citations": [],
                "organization_id": organization_id
            }
        
        except Exception as e:
            logger.error(f"Error creating plan: {str(e)}")
            return {
                **state,
                "error": f"Error creating plan: {str(e)}",
                "chat_history": [
                    {"role": "system", "content": "You are an expert RAG system agent that helps users find information."},
                    {"role": "user", "content": query}
                ],
                "retrieved_docs": {},
                "tool_results": {},
                "citations": []
            }
    
    async def _plan_retrieval_strategy(self, state: AgentState) -> AgentState:
        """
        Plan the retrieval strategy using the PlannerNode.
        
        Args:
            state: The current state
            
        Returns:
            The updated state with a retrieval strategy
        """
        query = state["query"]
        organization_id = state.get("organization_id", "default")
        
        try:
            # Create a planner state from the agent state
            planner_state: PlannerState = {
                "original_query": query,
                "organization_id": organization_id,
                "plan": state.get("retrieval_strategy"),
                "retrieved_docs": [],
                "graph_insights": [],
                "final_answer": None,
                "error_log": []
            }
            
            # Use the planner node to generate a retrieval strategy
            updated_planner_state = await self.planner_node.plan_retrieval(planner_state)
            
            # Extract the retrieval strategy from the planner state
            retrieval_strategy = updated_planner_state.get("plan")
            
            # Update the agent state with the retrieval strategy
            chat_history = state.get("chat_history", [])
            
            # Add the retrieval strategy to the chat history
            if retrieval_strategy:
                strategy_message = f"Retrieval Strategy: {retrieval_strategy}"
                chat_history.append(AIMessage(content=strategy_message))
            
            logger.info(f"Created retrieval strategy: {retrieval_strategy}")
            
            return {
                **state,
                "retrieval_strategy": retrieval_strategy,
                "chat_history": chat_history
            }
        
        except Exception as e:
            error_message = f"Error planning retrieval strategy: {str(e)}"
            logger.error(error_message)
            
            return {
                **state,
                "error": error_message
            }
    
    async def _synthesize_results(self, state: AgentState) -> AgentState:
        """
        Synthesize the results from all tools.
        
        Args:
            state: The current state
            
        Returns:
            The updated state with synthesized results
        """
        query = state["query"]
        tool_results = state.get("tool_results", {})
        chat_history = state.get("chat_history", [])
        
        try:
            # Collect all retrieved documents
            all_docs = []
            citations = []
            
            # Process tool results and build citations
            tool_history = state.get("tool_history", [])
            tool_results = state.get("tool_results", {})
            
            # Update tool history with results
            for i, execution in enumerate(tool_history):
                tool_name = execution["tool"]
                if tool_name in tool_results:
                    tool_history[i]["result"] = tool_results[tool_name]
            
            # Build citations from tool history
            for execution in tool_history:
                tool_name = execution["tool"]
                results = execution.get("result")
                
                if isinstance(results, list):
                    for i, doc in enumerate(results):
                        citation_id = doc.get("citation_id", f"{tool_name}-{i+1}")
                        
                        all_docs.append({
                            "tool": tool_name,
                            "content": doc.get("content", ""),
                            "citation_id": citation_id,
                            "execution_order": tool_execution.get("order", 0)
                        })
                        
                        citations.append({
                            "id": citation_id,
                            "tool": tool_name,
                            "source": doc.get("source", "unknown"),
                            "content": doc.get("content", "")[:200] + "..." if len(doc.get("content", "")) > 200 else doc.get("content", ""),
                            "metadata": doc.get("metadata", {}),
                            "execution_order": tool_execution.get("order", 0)
                        })
            
            # Create context from all documents
            context = ""
            for i, doc in enumerate(all_docs):
                context += f"[{doc['citation_id']}] {doc['content']}\n\n"
            
            # Use OpenAI to synthesize the results
            prompt = f"""
            Synthesize the following information to answer the query.
            
            Query: {query}
            
            Retrieved Information:
            {context}
            
            Provide a comprehensive answer that:
            1. Directly addresses the query
            2. Includes inline citations like [vector-1], [graph-2], etc.
            3. Is well-structured and easy to understand
            4. Only cites relevant sources
            """
            
            response = self.openai_client.chat.completions.create(
                model=settings.LLM_MODEL,
                messages=[
                    {"role": "system", "content": "You are an expert in synthesizing information from multiple sources."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            synthesis = response.choices[0].message.content.strip()
            
            logger.info("Synthesized results from all tools")
            
            return {
                **state,
                "synthesis": synthesis,
                "citations": citations,
                "answer": synthesis,
                "reasoning": "The system retrieved relevant information using multiple tools and synthesized a comprehensive answer with citations."
            }
        
        except Exception as e:
            logger.error(f"Error synthesizing results: {str(e)}")
            
            # If synthesis fails, use the last agent response as the answer
            last_assistant_message = None
            for message in reversed(chat_history):
                if message.get("role") == "assistant":
                    last_assistant_message = message.get("content", "")
                    break
            
            if last_assistant_message:
                return {
                    **state,
                    "synthesis": last_assistant_message,
                    "citations": citations,
                    "answer": last_assistant_message,
                    "reasoning": "The system used the agent's final response as the answer due to synthesis error."
                }
            else:
                return {
                    **state,
                    "error": f"Error synthesizing results: {str(e)}",
                    "answer": "I encountered an error while synthesizing the results. Please try again."
                }

    async def query_async(self, query: str, filters: Optional[Dict[str, Any]] = None, top_k: int = 5) -> Dict[str, Any]:
        """
        Query the RAG system asynchronously.
        
        Args:
            query: The query string
            filters: Optional filters to apply
            top_k: Maximum number of results to return
            
        Returns:
            The query result
        """
        logger.info(f"Querying RAG system asynchronously: {query}")
        
        try:
            # Initialize the state
            # Initialize chat history
            chat_history = [
                SystemMessage(content="You are an expert RAG system agent that helps users find information."),
                HumanMessage(content=query)
            ]
            
            # Initial tool call for planning using LangChain message types
            initial_messages = [AIMessage(
                content="",
                additional_kwargs={
                    "tool_calls": [{
                        "id": "planner-0",
                        "type": "function",
                        "function": {
                            "name": "planner",
                            "arguments": json.dumps({"query": query})
                        }
                    }]
                }
            )]
            
            initial_state: AgentState = {
                "query": query,
                "filters": filters,
                "top_k": top_k,
                "chat_history": chat_history,
                "messages": initial_messages,
                "retrieved_docs": {},
                "plan": None,
                "retrieval_strategy": None,  # Added for the planner node
                "tools_to_use": None,
                "current_tool": "planner",  # Start with planner tool
                "tool_results": {},
                "tool_history": [],  # Track tool execution history
                "synthesis": None,
                "citations": [],
                "answer": None,
                "reasoning": None,
                "error": None,
                "organization_id": filters.get("organization_id", "default") if filters else "default"  # Added for the planner node
            }
            
            # Run the graph
            final_state = await self.graph.ainvoke(initial_state)
            
            # Check for errors
            if final_state.get("error"):
                raise Exception(final_state["error"])
            
            # Return the result
            return {
                "query": query,
                "answer": final_state.get("answer", ""),
                "sources": final_state.get("citations", []),
                "reasoning": final_state.get("reasoning", ""),
                "synthesis": final_state.get("synthesis", "")
            }
        except Exception as e:
            logger.error(f"Error querying RAG system: {str(e)}")
            raise

    def query(self, query: str, filters: Optional[Dict[str, Any]] = None, top_k: int = 5) -> Dict[str, Any]:
        """
        Query the RAG system.
        
        Args:
            query: The query string
            filters: Optional filters to apply
            top_k: Maximum number of results to return
            
        Returns:
            The query result
        """
        # Run the async query in a synchronous context
        return asyncio.run(self.query_async(query, filters, top_k))