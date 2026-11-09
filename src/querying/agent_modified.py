from typing import Dict, List, Any, Optional, TypedDict, Annotated, Literal, Union, Tuple
import logging
import json
import asyncio
from openai import OpenAI
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_core.tools import Tool

from src.core.config import settings
from src.data_stores.postgres_client import PostgresClient
from src.data_stores.weaviate_client import WeaviateClient
from src.data_stores.neo4j_client import Neo4jClient
from src.querying.tools.vector_search import VectorSearchTool
from src.querying.tools.graph_retrieval import GraphRetrievalTool

# Configure logging
logger = logging.getLogger(__name__)


# Define the agent state
class AgentState(TypedDict):
    query: str
    filters: Optional[Dict[str, Any]]
    top_k: int
    chat_history: List[Dict[str, Any]]
    retrieved_docs: Dict[str, List[Dict[str, Any]]]
    plan: Optional[List[str]]
    tools_to_use: Optional[List[str]]
    current_tool: Optional[str]
    tool_results: Dict[str, Any]
    synthesis: Optional[str]
    citations: List[Dict[str, Any]]
    answer: Optional[str]
    reasoning: Optional[str]
    error: Optional[str]


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
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
        
        # Initialize tools
        self.vector_search_tool = VectorSearchTool(weaviate_client)
        self.graph_retrieval_tool = GraphRetrievalTool(neo4j_client)
        
        # Build the agent graph
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """
        Build the agent graph.
        
        Returns:
            The agent graph
        """
        # Define the tools
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "vector_search",
                    "description": "Search for documents using vector similarity",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "The query string"
                            },
                            "filters": {
                                "type": "object",
                                "description": "Optional filters to apply"
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Maximum number of results to return"
                            }
                        },
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "graph_traversal",
                    "description": "Traverse the graph to find relationships",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "The query string"
                            },
                            "tenant_id": {
                                "type": "string",
                                "description": "The tenant ID to filter results by"
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Maximum number of results to return"
                            }
                        },
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "generate_cypher",
                    "description": "Generate a Cypher query from natural language",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "The natural language query"
                            }
                        },
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "multi_query_search",
                    "description": "Perform search with multiple query variations",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "The query string"
                            },
                            "filters": {
                                "type": "object",
                                "description": "Optional filters to apply"
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Maximum number of results to return"
                            }
                        },
                        "required": ["query"]
                    }
                }
            }
        ]
        
        # Create a tool executor
        async def execute_tool(tool_name: str, tool_input: Dict[str, Any]) -> Any:
            """Execute a tool with the given input."""
            try:
                if tool_name == "vector_search":
                    return await self.vector_search_tool.search(
                        query=tool_input.get("query", ""),
                        filters=tool_input.get("filters"),
                        limit=tool_input.get("limit", 5)
                    )
                elif tool_name == "graph_traversal":
                    return await self.graph_retrieval_tool.traverse_relations(
                        query=tool_input.get("query", ""),
                        tenant_id=tool_input.get("tenant_id", "default"),
                        limit=tool_input.get("limit", 5)
                    )
                elif tool_name == "generate_cypher":
                    return await self.graph_retrieval_tool.generate_cypher(
                        query=tool_input.get("query", "")
                    )
                elif tool_name == "multi_query_search":
                    return await self.vector_search_tool.multi_query_search(
                        query=tool_input.get("query", ""),
                        filters=tool_input.get("filters"),
                        limit=tool_input.get("limit", 5)
                    )
                else:
                    return {"error": f"Unknown tool: {tool_name}"}
            except Exception as e:
                logger.error(f"Error executing tool {tool_name}: {str(e)}")
                return {"error": str(e)}
        
        # Convert the tool definitions to BaseTool objects
        tool_objects = []
        for tool_def in tools:
            if tool_def["type"] == "function":
                func_def = tool_def["function"]
                
                # Create a tool function that calls our execute_tool function
                async def tool_func(tool_name=func_def["name"], **kwargs):
                    return await execute_tool(tool_name, kwargs)
                
                # Create a Tool object
                tool = Tool(
                    name=func_def["name"],
                    description=func_def["description"],
                    func=lambda **kwargs: asyncio.run(tool_func(tool_name=func_def["name"], **kwargs)),
                    coroutine=tool_func
                )
                tool_objects.append(tool)
        
        # Create the tool node with the tool objects
        tool_node = ToolNode(tool_objects)
        
        # Define a custom agent node instead of using create_react_agent
        async def agent_node(state: AgentState) -> AgentState:
            """
            Custom agent node that uses OpenAI to decide which tool to use.
            """
            query = state["query"]
            chat_history = state.get("chat_history", [])
            tool_results = state.get("tool_results", {})
            
            # If we have a plan, use it to decide which tool to use
            plan = state.get("plan", [])
            tools_to_use = state.get("tools_to_use", [])
            
            # Format tool results for the prompt
            tool_results_str = ""
            for tool_name, result in tool_results.items():
                tool_results_str += f"\n\nTool: {tool_name}\nResult: {json.dumps(result, indent=2)}"
            
            # Create the prompt
            prompt = f"""
            You are an expert RAG system agent that helps users find information.
            You have access to multiple tools for retrieving information:
            - vector_search: For semantic similarity search
            - graph_traversal: For finding relationships in the knowledge graph
            - generate_cypher: For generating Cypher queries for complex graph patterns
            - multi_query_search: For searching with multiple query variations
            
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
                
                # Update the state
                return {
                    **state,
                    "current_tool": tool_name,
                    "tool_input": tool_input
                }
            elif action == "finish":
                # We're done, move to synthesis
                return {
                    **state,
                    "current_tool": "FINISH"
                }
            else:
                # Invalid action
                return {
                    **state,
                    "error": f"Invalid action: {action}"
                }
        
        # Define the agent state
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("agent", agent_node)
        workflow.add_node("tools", tool_node)
        workflow.add_node("plan", self._create_plan)
        workflow.add_node("synthesize", self._synthesize_results)
        
        # Add edges
        workflow.add_edge("plan", "agent")
        workflow.add_edge("agent", "tools")
        workflow.add_edge("tools", "agent")
        workflow.add_edge("agent", "synthesize")
        workflow.add_edge("synthesize", END)
        
        # Set the entry point
        workflow.set_entry_point("plan")
        
        # Conditional edges
        def should_end(state: AgentState) -> Literal["agent", "synthesize"]:
            """Determine if the agent should continue or synthesize results."""
            if state.get("current_tool") == "FINISH":
                return "synthesize"
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
            
            # Initialize the chat history
            chat_history = [
                {"role": "system", "content": "You are an expert RAG system agent that helps users find information."},
                {"role": "user", "content": query}
            ]
            
            # Add the plan to the chat history
            plan_message = "I'll help you answer this query. Here's my plan:\n"
            for i, step in enumerate(plan):
                plan_message += f"{i+1}. {step}\n"
            
            chat_history.append({"role": "assistant", "content": plan_message})
            
            return {
                **state,
                "plan": plan,
                "tools_to_use": tools_to_use,
                "chat_history": chat_history,
                "retrieved_docs": {},
                "tool_results": {},
                "citations": []
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
            
            for tool_name, results in tool_results.items():
                if isinstance(results, list):
                    for i, doc in enumerate(results):
                        citation_id = doc.get("citation_id", f"{tool_name}-{i+1}")
                        
                        all_docs.append({
                            "tool": tool_name,
                            "content": doc.get("content", ""),
                            "citation_id": citation_id
                        })
                        
                        citations.append({
                            "id": citation_id,
                            "tool": tool_name,
                            "source": doc.get("source", "unknown"),
                            "content": doc.get("content", "")[:200] + "..." if len(doc.get("content", "")) > 200 else doc.get("content", ""),
                            "metadata": doc.get("metadata", {})
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
            initial_state: AgentState = {
                "query": query,
                "filters": filters,
                "top_k": top_k,
                "chat_history": [],
                "retrieved_docs": {},
                "plan": None,
                "tools_to_use": None,
                "current_tool": None,
                "tool_results": {},
                "synthesis": None,
                "citations": [],
                "answer": None,
                "reasoning": None,
                "error": None
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