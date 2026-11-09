"""
Neo4j GraphRAG Client using neo4j-graphrag-python library.
This client provides advanced graph RAG capabilities including knowledge graph construction,
entity extraction, and hybrid vector+graph retrieval.
"""

from typing import Dict, List, Any, Optional, Tuple
import logging
from neo4j import GraphDatabase
from neo4j_graphrag.retrievers import VectorRetriever, VectorCypherRetriever, HybridRetriever
from neo4j_graphrag.llm import OpenAILLM
from neo4j_graphrag.embeddings import OpenAIEmbeddings
from neo4j_graphrag.experimental.components.entity_relation_extractor import (
    LLMEntityRelationExtractor,
    OnError,
)
from neo4j_graphrag.experimental.pipeline import Pipeline
from neo4j_graphrag.experimental.pipeline.kg_builder import SimpleKGPipeline

from src.core.config import settings
import uuid

logger = logging.getLogger(__name__)


class Neo4jGraphRAGClient:
    """
    Advanced Neo4j GraphRAG client using neo4j-graphrag-python library.
    Provides knowledge graph construction, entity extraction, and hybrid retrieval.
    """

    def __init__(self, uri: str = None, user: str = None, password: str = None,
                 max_retries: int = 3, timeout: int = 30):
        """
        Initialize the Neo4j GraphRAG client.
        
        Args:
            uri: URI of the Neo4j instance
            user: Username for authentication
            password: Password for authentication
            max_retries: Maximum number of connection retries
            timeout: Connection timeout in seconds
        """
        self.uri = uri or settings.NEO4J_URI
        self.user = user or settings.NEO4J_USER
        self.password = password or settings.NEO4J_PASSWORD
        self.max_retries = max_retries
        self.timeout = timeout
        
        # Initialize Neo4j driver with retry logic
        retry_count = 0
        last_error = None
        
        while retry_count < self.max_retries:
            try:
                self.driver = GraphDatabase.driver(
                    self.uri,
                    auth=(self.user, self.password),
                    max_transaction_retry_time=self.timeout
                )
                # Verify connection
                self.driver.verify_connectivity()
                logger.info("Successfully connected to Neo4j")
                break
            except Exception as e:
                retry_count += 1
                last_error = e
                wait_time = 2 ** retry_count  # Exponential backoff
                logger.warning(f"Connection attempt {retry_count} failed: {e}. Retrying in {wait_time} seconds...")
                import time
                time.sleep(wait_time)
        
        if retry_count == self.max_retries:
            logger.error(f"Failed to connect to Neo4j after {self.max_retries} attempts. Last error: {last_error}")
            raise Exception(f"Could not establish Neo4j connection: {last_error}")
        
        # Initialize LLM for entity extraction
        self.llm = OpenAILLM(
            model_name=settings.LLM_MODEL,
            api_key=settings.OPENAI_API_KEY
        )
        
        # Initialize embeddings
        self.embedder = OpenAIEmbeddings(
            model=settings.EMBEDDING_MODEL,
            api_key=settings.OPENAI_API_KEY
        )
        
        # Initialize entity-relation extractor
        self.entity_extractor = LLMEntityRelationExtractor(
            llm=self.llm,
            on_error=OnError.RAISE
        )
        
        # Ensure constraints and indexes
        self._ensure_constraints()
        self._ensure_tool_constraints()

    def _ensure_tool_constraints(self):
        """
        Ensure that the required constraints and indexes exist for tools and learning resources in Neo4j.
        """
        with self.driver.session() as session:
            # Tool constraints
            session.run("""
                CREATE CONSTRAINT tool_id IF NOT EXISTS
                FOR (t:Tool) REQUIRE t.id IS UNIQUE
            """)
            
            session.run("""
                CREATE CONSTRAINT feature_id IF NOT EXISTS
                FOR (f:Feature) REQUIRE f.id IS UNIQUE
            """)
            
            session.run("""
                CREATE CONSTRAINT subscription_id IF NOT EXISTS
                FOR (s:Subscription) REQUIRE s.id IS UNIQUE
            """)
            
            # Learning resource constraints
            session.run("""
                CREATE CONSTRAINT learning_resource_id IF NOT EXISTS
                FOR (r:LearningResource) REQUIRE r.id IS UNIQUE
            """)
            
            session.run("""
                CREATE CONSTRAINT topic_name IF NOT EXISTS
                FOR (t:Topic) REQUIRE t.name IS UNIQUE
            """)
            
            session.run("""
                CREATE CONSTRAINT job_role_name IF NOT EXISTS
                FOR (j:JobRole) REQUIRE j.name IS UNIQUE
            """)
            
            session.run("""
                CREATE CONSTRAINT context_name IF NOT EXISTS
                FOR (c:Context) REQUIRE c.name IS UNIQUE
            """)
            
            # Indexes
            session.run("""
                CREATE INDEX tool_name IF NOT EXISTS
                FOR (t:Tool) ON (t.name)
            """)
            
            session.run("""
                CREATE INDEX learning_resource_title IF NOT EXISTS
                FOR (r:LearningResource) ON (r.title)
            """)
            
            session.run("""
                CREATE INDEX learning_resource_type IF NOT EXISTS
                FOR (r:LearningResource) ON (r.resource_type)
            """)
        
    def _ensure_constraints(self):
        """
        Ensure that the required constraints and indexes exist in Neo4j.
        """
        with self.driver.session() as session:
            # Create constraint on Document nodes
            session.run("""
                CREATE CONSTRAINT document_id IF NOT EXISTS
                FOR (d:Document) REQUIRE d.id IS UNIQUE
            """)
            
            # Create constraint on Entity nodes
            session.run("""
                CREATE CONSTRAINT entity_id IF NOT EXISTS
                FOR (e:Entity) REQUIRE e.id IS UNIQUE
            """)
            
            # Create vector index for Document embeddings
            try:
                session.run("""
                    CREATE VECTOR INDEX document_embeddings IF NOT EXISTS
                    FOR (d:Document) ON (d.embedding)
                    OPTIONS {indexConfig: {
                        `vector.dimensions`: 1536,
                        `vector.similarity_function`: 'cosine'
                    }}
                """)
            except Exception as e:
                logger.warning(f"Could not create vector index (may already exist): {e}")
            
            # Create index on tenant_id for efficient filtering
            session.run("""
                CREATE INDEX tenant_id IF NOT EXISTS
                FOR (d:Document) ON (d.tenant_id)
            """)
            
            # Create index on Entity names
            session.run("""
                CREATE INDEX entity_name IF NOT EXISTS
                FOR (e:Entity) ON (e.name)
            """)

    def build_knowledge_graph(
        self,
        text: str,
        doc_id: str,
        metadata: Optional[Dict[str, Any]] = None,
        tenant_id: str = "default",
        retry_count: int = 0
    ) -> Dict[str, Any]:
        """
        Build a knowledge graph from text by extracting entities and relationships.
        
        Args:
            text: The text to process
            doc_id: The document ID
            metadata: Optional metadata
            tenant_id: The tenant ID for multi-tenancy
            
        Returns:
            Dictionary with extraction results
        """
        try:
            # Add session retry logic
            max_session_retries = 3
            current_retry = retry_count
            
            if current_retry >= max_session_retries:
                logger.error(f"Exceeded maximum retries ({max_session_retries}) for building knowledge graph")
                raise Exception("Maximum retries exceeded for building knowledge graph")
            # Use simplified entity extraction (avoiding async issues)
            # Extract entities using direct LLM call instead of async extractor
            import json as json_module
            
            prompt = f"""Extract entities and relationships from this text.
You must return ONLY valid JSON with this exact structure:
{{
  "entities": [
    {{"name": "entity name", "type": "Person|Organization|Location|Technology|Concept"}}
  ],
  "relationships": [
    {{"source": "entity1", "target": "entity2", "type": "relationship type"}}
  ]
}}

Do not include any explanatory text, only the JSON object.

Text: {text}"""
            
            try:
                response = self.llm.invoke(prompt)
                
                # Debug logging
                response_text = response.content if hasattr(response, 'content') else str(response)
                logger.debug(f"LLM Response: {response_text[:500]}")
                
                # Try to extract JSON from response (in case there's extra text)
                response_text = response_text.strip()
                
                # If response starts with markdown code block, extract JSON
                if response_text.startswith('```'):
                    # Remove markdown code blocks
                    response_text = response_text.split('```')[1]
                    if response_text.startswith('json'):
                        response_text = response_text[4:]
                    response_text = response_text.strip()
                
                result = json_module.loads(response_text)
                
            except json_module.JSONDecodeError as je:
                logger.error(f"Failed to parse LLM response as JSON: {je}")
                logger.error(f"Response was: {response_text[:500]}")
                # Return empty result rather than crashing
                result = {"entities": [], "relationships": []}
            except Exception as e:
                logger.error(f"Error calling LLM: {e}")
                raise
            
            entities = result.get("entities", [])
            relationships = result.get("relationships", [])
            
            # Add document node with metadata and tenant_id
            max_transaction_retries = 3
            retry_delay = 1  # Initial delay in seconds
            
            # Generate embedding outside transaction
            embedding = self.embedder.embed_query(text)
            
            # Convert metadata dict to JSON string for Neo4j storage
            import json as json_module
            metadata_json = json_module.dumps(metadata or {})
            
            for attempt in range(max_transaction_retries):
                try:
                    with self.driver.session(max_transaction_retry_time=self.timeout) as session:
                        # Use an explicit transaction
                        with session.begin_transaction() as tx:
                            # Create document node
                            tx.run("""
                                MERGE (d:Document {id: $doc_id})
                                SET d.content = $content,
                                    d.embedding = $embedding,
                                    d.tenant_id = $tenant_id,
                                    d.metadata = $metadata
                            """, {
                                "doc_id": doc_id,
                                "content": text,
                                "embedding": embedding,
                                "tenant_id": tenant_id,
                                "metadata": metadata_json
                            })
                
                            # Create entity nodes and link to document
                            for entity in entities:
                                entity_id = f"{tenant_id}_{entity['name']}_{entity.get('type', 'Entity')}"
                                entity_props_json = json_module.dumps(entity.get("properties", {}))
                                
                                # First try to find existing entity
                                result = tx.run("""
                                    MATCH (e:Entity {name: $name, tenant_id: $tenant_id})
                                    RETURN e
                                """, {
                                    "name": entity["name"],
                                    "tenant_id": tenant_id
                                })
                                
                                if not result.single():
                                    # Entity doesn't exist, create it
                                    tx.run("""
                                        CREATE (e:Entity {
                                            id: $entity_id,
                                            name: $name,
                                            type: $type,
                                            tenant_id: $tenant_id,
                                            properties: $properties
                                        })
                                    """, {
                                    "entity_id": entity_id,
                                    "name": entity["name"],
                                    "type": entity.get("type", "Entity"),
                                    "tenant_id": tenant_id,
                                    "properties": entity_props_json
                                })
                                
                                # Link entity to document
                                tx.run("""
                                    MATCH (d:Document {id: $doc_id})
                                    MATCH (e:Entity {id: $entity_id})
                                    MERGE (d)-[:MENTIONS]->(e)
                                """, {
                                    "doc_id": doc_id,
                                    "entity_id": entity_id
                                })
                
                            # Create relationships between entities
                            for rel in relationships:
                                # Try to match entities by name since we don't have source/target types
                                rel_props_json = json_module.dumps(rel.get("properties", {}))
                                
                                tx.run(f"""
                                    MATCH (source:Entity {{name: $source_name, tenant_id: $tenant_id}})
                                    MATCH (target:Entity {{name: $target_name, tenant_id: $tenant_id}})
                                    MERGE (source)-[r:`{rel['type']}`]->(target)
                                    SET r.properties = $properties
                                """, {
                                    "source_name": rel["source"],
                                    "target_name": rel["target"],
                                    "tenant_id": tenant_id,
                                    "properties": rel_props_json
                                })
            
                            # Commit transaction
                            tx.commit()
                            
                            logger.info(f"Built knowledge graph for document {doc_id} with {len(entities)} entities and {len(relationships)} relationships")
                            
                            return {
                                "entities": entities,
                                "relationships": relationships,
                                "doc_id": doc_id,
                                "status": "success"
                            }
                            
                except Exception as tx_error:
                    logger.warning(f"Transaction attempt {attempt + 1} failed: {tx_error}")
                    if attempt < max_transaction_retries - 1:
                        import time
                        wait_time = retry_delay * (2 ** attempt)  # Exponential backoff
                        logger.info(f"Retrying transaction in {wait_time} seconds...")
                        time.sleep(wait_time)
                    else:
                        logger.error("All transaction attempts failed")
                        raise
            
        except Exception as e:
            logger.error(f"Error building knowledge graph: {e}")
            
            if "Failed to read from defunct connection" in str(e):
                # Connection issue - retry with backoff
                wait_time = 2 ** retry_count
                logger.info(f"Connection issue detected, retrying in {wait_time} seconds...")
                import time
                time.sleep(wait_time)
                
                # Recursive retry with incremented counter
                return self.build_knowledge_graph(
                    text=text,
                    doc_id=doc_id,
                    metadata=metadata,
                    tenant_id=tenant_id,
                    retry_count=retry_count + 1
                )
            
            raise

    def extract_entities_and_relations(
        self,
        text: str,
        tenant_id: str = "default"
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Extract entities and relationships from text using LLM.
        
        Args:
            text: The text to extract from
            tenant_id: The tenant ID
            
        Returns:
            Tuple of (entities, relationships)
        """
        try:
            # Use the entity extractor
            result = self.entity_extractor.run(text=text)
            
            entities = []
            relationships = []
            
            if hasattr(result, 'entities'):
                entities = [
                    {
                        "name": entity.label,
                        "type": entity.type if hasattr(entity, 'type') else "Entity",
                        "properties": entity.properties if hasattr(entity, 'properties') else {}
                    }
                    for entity in result.entities
                ]
            
            if hasattr(result, 'relationships'):
                relationships = [
                    {
                        "source": rel.start_node.label,
                        "target": rel.end_node.label,
                        "type": rel.type,
                        "properties": rel.properties if hasattr(rel, 'properties') else {}
                    }
                    for rel in result.relationships
                ]
            
            return entities, relationships
            
        except Exception as e:
            logger.error(f"Error extracting entities and relations: {e}")
            return [], []

    def create_vector_retriever(
        self,
        index_name: str = "document_embeddings",
        tenant_id: Optional[str] = None
    ) -> VectorRetriever:
        """
        Create a vector retriever for semantic search.
        
        Args:
            index_name: Name of the vector index
            tenant_id: Optional tenant ID for filtering
            
        Returns:
            VectorRetriever instance
        """
        # VectorRetriever in newer versions uses return_properties instead of retrieval_query
        return_properties = ["id", "content", "metadata"]
        
        # Note: Tenant filtering needs to be handled in the search query or post-processing
        # as VectorRetriever doesn't support custom retrieval queries in newer versions
        return VectorRetriever(
            driver=self.driver,
            index_name=index_name,
            embedder=self.embedder,
            return_properties=return_properties
        )

    def create_hybrid_retriever(
        self,
        index_name: str = "document_embeddings",
        tenant_id: Optional[str] = None
    ) -> VectorCypherRetriever:
        """
        Create a hybrid retriever combining vector and graph traversal.
        
        Args:
            index_name: Name of the vector index
            tenant_id: Optional tenant ID for filtering
            
        Returns:
            VectorCypherRetriever instance
        """
        # Build retrieval query with graph traversal
        retrieval_query = """
        WITH node, score
        OPTIONAL MATCH (node)-[:MENTIONS]->(e:Entity)
        WITH node, score, collect(DISTINCT e) as entities
        OPTIONAL MATCH (node)-[:MENTIONS]->(e1:Entity)-[r]-(e2:Entity)<-[:MENTIONS]-(related:Document)
        WHERE node <> related
        """
        
        if tenant_id:
            retrieval_query += f" AND related.tenant_id = '{tenant_id}'"
        
        retrieval_query += """
        WITH node, score, entities, collect(DISTINCT related) as related_docs
        RETURN node.id AS id, node.content AS content,
               node.metadata AS metadata, score,
               entities, related_docs
        LIMIT 10
        """
        
        return VectorCypherRetriever(
            driver=self.driver,
            index_name=index_name,
            embedder=self.embedder,
            retrieval_query=retrieval_query
        )

    def search_with_vector(
        self,
        query: str,
        top_k: int = 5,
        tenant_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Search using vector similarity.
        
        Args:
            query: The search query
            top_k: Number of results to return
            tenant_id: Optional tenant ID for filtering
            
        Returns:
            List of matching documents
        """
        try:
            retriever = self.create_vector_retriever(tenant_id=tenant_id)
            results = retriever.search(query_text=query, top_k=top_k)
            
            return [
                {
                    "id": item.get("id"),
                    "content": item.get("content"),
                    "metadata": item.get("metadata", {}),
                    "score": item.get("score", 0.0)
                }
                for item in results.items
            ] if results else []
            
        except Exception as e:
            logger.error(f"Error in vector search: {e}")
            return []

    def search_with_hybrid(
        self,
        query: str,
        top_k: int = 5,
        tenant_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Search using hybrid vector + graph retrieval.
        
        Args:
            query: The search query
            top_k: Number of results to return
            tenant_id: Optional tenant ID for filtering
            
        Returns:
            List of matching documents with graph context
        """
        try:
            retriever = self.create_hybrid_retriever(tenant_id=tenant_id)
            results = retriever.search(query_text=query, top_k=top_k)
            
            return [
                {
                    "id": item.get("id"),
                    "content": item.get("content"),
                    "metadata": item.get("metadata", {}),
                    "score": item.get("score", 0.0),
                    "entities": item.get("entities", []),
                    "related_docs": item.get("related_docs", [])
                }
                for item in results.items
            ] if results else []
            
        except Exception as e:
            logger.error(f"Error in hybrid search: {e}")
            return []

    def traverse_graph(
        self,
        entity_name: str,
        max_depth: int = 2,
        tenant_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Traverse the knowledge graph starting from an entity.
        
        Args:
            entity_name: Starting entity name
            max_depth: Maximum traversal depth
            tenant_id: Optional tenant ID for filtering
            
        Returns:
            List of connected entities and relationships
        """
        try:
            with self.driver.session() as session:
                query = f"""
                MATCH path = (e:Entity {{name: $entity_name}})-[*1..{max_depth}]-(connected:Entity)
                """
                
                if tenant_id:
                    query += " WHERE e.tenant_id = $tenant_id AND connected.tenant_id = $tenant_id"
                
                query += """
                WITH path, connected
                OPTIONAL MATCH (connected)<-[:MENTIONS]-(d:Document)
                """
                
                if tenant_id:
                    query += " WHERE d.tenant_id = $tenant_id"
                
                query += """
                RETURN 
                    connected.name AS entity_name,
                    connected.type AS entity_type,
                    collect(DISTINCT {
                        doc_id: d.id,
                        content: d.content
                    }) AS documents,
                    length(path) AS distance
                ORDER BY distance
                LIMIT 20
                """
                
                params = {"entity_name": entity_name}
                if tenant_id:
                    params["tenant_id"] = tenant_id
                
                result = session.run(query, params)
                
                return [
                    {
                        "entity_name": record["entity_name"],
                        "entity_type": record["entity_type"],
                        "documents": record["documents"],
                        "distance": record["distance"]
                    }
                    for record in result
                ]
                
        except Exception as e:
            logger.error(f"Error traversing graph: {e}")
            return []

    def get_entity_context(
        self,
        entity_name: str,
        tenant_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get comprehensive context about an entity.
        
        Args:
            entity_name: The entity name
            tenant_id: Optional tenant ID for filtering
            
        Returns:
            Dictionary with entity context
        """
        try:
            with self.driver.session() as session:
                query = """
                MATCH (e:Entity {name: $entity_name})
                """
                
                if tenant_id:
                    query += " WHERE e.tenant_id = $tenant_id"
                
                query += """
                OPTIONAL MATCH (e)<-[:MENTIONS]-(d:Document)
                """
                
                if tenant_id:
                    query += " WHERE d.tenant_id = $tenant_id"
                
                query += """
                OPTIONAL MATCH (e)-[r]-(related:Entity)
                """
                
                if tenant_id:
                    query += " WHERE related.tenant_id = $tenant_id"
                
                query += """
                RETURN 
                    e.name AS name,
                    e.type AS type,
                    e.properties AS properties,
                    collect(DISTINCT {
                        doc_id: d.id,
                        content: d.content
                    }) AS documents,
                    collect(DISTINCT {
                        type: type(r),
                        entity: related.name
                    }) AS relationships
                """
                
                params = {"entity_name": entity_name}
                if tenant_id:
                    params["tenant_id"] = tenant_id
                
                result = session.run(query, params)
                record = result.single()
                
                if record:
                    return {
                        "name": record["name"],
                        "type": record["type"],
                        "properties": record["properties"],
                        "documents": record["documents"],
                        "relationships": record["relationships"]
                    }
                
                return {}
                
        except Exception as e:
            logger.error(f"Error getting entity context: {e}")
            return {}

    def add_tool(self, tool_data: Dict[str, Any], tenant_id: str = "global") -> str:
        """
        Add a tool to the knowledge graph with all its components.
        
        Args:
            tool_data: Dictionary containing tool data
            tenant_id: Tenant ID for multi-tenancy
            
        Returns:
            Tool ID
        """
        try:
            with self.driver.session() as session:
                with session.begin_transaction() as tx:
                    # Generate tool ID if not provided
                    tool_id = tool_data.get("id", str(uuid.uuid4()))
                    
                    # Create tool node
                    tx.run("""
                        MERGE (t:Tool {id: $tool_id})
                        SET t.name = $name,
                            t.homepage_url = $homepage_url,
                            t.last_scraped_at = $last_scraped_at,
                            t.short_description = $short_description,
                            t.detailed_description = $detailed_description,
                            t.rating = $rating,
                            t.logo_url = $logo_url,
                            t.tenant_id = $tenant_id,
                            t.tags = $tags
                    """, {
                        "tool_id": tool_id,
                        "name": tool_data["name"],
                        "homepage_url": str(tool_data["homepage_url"]),
                        "last_scraped_at": tool_data["last_scraped_at"].isoformat(),
                        "short_description": tool_data["short_description"],
                        "detailed_description": tool_data["detailed_description"],
                        "rating": tool_data["rating"],
                        "logo_url": str(tool_data["logo_url"]),
                        "tenant_id": tenant_id,
                        "tags": tool_data["tags"]
                    })
                    
                    # Add source URLs
                    for url in tool_data["source_urls"]:
                        tx.run("""
                            MATCH (t:Tool {id: $tool_id})
                            MERGE (s:Source {url: $url})
                            MERGE (t)-[:HAS_SOURCE]->(s)
                        """, {
                            "tool_id": tool_id,
                            "url": str(url)
                        })
                    
                    # Add categories
                    tx.run("""
                        MATCH (t:Tool {id: $tool_id})
                        MERGE (c:Category {name: $primary})
                        MERGE (t)-[:PRIMARY_CATEGORY]->(c)
                    """, {
                        "tool_id": tool_id,
                        "primary": tool_data["categories"]["primary"]
                    })
                    
                    for category in tool_data["categories"]["secondary"]:
                        tx.run("""
                            MATCH (t:Tool {id: $tool_id})
                            MERGE (c:Category {name: $category})
                            MERGE (t)-[:SECONDARY_CATEGORY]->(c)
                        """, {
                            "tool_id": tool_id,
                            "category": category
                        })
                    
                    # Add features
                    for i, feature in enumerate(tool_data["features"]):
                        feature_id = f"{tool_id}_feature_{i}"
                        tx.run("""
                            MATCH (t:Tool {id: $tool_id})
                            MERGE (f:Feature {id: $feature_id})
                            SET f.name = $name,
                                f.description = $description,
                                f.use_case = $use_case
                            MERGE (t)-[:HAS_FEATURE]->(f)
                        """, {
                            "tool_id": tool_id,
                            "feature_id": feature_id,
                            "name": feature["name"],
                            "description": feature["description"],
                            "use_case": feature["use_case"]
                        })
                    
                    # Add differentiators
                    for i, diff in enumerate(tool_data["differentiators"]):
                        tx.run("""
                            MATCH (t:Tool {id: $tool_id})
                            MERGE (d:Differentiator {id: $diff_id})
                            SET d.description = $description
                            MERGE (t)-[:HAS_DIFFERENTIATOR]->(d)
                        """, {
                            "tool_id": tool_id,
                            "diff_id": f"{tool_id}_diff_{i}",
                            "description": diff
                        })
                    
                    # Add subscriptions
                    for i, sub in enumerate(tool_data["subscriptions"]):
                        sub_id = f"{tool_id}_sub_{i}"
                        tx.run("""
                            MATCH (t:Tool {id: $tool_id})
                            MERGE (s:Subscription {id: $sub_id})
                            SET s.plan_name = $plan_name,
                                s.price_monthly = $price_monthly,
                                s.price_annual = $price_annual,
                                s.pricing_model = $pricing_model,
                                s.features_included = $features_included
                            MERGE (t)-[:HAS_SUBSCRIPTION]->(s)
                        """, {
                            "tool_id": tool_id,
                            "sub_id": sub_id,
                            "plan_name": sub["plan_name"],
                            "price_monthly": sub["price_monthly"],
                            "price_annual": sub["price_annual"],
                            "pricing_model": sub["pricing_model"],
                            "features_included": sub["features_included"]
                        })
                    
                    # Add compliance information
                    tx.run("""
                        MATCH (t:Tool {id: $tool_id})
                        MERGE (c:Compliance {id: $compliance_id})
                        SET c.gdpr_compliant = $gdpr_compliant,
                            c.us_cloud_act_safe = $us_cloud_act_safe,
                            c.data_sovereignty_options = $data_sovereignty_options,
                            c.certifications = $certifications
                        MERGE (t)-[:HAS_COMPLIANCE]->(c)
                    """, {
                        "tool_id": tool_id,
                        "compliance_id": f"{tool_id}_compliance",
                        "gdpr_compliant": tool_data["compliance"]["gdpr_compliant"],
                        "us_cloud_act_safe": tool_data["compliance"]["us_cloud_act_safe"],
                        "data_sovereignty_options": tool_data["compliance"]["data_sovereignty_options"],
                        "certifications": tool_data["compliance"]["certifications"]
                    })
                    
                    # Add documentation links
                    for i, doc_link in enumerate(tool_data["documentation_links"]):
                        tx.run("""
                            MATCH (t:Tool {id: $tool_id})
                            MERGE (d:Documentation {url: $url})
                            MERGE (t)-[:HAS_DOCUMENTATION]->(d)
                        """, {
                            "tool_id": tool_id,
                            "url": str(doc_link)
                        })
                    
                    return tool_id
                    
        except Exception as e:
            logger.error(f"Error adding tool to Neo4j: {e}")
            raise

    def add_learning_resource(self, resource_data: Dict[str, Any], tenant_id: str = "global") -> str:
        """
        Add a learning resource to the knowledge graph with all its components.
        
        Args:
            resource_data: Dictionary containing learning resource data
            tenant_id: Tenant ID for multi-tenancy
            
        Returns:
            Resource ID
        """
        try:
            with self.driver.session() as session:
                with session.begin_transaction() as tx:
                    # Generate resource ID if not provided
                    resource_id = resource_data.get("resource_id", str(uuid.uuid4()))
                    
                    # Create learning resource node
                    tx.run("""
                        MERGE (r:LearningResource {id: $resource_id})
                        SET r.title = $title,
                            r.description = $description,
                            r.source_url = $source_url,
                            r.resource_type = $resource_type,
                            r.expertise_level = $expertise_level,
                            r.estimated_time = $estimated_time,
                            r.tenant_id = $tenant_id,
                            r.tags = $tags
                    """, {
                        "resource_id": resource_id,
                        "title": resource_data["title"],
                        "description": resource_data["description"],
                        "source_url": resource_data["source_url"],
                        "resource_type": resource_data["resource_type"],
                        "expertise_level": resource_data["target_audience"]["expertise_level"],
                        "estimated_time": resource_data["estimatedTime"],
                        "tenant_id": tenant_id,
                        "tags": resource_data["tags"]
                    })
                    
                    # Add categories
                    tx.run("""
                        MATCH (r:LearningResource {id: $resource_id})
                        MERGE (c:Category {name: $primary})
                        MERGE (r)-[:PRIMARY_CATEGORY]->(c)
                    """, {
                        "resource_id": resource_id,
                        "primary": resource_data["categories"]["primary"]
                    })
                    
                    for category in resource_data["categories"]["secondary"]:
                        tx.run("""
                            MATCH (r:LearningResource {id: $resource_id})
                            MERGE (c:Category {name: $category})
                            MERGE (r)-[:SECONDARY_CATEGORY]->(c)
                        """, {
                            "resource_id": resource_id,
                            "category": category
                        })
                    
                    # Add topics
                    for topic in resource_data["topics_discussed"]:
                        tx.run("""
                            MATCH (r:LearningResource {id: $resource_id})
                            MERGE (t:Topic {name: $topic})
                            MERGE (r)-[:DISCUSSES]->(t)
                        """, {
                            "resource_id": resource_id,
                            "topic": topic
                        })
                    
                    # Add target job roles
                    for role in resource_data["target_audience"]["job_roles"]:
                        tx.run("""
                            MATCH (r:LearningResource {id: $resource_id})
                            MERGE (j:JobRole {name: $role})
                            MERGE (r)-[:TARGETS_ROLE]->(j)
                        """, {
                            "resource_id": resource_id,
                            "role": role
                        })
                    
                    # Add useful contexts
                    for context in resource_data["useful_context"]:
                        tx.run("""
                            MATCH (r:LearningResource {id: $resource_id})
                            MERGE (c:Context {name: $context})
                            MERGE (r)-[:USEFUL_IN]->(c)
                        """, {
                            "resource_id": resource_id,
                            "context": context
                        })
                    
                    # Add content details
                    content = resource_data["content"]
                    tx.run("""
                        MATCH (r:LearningResource {id: $resource_id})
                        MERGE (c:Content {id: $content_id})
                        SET c.summary = $summary,
                            c.full_text = $full_text,
                            c.video_transcript = $video_transcript,
                            c.video_url = $video_url
                        MERGE (r)-[:HAS_CONTENT]->(c)
                    """, {
                        "resource_id": resource_id,
                        "content_id": f"{resource_id}_content",
                        "summary": content["summary"],
                        "full_text": content["full_text"],
                        "video_transcript": content.get("video_transcript"),
                        "video_url": content.get("video_url")
                    })
                    
                    # Add image analysis
                    for i, image in enumerate(content.get("image_analysis", [])):
                        tx.run("""
                            MATCH (r:LearningResource {id: $resource_id})
                            MERGE (i:Image {id: $image_id})
                            SET i.url = $url,
                                i.description = $description
                            MERGE (r)-[:HAS_IMAGE]->(i)
                        """, {
                            "resource_id": resource_id,
                            "image_id": f"{resource_id}_image_{i}",
                            "url": image["image_url"],
                            "description": image["description"]
                        })
                    
                    return resource_id
                    
        except Exception as e:
            logger.error(f"Error adding learning resource to Neo4j: {e}")
            raise

    def close(self):
        """
        Close the Neo4j driver.
        """
        if self.driver:
            self.driver.close()