from typing import Dict, List, Any, Optional, Union
import logging
import json
from openai import OpenAI

from src.core.config import settings
from src.data_stores.neo4j_client import Neo4jClient

# Configure logging
logger = logging.getLogger(__name__)


class GraphRetrievalTool:
    """
    Tool for traversing Neo4j graph database for relationship-based retrieval.
    """

    def __init__(self, neo4j_client: Neo4jClient):
        """
        Initialize the graph retrieval tool.
        
        Args:
            neo4j_client: The Neo4j client
        """
        self.neo4j_client = neo4j_client
        
        # Initialize OpenAI client for query generation
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
    
    async def traverse_relations(
        self, 
        query: str, 
        tenant_id: str = "default", 
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Traverse the graph to find relationships matching the query.
        
        Args:
            query: The query string
            tenant_id: The tenant ID to filter results by
            limit: Maximum number of results to return
            
        Returns:
            List of paths or relationships matching the query
        """
        logger.info(f"Traversing graph relations for: {query}")
        
        try:
            # Use the Neo4j client to traverse relations
            results = self.neo4j_client.traverse_relations(
                query=query,
                tenant_id=tenant_id,
                limit=limit
            )
            
            # Format the results with citation information
            formatted_results = []
            for i, result in enumerate(results):
                # Extract document ID if available
                doc_id = result.get("document_id") if "document_id" in result else None
                
                # If we have a document ID, get the full document
                if doc_id:
                    document = self.neo4j_client.get_document_by_id(doc_id)
                    if document:
                        formatted_results.append({
                            "content": document.get("content", ""),
                            "metadata": document.get("metadata", {}),
                            "source": document.get("source", "unknown"),
                            "citation_id": f"graph-doc-{i+1}",
                            "graph_context": result
                        })
                else:
                    # For other types of results (paths, entities, etc.)
                    formatted_results.append({
                        "content": str(result),  # Convert to string for consistency
                        "metadata": {"type": "graph_result"},
                        "source": "graph_database",
                        "citation_id": f"graph-rel-{i+1}",
                        "graph_context": result
                    })
            
            logger.info(f"Graph traversal returned {len(formatted_results)} results")
            return formatted_results
        
        except Exception as e:
            logger.error(f"Error in graph traversal: {str(e)}")
            return []
    
    async def generate_cypher(self, query: str) -> str:
        """
        Generate a Cypher query from a natural language query using LLM.
        
        Args:
            query: The natural language query
            
        Returns:
            A Cypher query
        """
        logger.info(f"Generating Cypher for query: {query}")
        
        try:
            # Use OpenAI to generate a Cypher query
            prompt = f"""
            Convert the following natural language query into a Cypher query for Neo4j.
            The database has the following structure:
            - Document nodes with properties: id, content, source, created_at, tenant_id
            - Entity nodes with properties: name, type, tenant_id
            - MENTIONS relationships from Document to Entity
            - Various relationships between Entity nodes based on their semantic connections
            
            Natural language query: {query}
            
            Return only the Cypher query without any explanations or markdown formatting.
            """
            
            response = self.openai_client.chat.completions.create(
                model=settings.LLM_MODEL,
                messages=[
                    {"role": "system", "content": "You are an expert in converting natural language to Cypher queries for Neo4j."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            cypher_query = response.choices[0].message.content.strip()
            
            # Remove any markdown code block formatting if present
            if cypher_query.startswith("```") and cypher_query.endswith("```"):
                cypher_query = cypher_query[3:-3].strip()
            
            if cypher_query.startswith("```cypher") and cypher_query.endswith("```"):
                cypher_query = cypher_query[9:-3].strip()
            
            logger.info(f"Generated Cypher query: {cypher_query}")
            return cypher_query
        
        except Exception as e:
            logger.error(f"Error generating Cypher query: {str(e)}")
            return ""
    
    async def execute_cypher(
        self, 
        cypher_query: str, 
        tenant_id: str = "default"
    ) -> List[Dict[str, Any]]:
        """
        Execute a Cypher query and format the results.
        
        Args:
            cypher_query: The Cypher query to execute
            tenant_id: The tenant ID to filter results by
            
        Returns:
            The query results
        """
        logger.info(f"Executing Cypher query: {cypher_query}")
        
        try:
            # Add tenant_id filter if not already in the query
            if "tenant_id" not in cypher_query:
                # This is a simple approach; in a real system, you'd need more sophisticated query parsing
                if "WHERE" in cypher_query.upper():
                    cypher_query = cypher_query.replace("WHERE", f"WHERE n.tenant_id = '{tenant_id}' AND ")
                else:
                    match_clause_end = cypher_query.upper().find("RETURN")
                    if match_clause_end > 0:
                        cypher_query = cypher_query[:match_clause_end] + f" WHERE n.tenant_id = '{tenant_id}' " + cypher_query[match_clause_end:]
            
            # Execute the query using the Neo4j client
            # In a real implementation, you would have a method to execute arbitrary Cypher
            # For now, we'll use the traverse_relations method which can handle Cypher
            results = self.neo4j_client.traverse_relations(
                query=cypher_query,
                tenant_id=tenant_id
            )
            
            # Format the results with citation information
            formatted_results = []
            for i, result in enumerate(results):
                formatted_results.append({
                    "content": str(result),  # Convert to string for consistency
                    "metadata": {"type": "cypher_result"},
                    "source": "graph_database",
                    "citation_id": f"cypher-{i+1}",
                    "cypher_query": cypher_query
                })
            
            logger.info(f"Cypher query returned {len(formatted_results)} results")
            return formatted_results
        
        except Exception as e:
            logger.error(f"Error executing Cypher query: {str(e)}")
            return []
    
    async def find_related_entities(
        self, 
        entity_name: str, 
        tenant_id: str = "default", 
        max_depth: int = 2, 
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Find entities related to the given entity.
        
        Args:
            entity_name: The name of the entity
            tenant_id: The tenant ID to filter results by
            max_depth: Maximum path depth for relationships
            limit: Maximum number of results to return
            
        Returns:
            List of related entities
        """
        logger.info(f"Finding entities related to: {entity_name}")
        
        try:
            # Create a Cypher query to find related entities
            cypher_query = f"""
            MATCH (e:Entity {{name: '{entity_name}', tenant_id: '{tenant_id}'}})-[r*1..{max_depth}]-(related:Entity)
            WHERE related.tenant_id = '{tenant_id}' AND e <> related
            RETURN related.name AS name, related.type AS type, 
                   [rel IN r | type(rel)] AS relationship_types,
                   length(r) AS distance
            ORDER BY distance
            LIMIT {limit}
            """
            
            # Execute the query
            results = await self.execute_cypher(cypher_query, tenant_id)
            
            logger.info(f"Found {len(results)} entities related to {entity_name}")
            return results
        
        except Exception as e:
            logger.error(f"Error finding related entities: {str(e)}")
            return []
    
    async def find_paths_between_entities(
        self, 
        source_entity: str, 
        target_entity: str, 
        tenant_id: str = "default", 
        max_depth: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Find paths between two entities.
        
        Args:
            source_entity: The source entity name
            target_entity: The target entity name
            tenant_id: The tenant ID to filter results by
            max_depth: Maximum path depth
            
        Returns:
            List of paths between the entities
        """
        logger.info(f"Finding paths between {source_entity} and {target_entity}")
        
        try:
            # Create a Cypher query to find paths
            cypher_query = f"""
            MATCH path = (source:Entity {{name: '{source_entity}', tenant_id: '{tenant_id}'}})-[r*1..{max_depth}]-(target:Entity {{name: '{target_entity}', tenant_id: '{tenant_id}'}})
            WHERE source <> target
            RETURN path, length(path) AS path_length
            ORDER BY path_length
            LIMIT 5
            """
            
            # Execute the query
            results = await self.execute_cypher(cypher_query, tenant_id)
            
            logger.info(f"Found {len(results)} paths between {source_entity} and {target_entity}")
            return results
        
        except Exception as e:
            logger.error(f"Error finding paths between entities: {str(e)}")
            return []
    
    async def extract_entities_from_query(self, query: str) -> List[str]:
        """
        Extract entity names from a query using LLM.
        
        Args:
            query: The query string
            
        Returns:
            List of entity names
        """
        logger.info(f"Extracting entities from query: {query}")
        
        try:
            # Use OpenAI to extract entities
            prompt = f"""
            Extract the names of entities (people, organizations, locations, concepts, etc.) from the following query.
            Return a JSON array of strings, where each string is an entity name.
            
            Query: {query}
            """
            
            response = self.openai_client.chat.completions.create(
                model=settings.LLM_MODEL,
                messages=[
                    {"role": "system", "content": "You are an expert in named entity recognition."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            # Parse the response
            result = json.loads(response.choices[0].message.content)
            entities = result.get("entities", [])
            
            logger.info(f"Extracted {len(entities)} entities from query")
            return entities
        
        except Exception as e:
            logger.error(f"Error extracting entities from query: {str(e)}")
            return []