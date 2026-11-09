from neo4j import GraphDatabase
from typing import Dict, List, Any, Optional, Tuple
import logging
import json
import uuid
from openai import OpenAI

from src.core.config import settings


class Neo4jClient:
    """
    Client for interacting with Neo4j graph database.
    Uses Cypher for graph queries and LLM for entity/relation extraction.
    Implements connection pooling to prevent resource leaks.
    """

    # Class-level connection pool
    _driver_pool = {}
    
    @classmethod
    def get_driver(cls, uri, user, password):
        """
        Get a driver from the connection pool or create a new one.
        
        Args:
            uri: URI of the Neo4j instance
            user: Username for authentication
            password: Password for authentication
            
        Returns:
            A Neo4j driver instance
        """
        key = f"{uri}:{user}"
        if key not in cls._driver_pool or cls._driver_pool[key] is None:
            cls._driver_pool[key] = GraphDatabase.driver(
                uri,
                auth=(user, password),
                max_connection_lifetime=3600  # 1 hour max connection lifetime
            )
        return cls._driver_pool[key]
    
    @classmethod
    def close_all_drivers(cls):
        """
        Close all drivers in the connection pool.
        """
        for key, driver in cls._driver_pool.items():
            if driver:
                try:
                    driver.close()
                except Exception as e:
                    logging.warning(f"Error closing Neo4j driver {key}: {e}")
        cls._driver_pool.clear()

    def __init__(self, uri: str = None, user: str = None, password: str = None):
        """
        Initialize the Neo4j client.
        
        Args:
            uri: URI of the Neo4j instance
            user: Username for authentication
            password: Password for authentication
        """
        self.uri = uri or settings.NEO4J_URI
        self.user = user or settings.NEO4J_USER
        self.password = password or settings.NEO4J_PASSWORD
        
        # Get driver from connection pool
        self.driver = self.get_driver(self.uri, self.user, self.password)
        
        # Initialize OpenAI client for entity extraction
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
        
        # Ensure constraints and indexes
        self._ensure_constraints()

    def _init_driver(self):
        """
        Initialize the Neo4j driver (legacy method, kept for compatibility).
        """
        return self.get_driver(self.uri, self.user, self.password)

    def _ensure_constraints(self):
        """
        Ensure that the required constraints and indexes exist in Neo4j.
        """
        with self.driver.session() as session:
            # Create constraint on Document nodes
            try:
                session.run("""
                    CREATE CONSTRAINT document_id IF NOT EXISTS
                    FOR (d:Document) REQUIRE d.id IS UNIQUE
                """)
            except Exception as e:
                logging.debug(f"Document ID constraint already exists or error: {e}")
            
            # Create constraint on Entity nodes
            try:
                session.run("""
                    CREATE CONSTRAINT entity_name_tenant IF NOT EXISTS
                    FOR (e:Entity) REQUIRE (e.name, e.tenant_id) IS UNIQUE
                """)
            except Exception as e:
                logging.debug(f"Entity name constraint already exists or error: {e}")
            
            # Create index on Document content for full-text search
            try:
                session.run("""
                    CREATE FULLTEXT INDEX document_content IF NOT EXISTS
                    FOR (d:Document) ON EACH [d.content]
                """)
            except Exception as e:
                logging.debug(f"Document content index already exists or error: {e}")
            
            # Create index on tenant_id for efficient filtering
            try:
                session.run("""
                    CREATE INDEX tenant_id IF NOT EXISTS
                    FOR (d:Document) ON d.tenant_id
                """)
            except Exception as e:
                logging.debug(f"Tenant ID index already exists or error: {e}")

    def extract_entities_and_relations(self, content: str) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Extract entities and relationships from content using LLM.
        
        Args:
            content: The content to extract entities and relationships from
            
        Returns:
            A tuple of (entities, relationships)
        """
        try:
            # Skip extraction for empty content
            if not content or len(content.strip()) == 0:
                logging.warning("Empty content provided for entity extraction")
                return [], []
                
            # Truncate content if it's too long (OpenAI has token limits)
            if len(content) > 8000:
                logging.warning(f"Content too long ({len(content)} chars), truncating to 8000 chars")
                content = content[:8000]
            
            # Configure the OpenAI client with additional options
            client_kwargs = {
                "api_key": settings.OPENAI_API_KEY,
            }
            
            # Add organization if available
            if hasattr(settings, 'OPENAI_ORGANIZATION') and settings.OPENAI_ORGANIZATION:
                client_kwargs["organization"] = settings.OPENAI_ORGANIZATION
                
            # Create the client without the project parameter
            client = OpenAI(**client_kwargs)
            
            # Prompt for the LLM to extract entities and relationships
            prompt = f"""
            Extract named entities and their relationships from the following text.
            Format the response as a JSON object with two arrays: "entities" and "relationships".
            
            For entities, include:
            - name: The entity name
            - type: The entity type (e.g., Person, Organization, Location, Concept, etc.)
            - id: A unique identifier for the entity (use a UUID or similar)
            
            For relationships, include:
            - source: The source entity name
            - target: The target entity name
            - type: The relationship type (e.g., WORKS_FOR, LOCATED_IN, PART_OF, etc.)
            
            Text: {content}
            
            JSON Response:
            """
            
            # Call the LLM to extract entities and relationships
            response = client.chat.completions.create(
                model=settings.LLM_MODEL or "gpt-4o",
                messages=[
                    {"role": "system", "content": "You are an expert in named entity recognition and relationship extraction."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            # Parse the response
            result = json.loads(response.choices[0].message.content)
            
            # Extract entities and relationships
            entities = result.get("entities", [])
            relationships = result.get("relationships", [])
            
            # Add IDs to entities if missing
            for entity in entities:
                if "id" not in entity:
                    entity["id"] = str(uuid.uuid4())
            
            logging.info(f"Extracted {len(entities)} entities and {len(relationships)} relationships")
            return entities, relationships
        
        except Exception as e:
            logging.error(f"Error extracting entities and relationships: {e}")
            return [], []

    def create_graph_nodes(self, doc_id: str, entities: List[Dict[str, Any]], relationships: List[Dict[str, Any]], tenant_id: str = "default") -> None:
        """
        Create graph nodes and relationships in Neo4j.
        
        Args:
            doc_id: The ID of the document
            entities: List of entities extracted from the document
            relationships: List of relationships between entities
            tenant_id: The tenant ID for multi-tenancy support
        """
        try:
            with self.driver.session() as session:
                # Create the document node with tenant_id
                session.run("""
                    MERGE (d:Document {id: $id})
                    SET d.tenant_id = $tenant_id
                """, {
                    "id": doc_id,
                    "tenant_id": tenant_id
                })
                
                # Create entity nodes and relationships to the document
                for entity in entities:
                    try:
                        # Generate a unique ID for the entity if not present
                        entity_id = entity.get("id", str(uuid.uuid4()))
                        
                        # Create the entity and link to document
                        session.run("""
                            MATCH (d:Document {id: $doc_id})
                            MERGE (e:Entity {id: $entity_id, name: $name, tenant_id: $tenant_id})
                            SET e.type = $type
                            MERGE (d)-[:MENTIONS]->(e)
                        """, {
                            "doc_id": doc_id,
                            "entity_id": entity_id,
                            "name": entity["name"],
                            "type": entity["type"],
                            "tenant_id": tenant_id
                        })
                    except Exception as e:
                        logging.warning(f"Error creating entity {entity.get('name')}: {str(e)}")
                        continue
                
                # Create relationships between entities
                for rel in relationships:
                    try:
                        # Sanitize relationship type
                        rel_type = rel["type"].replace(" ", "_").replace("-", "_").upper()
                        
                        # Create properties for the relationship
                        rel_properties = {
                            "tenant_id": tenant_id,
                            "document_id": doc_id
                        }
                        
                        # Add any additional properties from the relationship
                        if "properties" in rel and isinstance(rel["properties"], dict):
                            for key, value in rel["properties"].items():
                                # Handle nested dictionaries by converting them to JSON strings
                                if isinstance(value, dict):
                                    try:
                                        rel_properties[key] = json.dumps(value)
                                    except Exception as e:
                                        logging.warning(f"Error serializing property {key} to JSON: {str(e)}")
                                        # Skip this property
                                        continue
                                else:
                                    # Keep primitive types as is
                                    rel_properties[key] = value
                        
                        # Create the relationship with properties
                        session.run(f"""
                            MATCH (source:Entity {{name: $source, tenant_id: $tenant_id}})
                            MATCH (target:Entity {{name: $target, tenant_id: $tenant_id}})
                            MERGE (source)-[r:{rel_type}]->(target)
                            SET r += $properties
                        """, {
                            "source": rel["source"],
                            "target": rel["target"],
                            "tenant_id": tenant_id,
                            "properties": rel_properties
                        })
                    except Exception as e:
                        logging.warning(f"Error creating relationship {rel.get('type')}: {str(e)}")
                        continue
        except Exception as e:
            logging.error(f"Error creating graph nodes: {str(e)}")

    def traverse_relations(self, query: str, tenant_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Traverse the graph to find relationships matching the query.
        Results are filtered by tenant_id.
        
        Args:
            query: The Cypher query or natural language query
            tenant_id: The tenant ID to filter results by
            limit: Maximum number of results to return
            
        Returns:
            List of paths or relationships matching the query
        """
        # Check if the query is a Cypher query (starts with MATCH, RETURN, etc.)
        is_cypher = any(query.strip().upper().startswith(keyword) for keyword in ["MATCH", "RETURN", "WITH", "CALL"])
        
        with self.driver.session() as session:
            if is_cypher:
                # If it's a Cypher query, execute it directly
                # Add tenant_id filter if not already in the query
                if "tenant_id" not in query:
                    # This is a simple approach; in a real system, you'd need more sophisticated query parsing
                    if "WHERE" in query.upper():
                        query = query.replace("WHERE", f"WHERE n.tenant_id = '{tenant_id}' AND ")
                    else:
                        match_clause_end = query.upper().find("RETURN")
                        if match_clause_end > 0:
                            query = query[:match_clause_end] + f" WHERE n.tenant_id = '{tenant_id}' " + query[match_clause_end:]
                
                result = session.run(query)
            else:
                # If it's a natural language query, convert it to a graph pattern
                # This is a simplified implementation; in a real system, you'd use an LLM to generate Cypher
                
                # Extract entities from the query
                entities, _ = self.extract_entities_and_relations(query)
                entity_names = [entity["name"] for entity in entities]
                
                # Build a query to find paths between entities mentioned in the query
                if len(entity_names) >= 2:
                    # If we have at least two entities, find paths between them
                    result = session.run("""
                        MATCH path = (source:Entity)-[*1..3]-(target:Entity)
                        WHERE source.name IN $entity_names
                        AND target.name IN $entity_names
                        AND source <> target
                        AND source.tenant_id = $tenant_id
                        AND target.tenant_id = $tenant_id
                        RETURN path, length(path) AS path_length
                        ORDER BY path_length
                        LIMIT $limit
                    """, {
                        "entity_names": entity_names,
                        "tenant_id": tenant_id,
                        "limit": limit
                    })
                else:
                    # If we have one or no entities, find documents and entities related to the query
                    result = session.run("""
                        CALL db.index.fulltext.queryNodes("document_content", $query) YIELD node, score
                        WHERE node.tenant_id = $tenant_id
                        MATCH (node)-[:MENTIONS]->(e:Entity)
                        WHERE e.tenant_id = $tenant_id
                        RETURN node.id AS document_id, collect(e) AS entities, score
                        ORDER BY score DESC
                        LIMIT $limit
                    """, {
                        "query": query,
                        "tenant_id": tenant_id,
                        "limit": limit
                    })
            
            # Process the results
            results = []
            for record in result:
                results.append(dict(record))
            
            return results

    def add_document(self, document_id: str, content: str, metadata: Dict[str, Any]) -> None:
        """
        Add a document to Neo4j.
        
        Args:
            document_id: The ID of the document
            content: The content of the document
            metadata: Metadata about the document
        """
        try:
            tenant_id = metadata.get("tenant_id", "default")
            
            # Ensure document_id is not empty
            if not document_id:
                document_id = str(uuid.uuid4())
                
            # Ensure content is not None
            if content is None:
                content = ""
                
            with self.driver.session() as session:
                # Create the document node
                # Convert metadata to JSON string since Neo4j doesn't support nested maps
                try:
                    metadata_json = json.dumps(metadata)
                except Exception as e:
                    logging.warning(f"Error serializing metadata to JSON: {str(e)}")
                    metadata_json = "{}"
                
                # Create or update the document node
                session.run("""
                    MERGE (d:Document {id: $id})
                    SET d.content = $content,
                        d.source = $source,
                        d.created_at = $created_at,
                        d.metadata = $metadata,
                        d.tenant_id = $tenant_id
                """, {
                    "id": document_id,
                    "content": content,
                    "source": metadata.get("source", "unknown"),
                    "created_at": metadata.get("created_at", ""),
                    "metadata": metadata_json,
                    "tenant_id": tenant_id
                })
                
                logging.info(f"Document node created in Neo4j with ID: {document_id}")
                
                try:
                    # Extract entities and relationships using LLM
                    entities, relationships = self.extract_entities_and_relations(content)
                    
                    # Create graph nodes and relationships
                    if entities and relationships:
                        self.create_graph_nodes(document_id, entities, relationships, tenant_id)
                        logging.info(f"Created {len(entities)} entities and {len(relationships)} relationships for document {document_id}")
                    else:
                        logging.warning(f"No entities or relationships extracted for document {document_id}")
                except Exception as e:
                    logging.error(f"Error extracting or storing entities: {str(e)}")
                    # Continue without failing - document is still stored
        except Exception as e:
            logging.error(f"Error adding document to Neo4j: {str(e)}")

    def add_entity(self, entity_id: str, name: str, entity_type: str, properties: Dict[str, Any]) -> None:
        """
        Add an entity to Neo4j.
        
        Args:
            entity_id: The ID of the entity
            name: The name of the entity
            entity_type: The type of the entity
            properties: Additional properties for the entity
        """
        tenant_id = properties.get("tenant_id", "default")
        
        with self.driver.session() as session:
            # Convert properties to JSON string since Neo4j doesn't support nested maps
            properties_json = json.dumps(properties)
            
            session.run("""
                MERGE (e:Entity {id: $id, name: $name, tenant_id: $tenant_id})
                SET e.type = $type,
                    e.properties = $properties
            """, {
                "id": entity_id,
                "name": name,
                "type": entity_type,
                "tenant_id": tenant_id,
                "properties": properties_json
            })

    def add_relationship(self, source_id: str, target_id: str, rel_type: str, properties: Dict[str, Any]) -> None:
        """
        Add a relationship between two entities in Neo4j.
        
        Args:
            source_id: The ID of the source entity
            target_id: The ID of the target entity
            rel_type: The type of the relationship
            properties: Additional properties for the relationship
        """
        tenant_id = properties.get("tenant_id", "default")
        
        with self.driver.session() as session:
            # Sanitize relationship type (Neo4j requires valid characters)
            safe_rel_type = rel_type.replace(" ", "_").replace("-", "_").upper()
            
            # Process properties to ensure they are Neo4j compatible
            processed_properties = {}
            for key, value in properties.items():
                # Handle nested dictionaries by converting them to JSON strings
                if isinstance(value, dict):
                    try:
                        processed_properties[key] = json.dumps(value)
                    except Exception as e:
                        logging.warning(f"Error serializing property {key} to JSON: {str(e)}")
                        # Skip this property
                        continue
                else:
                    # Keep primitive types as is
                    processed_properties[key] = value
            
            try:
                session.run(f"""
                    MATCH (source {{id: $source_id, tenant_id: $tenant_id}})
                    MATCH (target {{id: $target_id, tenant_id: $tenant_id}})
                    MERGE (source)-[r:{safe_rel_type}]->(target)
                    SET r += $properties
                """, {
                    "source_id": source_id,
                    "target_id": target_id,
                    "tenant_id": tenant_id,
                    "properties": processed_properties
                })
            except Exception as e:
                logging.error(f"Error storing relationship in Neo4j: {str(e)}")
                raise

    def get_document_by_id(self, document_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a document from Neo4j by ID.
        
        Args:
            document_id: The ID of the document
            
        Returns:
            The document or None if not found
        """
        with self.driver.session() as session:
            result = session.run("""
                MATCH (d:Document {id: $id})
                RETURN d.id AS id, d.content AS content, d.source AS source,
                       d.created_at AS created_at, d.metadata AS metadata,
                       d.tenant_id AS tenant_id
            """, {"id": document_id})
            
            record = result.single()
            if record:
                return {
                    "id": record["id"],
                    "content": record["content"],
                    "source": record["source"],
                    "created_at": record["created_at"],
                    "metadata": record["metadata"],
                    "tenant_id": record["tenant_id"]
                }
            
            return None

    def get_related_documents(self, document_id: str, tenant_id: str = None, max_depth: int = 2, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Get documents related to the given document through entity relationships.
        
        Args:
            document_id: The ID of the document
            tenant_id: Optional tenant ID to filter results
            max_depth: Maximum path depth for relationships
            limit: Maximum number of results to return
            
        Returns:
            List of related documents
        """
        with self.driver.session() as session:
            query = """
                MATCH (d:Document {id: $id})
                MATCH (d)-[:MENTIONS]->(e:Entity)<-[:MENTIONS]-(related:Document)
                WHERE d <> related
            """
            
            if tenant_id:
                query += " AND related.tenant_id = $tenant_id"
            
            query += """
                RETURN related.id AS id, related.content AS content, related.source AS source,
                       related.created_at AS created_at, related.metadata AS metadata,
                       related.tenant_id AS tenant_id,
                       count(e) AS shared_entities
                ORDER BY shared_entities DESC
                LIMIT $limit
            """
            
            params = {
                "id": document_id,
                "limit": limit
            }
            
            if tenant_id:
                params["tenant_id"] = tenant_id
            
            result = session.run(query, params)
            
            documents = []
            for record in result:
                documents.append({
                    "id": record["id"],
                    "content": record["content"],
                    "source": record["source"],
                    "created_at": record["created_at"],
                    "metadata": record["metadata"],
                    "tenant_id": record["tenant_id"],
                    "shared_entities": record["shared_entities"]
                })
            
            return documents

    def search_documents(self, query: str, tenant_id: str = None, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search for documents in Neo4j using full-text search.
        
        Args:
            query: The search query
            tenant_id: Optional tenant ID to filter results
            limit: Maximum number of results to return
            
        Returns:
            List of matching documents
        """
        with self.driver.session() as session:
            query_str = """
                CALL db.index.fulltext.queryNodes("document_content", $query)
                YIELD node, score
            """
            
            if tenant_id:
                query_str += " WHERE node.tenant_id = $tenant_id"
            
            query_str += """
                RETURN node.id AS id, node.content AS content, node.source AS source,
                       node.created_at AS created_at, node.metadata AS metadata,
                       node.tenant_id AS tenant_id,
                       score
                ORDER BY score DESC
                LIMIT $limit
            """
            
            params = {
                "query": query,
                "limit": limit
            }
            
            if tenant_id:
                params["tenant_id"] = tenant_id
            
            result = session.run(query_str, params)
            
            documents = []
            for record in result:
                documents.append({
                    "id": record["id"],
                    "content": record["content"],
                    "source": record["source"],
                    "created_at": record["created_at"],
                    "metadata": record["metadata"],
                    "tenant_id": record["tenant_id"],
                    "score": record["score"]
                })
            
            return documents
    
    def query(self, cypher_query: str, parameters: Dict[str, Any] = None) -> Any:
        """
        Execute a Cypher query on Neo4j.
        
        Args:
            cypher_query: The Cypher query to execute
            parameters: Parameters for the query
            
        Returns:
            Query results
        """
        with self.driver.session() as session:
            result = session.run(cypher_query, parameters or{})
            # Return the summary or records as needed
            return result.consume()

    def close(self):
        """
        Close the Neo4j driver.
        Note: This doesn't actually close the driver, but removes it from the instance.
        The driver is managed by the connection pool and will be closed when the application shuts down.
        """
        # Remove reference to the driver, but don't close it
        # as it might be used by other instances
        self.driver = None