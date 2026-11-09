from typing import Dict, List, Any, Optional
import logging
from openai import OpenAI

from src.core.config import settings
from src.data_stores.weaviate_client import WeaviateClient

# Configure logging
logger = logging.getLogger(__name__)


class VectorSearchTool:
    """
    Tool for semantic similarity search using Weaviate.
    Provides methods for searching documents and AI tools.
    """

    def __init__(self, weaviate_client: WeaviateClient):
        """
        Initialize the vector search tool.
        
        Args:
            weaviate_client: The Weaviate client
        """
        self.weaviate_client = weaviate_client
        
        # Initialize OpenAI client for embeddings
        # Handle both standard and project-based API keys
        api_key = settings.OPENAI_API_KEY
        
        # Configure the OpenAI client with additional options
        client_kwargs = {
            "api_key": api_key,
        }
        
        # Add organization if available
        if hasattr(settings, 'OPENAI_ORGANIZATION') and settings.OPENAI_ORGANIZATION:
            client_kwargs["organization"] = settings.OPENAI_ORGANIZATION
            
        # Create the client without the project parameter
        self.openai_client = OpenAI(**client_kwargs)
    
    async def search(
        self, 
        query: str, 
        filters: Optional[Dict[str, Any]] = None, 
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Perform semantic search using Weaviate.
        
        Args:
            query: The query string
            filters: Optional filters to apply
            limit: Maximum number of results to return
            
        Returns:
            List of documents matching the query
        """
        logger.info(f"Performing vector search for: {query}")
        
        try:
            # Query documents from Weaviate
            documents = self.weaviate_client.query_documents(
                query=query,
                filters=filters,
                limit=limit
            )
            
            # Format the results with citation information
            results = []
            for i, doc in enumerate(documents):
                results.append({
                    "content": doc.get("content", ""),
                    "metadata": doc.get("metadata", {}),
                    "source": doc.get("source", "unknown"),
                    "relevance_score": doc.get("relevance_score", 0.0),
                    "citation_id": f"vector-{i+1}"
                })
            
            logger.info(f"Vector search returned {len(results)} results")
            return results
        
        except Exception as e:
            logger.error(f"Error in vector search: {str(e)}")
            return []
    
    async def hybrid_search(
        self, 
        query: str, 
        filters: Optional[Dict[str, Any]] = None, 
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Perform hybrid search (semantic + keyword) using Weaviate.
        
        Args:
            query: The query string
            filters: Optional filters to apply
            limit: Maximum number of results to return
            
        Returns:
            List of documents matching the query
        """
        logger.info(f"Performing hybrid search for: {query}")
        
        try:
            # In a full implementation, you would use Weaviate's hybrid search capabilities
            # For now, we'll just use the standard semantic search
            
            documents = self.weaviate_client.query_documents(
                query=query,
                filters=filters,
                limit=limit
            )
            
            # Format the results with citation information
            results = []
            for i, doc in enumerate(documents):
                results.append({
                    "content": doc.get("content", ""),
                    "metadata": doc.get("metadata", {}),
                    "source": doc.get("source", "unknown"),
                    "relevance_score": doc.get("relevance_score", 0.0),
                    "citation_id": f"hybrid-{i+1}"
                })
            
            logger.info(f"Hybrid search returned {len(results)} results")
            return results
        
        except Exception as e:
            logger.error(f"Error in hybrid search: {str(e)}")
            return []
    
    async def multi_query_search(
        self, 
        query: str, 
        filters: Optional[Dict[str, Any]] = None, 
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Perform multi-query search by generating variations of the original query.
        
        Args:
            query: The query string
            filters: Optional filters to apply
            limit: Maximum number of results to return
            
        Returns:
            List of documents matching the query
        """
        logger.info(f"Performing multi-query search for: {query}")
        
        try:
            # Generate query variations using OpenAI
            prompt = f"""
            Generate 3 different variations of the following query that might retrieve different but relevant information.
            Make the variations diverse in their phrasing and focus.
            
            Original query: {query}
            
            Return a JSON array of strings, where each string is a query variation.
            """
            
            response = self.openai_client.chat.completions.create(
                model=settings.LLM_MODEL,
                messages=[
                    {"role": "system", "content": "You are an expert in generating query variations for retrieval systems."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            # Parse the response
            import json
            result = json.loads(response.choices[0].message.content)
            query_variations = result.get("queries", [query])
            
            # Ensure we have the original query
            if query not in query_variations:
                query_variations.append(query)
            
            # Perform search for each query variation
            all_results = []
            for i, variation in enumerate(query_variations):
                # Limit the number of results per variation
                per_variation_limit = max(2, limit // len(query_variations))
                
                documents = self.weaviate_client.query_documents(
                    query=variation,
                    filters=filters,
                    limit=per_variation_limit
                )
                
                # Format and add to results
                for j, doc in enumerate(documents):
                    all_results.append({
                        "content": doc.get("content", ""),
                        "metadata": doc.get("metadata", {}),
                        "source": doc.get("source", "unknown"),
                        "relevance_score": doc.get("relevance_score", 0.0),
                        "citation_id": f"multi-{i+1}-{j+1}",
                        "query_variation": variation
                    })
            
            # Remove duplicates (simplified approach)
            unique_results = []
            seen_contents = set()
            
            for result in all_results:
                content = result["content"]
                if content not in seen_contents:
                    seen_contents.add(content)
                    unique_results.append(result)
            
            # Limit to the requested number
            final_results = unique_results[:limit]
            
            logger.info(f"Multi-query search returned {len(final_results)} results")
            return final_results
        
        except Exception as e:
            logger.error(f"Error in multi-query search: {str(e)}")
            return []
            
    async def search_ai_tools(
        self,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search for AI tools using natural language queries.
        
        Args:
            query: Natural language query (e.g., "find a tool to make videos from text")
            filters: Optional filters to apply (e.g., {"category": "video"})
            limit: Maximum number of results to return
            
        Returns:
            List of AI tools matching the query with citation information
        """
        logger.info(f"Searching for AI tools with query: {query}")
        
        try:
            # Use the specialized search_ai_tools method from the Weaviate client
            tools = self.weaviate_client.search_ai_tools(
                query=query,
                filters=filters,
                limit=limit
            )
            
            # Format the results with citation information
            results = []
            for i, tool in enumerate(tools):
                results.append({
                    "name": tool.get("name", "Unknown Tool"),
                    "description": tool.get("description", ""),
                    "use_case": tool.get("use_case", ""),
                    "url": tool.get("url", ""),
                    "pricing": tool.get("pricing", ""),
                    "category": tool.get("category", ""),
                    "rating": tool.get("rating", 0.0),
                    "relevance_score": tool.get("relevance_score", 0.0),
                    "citation_id": f"tool-{i+1}"
                })
            
            logger.info(f"AI tool search returned {len(results)} results")
            return results
        
        except Exception as e:
            logger.error(f"Error in AI tool search: {str(e)}")
            return []