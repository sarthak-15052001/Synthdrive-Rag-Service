from typing import Dict, List, Any, Optional
import logging
from openai import OpenAI

from src.core.config import settings
from src.data_stores.weaviate_client import WeaviateClient

# Configure logging
logger = logging.getLogger(__name__)


class GlobalKnowledgeDomain:
    """
    Tool for accessing the Global Knowledge Domain for Vetted AI Tools.
    Uses Weaviate for semantic search on tool descriptions and use cases.
    """

    def __init__(self, weaviate_client: WeaviateClient):
        """
        Initialize the Global Knowledge Domain tool.
        
        Args:
            weaviate_client: The Weaviate client
        """
        self.weaviate_client = weaviate_client
        
        # Initialize OpenAI client for generating explanations
        client_kwargs = {
            "api_key": settings.OPENAI_API_KEY,
        }
        
        # Add organization if available
        if hasattr(settings, 'OPENAI_ORGANIZATION') and settings.OPENAI_ORGANIZATION:
            client_kwargs["organization"] = settings.OPENAI_ORGANIZATION
            
        self.openai_client = OpenAI(**client_kwargs)
    
    async def search_ai_tools(
        self,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 5,
        explain: bool = True
    ) -> Dict[str, Any]:
        """
        Search for AI tools using natural language queries and explain why they match.
        
        Args:
            query: Natural language query (e.g., "tool for video from text")
            filters: Optional filters to apply
            limit: Maximum number of results to return
            explain: Whether to generate explanations for why tools match
            
        Returns:
            Dictionary containing tools and explanations
        """
        logger.info(f"Searching for AI tools with query: {query}")
        
        try:
            # Search for AI tools using the Weaviate client
            tools = self.weaviate_client.search_ai_tools(
                query=query,
                filters=filters,
                limit=limit
            )
            
            # Format the results
            formatted_tools = []
            for tool in tools:
                formatted_tools.append({
                    "name": tool.get("name", "Unknown Tool"),
                    "description": tool.get("description", ""),
                    "use_case": tool.get("use_case", ""),
                    "url": tool.get("url", ""),
                    "pricing": tool.get("pricing", ""),
                    "category": tool.get("category", ""),
                    "rating": tool.get("rating", 0.0),
                    "relevance_score": tool.get("relevance_score", 0.0)
                })
            
            # Generate explanations if requested
            explanations = {}
            if explain and formatted_tools:
                explanations = await self._generate_explanations(query, formatted_tools)
            
            return {
                "query": query,
                "tools": formatted_tools,
                "explanations": explanations
            }
        
        except Exception as e:
            logger.error(f"Error in AI tool search: {str(e)}")
            return {
                "query": query,
                "tools": [],
                "explanations": {},
                "error": str(e)
            }
    
    async def _generate_explanations(self, query: str, tools: List[Dict[str, Any]]) -> Dict[str, str]:
        """
        Generate explanations for why each tool matches the query.
        
        Args:
            query: The original query
            tools: List of tools to explain
            
        Returns:
            Dictionary mapping tool names to explanations
        """
        try:
            # Prepare the prompt
            tool_descriptions = ""
            for i, tool in enumerate(tools):
                tool_descriptions += f"Tool {i+1}: {tool['name']}\n"
                tool_descriptions += f"Description: {tool['description']}\n"
                tool_descriptions += f"Use Case: {tool['use_case']}\n"
                tool_descriptions += f"Category: {tool['category']}\n\n"
            
            prompt = f"""
            You are simulating the SynthDrive system's Global Knowledge Domain for Vetted AI Tools. 
            This uses Weaviate for semantic search on tool descriptions and use cases.
            
            Given this user query: "{query}", the system has performed a semantic search and found the following tools:
            
            {tool_descriptions}
            
            For each tool, explain why it matches the user's query. Focus on how the tool's features, capabilities, 
            and use cases align with what the user is looking for. Be specific and concise.
            
            Format your response as a JSON object where keys are tool names and values are explanations.
            """
            
            # Generate explanations using OpenAI
            response = self.openai_client.chat.completions.create(
                model=settings.LLM_MODEL,
                messages=[
                    {"role": "system", "content": "You are an expert in AI tools and technologies."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            # Parse the response
            import json
            explanations = json.loads(response.choices[0].message.content)
            
            return explanations
        
        except Exception as e:
            logger.error(f"Error generating explanations: {str(e)}")
            return {tool["name"]: "Explanation unavailable" for tool in tools}