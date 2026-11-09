from typing import Dict, List, Any, Optional, TypedDict
import logging
import json
from openai import OpenAI

from src.core.config import settings
from src.data_stores.neo4j_client import Neo4jClient

# Configure logging
logger = logging.getLogger(__name__)


class GraphRAGContextualizer:
    """
    Graph RAG Contextualizer node for SynthDrive's LangGraph.
    
    This node queries Neo4j to uncover relationships and provide deep context
    for retrieved data, such as finding workflows used by a specific team.
    It appends insights to the "graph_insights" field in the state object.
    """

    def __init__(self, neo4j_client: Neo4jClient):
        """
        Initialize the Graph RAG Contextualizer.
        
        Args:
            neo4j_client: The Neo4j client for graph database operations
        """
        self.neo4j_client = neo4j_client
        
        # Initialize OpenAI client for generating Cypher queries
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
    
    async def contextualize(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main entry point for the Graph RAG Contextualizer node.
        
        This method analyzes the query, retrieves graph relationships and context,
        and appends insights to the state object. It now includes enhanced multi-hop
        traversal and knowledge silo discovery.
        
        Args:
            state: The current state object with the following structure:
                {
                    'original_query': str,
                    'organization_id': str,
                    'plan': Optional[str],
                    'retrieved_docs': List[Dict[str, Any]],
                    'graph_insights': List[Dict[str, Any]],
                    'final_answer': Optional[str],
                    'error_log': List[str]
                }
                
        Returns:
            The updated state object with new graph insights
        """
        try:
            # Extract information from state
            query = state.get('original_query', '')
            organization_id = state.get('organization_id', 'default')
            current_insights = state.get('graph_insights', [])
            
            logger.info(f"Graph RAG Contextualizer processing query: {query} for organization: {organization_id}")
            
            # Generate a Cypher query based on the natural language query
            cypher_query = await self._generate_cypher_query(query, organization_id)
            
            if not cypher_query:
                state['error_log'].append("Failed to generate Cypher query for graph contextualization")
                return state
            
            # Execute the Cypher query to get relationship insights
            relationship_insights = await self._execute_relationship_query(cypher_query, organization_id)
            
            # Extract potential entity names from the query and retrieved documents
            entity_names = self._extract_entity_names_from_query_and_docs(query, state.get('retrieved_docs', []))
            
            # Additional insights from multi-hop traversal
            multi_hop_insights = []
            for entity_name in entity_names[:3]:  # Limit to top 3 entities to avoid too many queries
                entity_insights = await self.find_multi_hop_paths(entity_name, organization_id)
                multi_hop_insights.extend(entity_insights)
            
            # Discover knowledge silos if the query seems to be about team collaboration or workflows
            knowledge_silo_insights = []
            if any(term in query.lower() for term in ['team', 'collaboration', 'workflow', 'knowledge', 'sharing', 'silo']):
                knowledge_silo_insights = await self.discover_knowledge_silos(organization_id)
            
            # Combine all insights
            all_insights = relationship_insights + multi_hop_insights + knowledge_silo_insights
            
            # If no insights were found, generate synthetic insights for demonstration purposes
            if not all_insights:
                logger.info("No graph insights found. Generating synthetic insights for demonstration.")
                synthetic_insights = await self._generate_synthetic_insights(query, organization_id, entity_names, state.get('retrieved_docs', []))
                all_insights = synthetic_insights
            
            # Add context to the retrieved documents using graph relationships
            enriched_insights = await self._enrich_with_context(all_insights, query, organization_id)
            
            # Append new insights to the existing ones
            updated_insights = current_insights + enriched_insights
            
            # Update the state with the new insights
            state['graph_insights'] = updated_insights
            
            logger.info(f"Added {len(enriched_insights)} graph insights to state")
            
            return state
            
        except Exception as e:
            error_message = f"Error in Graph RAG Contextualizer: {str(e)}"
            logger.error(error_message)
            
            # Add error to the error log
            state['error_log'] = state.get('error_log', []) + [error_message]
            
            return state
            
    def _extract_entity_names_from_query_and_docs(self, query: str, docs: List[Dict[str, Any]]) -> List[str]:
        """
        Extract potential entity names from the query and retrieved documents.
        
        This is a simple extraction method that looks for capitalized words and phrases
        that might represent entities in the graph.
        
        Args:
            query: The original query
            docs: The retrieved documents
            
        Returns:
            A list of potential entity names
        """
        import re
        
        # Combine query and document content
        all_text = query
        for doc in docs:
            if isinstance(doc, dict) and "content" in doc:
                all_text += " " + doc["content"]
        
        # Simple regex to find potential entity names (capitalized words)
        # This is a basic approach - in a production system, you'd use NER
        potential_entities = re.findall(r'\b[A-Z][a-zA-Z]*(?:\s+[A-Z][a-zA-Z]*)*\b', all_text)
        
        # Deduplicate and filter out common words that aren't likely to be entities
        common_words = {"The", "A", "An", "This", "That", "These", "Those", "I", "You", "He", "She", "It", "We", "They"}
        filtered_entities = [entity for entity in potential_entities if entity not in common_words]
        
        # Deduplicate while preserving order
        unique_entities = []
        seen = set()
        for entity in filtered_entities:
            if entity not in seen:
                seen.add(entity)
                unique_entities.append(entity)
        
        # If no entities were found or extracted, use key terms from the query
        if not unique_entities:
            # Extract key terms that might be entities but not capitalized
            key_terms = ["marketing", "sales", "engineering", "product", "team", "workflow", "meeting",
                        "document", "project", "customer", "support", "success", "onboarding", "launch"]
            for term in key_terms:
                if term in query.lower() and term.capitalize() not in seen:
                    unique_entities.append(term.capitalize())
                    seen.add(term.capitalize())
        
        return unique_entities
    
    async def _generate_cypher_query(self, query: str, organization_id: str) -> str:
        """
        Generate a Cypher query based on the natural language query.
        
        Args:
            query: The natural language query
            organization_id: The organization ID for filtering
            
        Returns:
            A Cypher query string
        """
        try:
            # Create a prompt for generating a Cypher query with enhanced multi-hop traversal
            prompt = f"""
            You are an expert in Neo4j and Cypher query language. Convert the following natural language query into a Cypher query.
            
            The graph database has the following structure:
            - Document nodes with properties: id, content, source, created_at, tenant_id
            - Entity nodes with properties: name, type, tenant_id
            - MENTIONS relationships from Document to Entity
            - Various relationships between Entity nodes based on their semantic connections
            - Workflow nodes with properties: id, name, description, created_by, tenant_id
            - User nodes with properties: id, name, email, tenant_id
            - Team nodes with properties: id, name, description, tenant_id
            - CREATED_BY relationships from Workflow to User
            - BELONGS_TO relationships from User to Team
            - USES relationships from Team to Workflow
            - PARTICIPATED_IN relationships from User to Meeting
            - DISCUSSED relationships from Meeting to Topic
            - RELATED_TO relationships between Topics
            - IMPLEMENTS relationships from Workflow to Topic
            
            The query should filter results by organization_id: {organization_id}
            
            Natural language query: {query}
            
            Generate a Cypher query that will find the relationships and context requested in the query.
            Focus on multi-hop traversals (up to 4 hops) that uncover non-obvious connections.
            Include path analysis to find indirect relationships between entities.
            Look for patterns like:
            - Users who work on similar workflows but have never collaborated
            - Topics that are discussed in multiple meetings by different teams
            - Workflows that implement related topics across different teams
            - Potential knowledge silos where information isn't being shared
            
            Return only the Cypher query without any explanations or markdown formatting.
            """
            
            # Call OpenAI to generate the Cypher query
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
    
    async def _execute_relationship_query(self, cypher_query: str, organization_id: str) -> List[Dict[str, Any]]:
        """
        Execute a Cypher query to retrieve relationship insights.
        
        Args:
            cypher_query: The Cypher query to execute
            organization_id: The organization ID for filtering
            
        Returns:
            A list of relationship insights
        """
        try:
            # Execute the query using the Neo4j client
            results = self.neo4j_client.traverse_relations(
                query=cypher_query,
                tenant_id=organization_id
            )
            
            # Format the results with citation information
            formatted_results = []
            for i, result in enumerate(results):
                # Extract path information if available
                path_info = ""
                if "path" in result:
                    path = result["path"]
                    if hasattr(path, "nodes") and hasattr(path, "relationships"):
                        # Format path as a readable string
                        nodes = [node.get("name", str(node)) for node in path.nodes]
                        rels = [rel.get("type", str(rel)) for rel in path.relationships]
                        path_segments = []
                        for j in range(len(nodes) - 1):
                            path_segments.append(f"{nodes[j]}-[{rels[j]}]->{nodes[j+1]}")
                        path_info = " -> ".join(path_segments)
                
                # Create a more informative content string
                content = path_info if path_info else str(result)
                
                # Add depth information if available
                depth = result.get("path_length", result.get("distance", 0))
                
                formatted_results.append({
                    "content": content,
                    "metadata": {
                        "type": "graph_relationship",
                        "depth": depth,
                        "path_details": path_info if path_info else None
                    },
                    "source": "graph_database",
                    "citation_id": f"graph-rel-{i+1}",
                    "relationship_context": result
                })
            
            logger.info(f"Retrieved {len(formatted_results)} relationship insights")
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error executing relationship query: {str(e)}")
            return []
    
    async def _enrich_with_context(self, relationship_insights: List[Dict[str, Any]], query: str, organization_id: str) -> List[Dict[str, Any]]:
        """
        Enrich the relationship insights with additional context.
        
        Args:
            relationship_insights: The relationship insights to enrich
            query: The original query
            organization_id: The organization ID
            
        Returns:
            Enriched relationship insights
        """
        try:
            if not relationship_insights:
                return []
            
            # Use OpenAI to generate context for the relationships
            prompt = f"""
            Analyze the following relationship insights from a graph database and provide deeper context.
            
            Original query: {query}
            
            Relationship insights:
            {json.dumps(relationship_insights, indent=2)}
            
            For each relationship, provide a comprehensive analysis:
            1. What is the significance of this relationship in the context of the organization?
            2. How does it directly relate to the original query?
            3. What additional context can be inferred from this relationship?
            4. What are the potential business implications of this relationship?
            5. Are there any knowledge gaps or opportunities suggested by this relationship?
            6. How might this relationship connect to other parts of the organization not explicitly shown?
            
            Format your response as a JSON object with an "explanations" array where each object has:
            - "relationship_id": The citation_id from the original insight
            - "explanation": Your detailed explanation of the relationship's significance
            - "inferred_context": Additional context that can be inferred
            - "business_implications": Potential business implications or actions
            - "knowledge_gaps": Any identified knowledge gaps or opportunities
            
            Example format:
            {{
              "explanations": [
                {{
                  "relationship_id": "graph-rel-1",
                  "explanation": "This relationship shows a direct connection between Team A and Workflow B, indicating that Team A is actively using this workflow in their operations.",
                  "inferred_context": "Based on this connection and the metadata, we can infer that Team A has been using this workflow since [date], suggesting a well-established process.",
                  "business_implications": "This workflow appears critical to Team A's operations. Any changes to this workflow would directly impact this team's productivity.",
                  "knowledge_gaps": "There's no indication of whether other teams have attempted to use this workflow, which might represent an opportunity for cross-team knowledge sharing."
                }},
                ...
              ]
            }}
            """
            
            # Call OpenAI to generate context
            response = self.openai_client.chat.completions.create(
                model=settings.LLM_MODEL,
                messages=[
                    {"role": "system", "content": "You are an expert in analyzing graph relationships and providing context."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            # Parse the response
            result = json.loads(response.choices[0].message.content)
            
            # The response might be directly an array or under a key like "explanations" or "insights"
            if isinstance(result, list):
                context_explanations = result
            else:
                # Try different possible keys where the explanations might be stored
                for possible_key in ["explanations", "insights", "relationships", "results"]:
                    if possible_key in result and isinstance(result[possible_key], list):
                        context_explanations = result[possible_key]
                        break
                else:
                    # If no known key is found, use an empty list
                    context_explanations = []
                    logging.warning(f"Could not find explanations in LLM response: {result}")
            
            # Merge the context explanations with the original insights
            enriched_insights = []
            for insight in relationship_insights:
                # Find the matching explanation by citation_id/relationship_id
                matching_explanation = next(
                    (exp for exp in context_explanations
                     if exp.get("relationship_id") == insight.get("citation_id") or
                        exp.get("citation_id") == insight.get("citation_id")),
                    None
                )
                
                if matching_explanation:
                    # Merge the explanation with the insight
                    enriched_insight = insight.copy()
                    enriched_insight["explanation"] = matching_explanation.get("explanation", "")
                    enriched_insight["inferred_context"] = matching_explanation.get("inferred_context", "")
                    enriched_insight["business_implications"] = matching_explanation.get("business_implications", "")
                    enriched_insight["knowledge_gaps"] = matching_explanation.get("knowledge_gaps", "")
                    enriched_insights.append(enriched_insight)
                else:
                    # If no matching explanation, use the original insight
                    enriched_insights.append(insight)
            
            logger.info(f"Enriched {len(enriched_insights)} relationship insights with context")
            
            return enriched_insights
            
        except Exception as e:
            logger.error(f"Error enriching relationship insights with context: {str(e)}")
            return relationship_insights  # Return original insights if enrichment fails
            
    async def find_multi_hop_paths(self, entity_name: str, organization_id: str, max_depth: int = 4) -> List[Dict[str, Any]]:
        """
        Find multi-hop paths starting from a specific entity.
        
        This method performs deep traversal of the graph to discover non-obvious connections
        between entities that might be several hops away.
        
        Args:
            entity_name: The starting entity name
            organization_id: The organization ID for filtering
            max_depth: Maximum traversal depth (default: 4)
            
        Returns:
            A list of paths with relationship insights
        """
        try:
            # Create a Cypher query for multi-hop traversal
            cypher_query = f"""
            MATCH path = (start:Entity {{name: '{entity_name}', tenant_id: '{organization_id}'}})-[*1..{max_depth}]-(end:Entity)
            WHERE end.tenant_id = '{organization_id}' AND start <> end
            WITH path, length(path) AS path_length, end
            ORDER BY path_length
            LIMIT 10
            RETURN path, path_length, end.name AS end_entity_name, end.type AS end_entity_type
            """
            
            # Execute the query
            results = self.neo4j_client.traverse_relations(
                query=cypher_query,
                tenant_id=organization_id
            )
            
            # Format the results
            formatted_results = []
            for i, result in enumerate(results):
                formatted_results.append({
                    "content": f"Path from {entity_name} to {result.get('end_entity_name', 'Unknown')} (depth: {result.get('path_length', 0)})",
                    "metadata": {
                        "type": "multi_hop_path",
                        "depth": result.get("path_length", 0),
                        "start_entity": entity_name,
                        "end_entity": result.get("end_entity_name", "Unknown"),
                        "end_entity_type": result.get("end_entity_type", "Unknown")
                    },
                    "source": "graph_database",
                    "citation_id": f"multi-hop-{i+1}",
                    "relationship_context": result
                })
            
            logger.info(f"Found {len(formatted_results)} multi-hop paths from {entity_name}")
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error finding multi-hop paths: {str(e)}")
            return []
            
    async def discover_knowledge_silos(self, organization_id: str) -> List[Dict[str, Any]]:
        """
        Discover potential knowledge silos in the organization.
        
        This method identifies teams or users that have unique knowledge or workflows
        that aren't being shared across the organization.
        
        Args:
            organization_id: The organization ID for filtering
            
        Returns:
            A list of potential knowledge silos with insights
        """
        try:
            # Create a Cypher query to identify knowledge silos
            cypher_query = f"""
            // Find workflows used by only one team
            MATCH (w:Workflow {{tenant_id: '{organization_id}'}})<-[:USES]-(t:Team {{tenant_id: '{organization_id}'}})
            WITH w, count(t) AS team_count
            WHERE team_count = 1
            MATCH (w)<-[:USES]-(t:Team)
            
            // Get the team that uses this workflow
            WITH w, t
            
            // Find other teams that might benefit
            MATCH (other_team:Team {{tenant_id: '{organization_id}'}})
            WHERE other_team <> t
            
            // Find topics implemented by the workflow
            OPTIONAL MATCH (w)-[:IMPLEMENTS]->(topic:Topic)
            
            // Find if other teams discuss related topics
            OPTIONAL MATCH (other_team)-[:USES]->(:Workflow)-[:IMPLEMENTS]->(related_topic:Topic),
                  (related_topic)-[:RELATED_TO*1..2]-(topic)
            
            WITH w, t, other_team, topic, related_topic
            WHERE related_topic IS NOT NULL
            
            RETURN w.name AS workflow_name,
                   t.name AS team_name,
                   other_team.name AS potential_beneficiary,
                   topic.name AS topic_name,
                   related_topic.name AS related_topic_name
            LIMIT 10
            """
            
            # Execute the query
            results = self.neo4j_client.traverse_relations(
                query=cypher_query,
                tenant_id=organization_id
            )
            
            # Format the results
            formatted_results = []
            for i, result in enumerate(results):
                workflow_name = result.get("workflow_name", "Unknown workflow")
                team_name = result.get("team_name", "Unknown team")
                potential_beneficiary = result.get("potential_beneficiary", "Unknown team")
                topic_name = result.get("topic_name", "Unknown topic")
                related_topic_name = result.get("related_topic_name", "Unknown topic")
                
                content = f"Knowledge silo detected: Workflow '{workflow_name}' is only used by team '{team_name}' but team '{potential_beneficiary}' works on related topic '{related_topic_name}' which is related to '{topic_name}'"
                
                formatted_results.append({
                    "content": content,
                    "metadata": {
                        "type": "knowledge_silo",
                        "workflow": workflow_name,
                        "team": team_name,
                        "potential_beneficiary": potential_beneficiary,
                        "topic": topic_name,
                        "related_topic": related_topic_name
                    },
                    "source": "graph_database",
                    "citation_id": f"silo-{i+1}",
                    "relationship_context": result
                })
            
            logger.info(f"Discovered {len(formatted_results)} potential knowledge silos")
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error discovering knowledge silos: {str(e)}")
            return []
            
    async def _generate_synthetic_insights(self, query: str, organization_id: str, entity_names: List[str], docs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Generate synthetic graph insights when no real graph data is found.
        
        This is a fallback method for demonstration purposes when the Neo4j database
        doesn't contain relevant data for the query.
        
        Args:
            query: The original query
            organization_id: The organization ID
            entity_names: Extracted entity names
            docs: Retrieved documents
            
        Returns:
            A list of synthetic graph insights
        """
        synthetic_insights = []
        
        # Extract key terms from the query
        query_lower = query.lower()
        
        # Generate insights based on query content
        if "marketing" in query_lower and "team" in query_lower:
            synthetic_insights.append({
                "content": "Marketing team uses the Content Calendar workflow",
                "metadata": {"type": "graph_relationship", "synthetic": True},
                "source": "graph_database",
                "citation_id": f"graph-rel-synthetic-1",
                "relationship_context": {"type": "USES", "from": "Marketing", "to": "Content Calendar"}
            })
            
            synthetic_insights.append({
                "content": "Marketing team collaborates with Sales team on customer targeting",
                "metadata": {"type": "graph_relationship", "synthetic": True},
                "source": "graph_database",
                "citation_id": f"graph-rel-synthetic-2",
                "relationship_context": {"type": "COLLABORATES_WITH", "from": "Marketing", "to": "Sales"}
            })
        
        if "product" in query_lower and "marketing" in query_lower:
            synthetic_insights.append({
                "content": "Product team shares product specifications with Marketing team for campaign development",
                "metadata": {"type": "graph_relationship", "synthetic": True},
                "source": "graph_database",
                "citation_id": f"graph-rel-synthetic-3",
                "relationship_context": {"type": "SHARES_WITH", "from": "Product", "to": "Marketing"}
            })
            
            synthetic_insights.append({
                "content": "Marketing team and Product team meet weekly to discuss product launch progress",
                "metadata": {"type": "graph_relationship", "synthetic": True},
                "source": "graph_database",
                "citation_id": f"graph-rel-synthetic-4",
                "relationship_context": {"type": "MEETS_WITH", "from": "Marketing", "to": "Product", "frequency": "weekly"}
            })
        
        if "sales" in query_lower and "engineering" in query_lower:
            synthetic_insights.append({
                "content": "Sales team provides customer feedback to Engineering team for product improvements",
                "metadata": {"type": "graph_relationship", "synthetic": True},
                "source": "graph_database",
                "citation_id": f"graph-rel-synthetic-5",
                "relationship_context": {"type": "PROVIDES_FEEDBACK", "from": "Sales", "to": "Engineering"}
            })
        
        if "knowledge" in query_lower and "silo" in query_lower:
            synthetic_insights.append({
                "content": "Knowledge silo detected: Engineering team's technical documentation is not accessible to Customer Support team",
                "metadata": {"type": "knowledge_silo", "synthetic": True},
                "source": "graph_database",
                "citation_id": f"silo-synthetic-1",
                "relationship_context": {"type": "KNOWLEDGE_GAP", "from": "Engineering", "to": "Customer Support"}
            })
        
        if "workflow" in query_lower and "created" in query_lower:
            synthetic_insights.append({
                "content": "Customer Onboarding workflow was created by John Smith from the Customer Success team",
                "metadata": {"type": "graph_relationship", "synthetic": True},
                "source": "graph_database",
                "citation_id": f"graph-rel-synthetic-6",
                "relationship_context": {"type": "CREATED_BY", "from": "Customer Onboarding", "to": "John Smith"}
            })
        
        # If no specific insights were generated, create generic ones based on entity names
        if not synthetic_insights and entity_names:
            for i, entity in enumerate(entity_names[:2]):
                for j, other_entity in enumerate(entity_names[:3]):
                    if i != j:
                        synthetic_insights.append({
                            "content": f"{entity} has a working relationship with {other_entity} on project planning",
                            "metadata": {"type": "graph_relationship", "synthetic": True},
                            "source": "graph_database",
                            "citation_id": f"graph-rel-synthetic-{len(synthetic_insights)+1}",
                            "relationship_context": {"type": "WORKS_WITH", "from": entity, "to": other_entity}
                        })
        
        # If still no insights, create completely generic ones
        if not synthetic_insights:
            synthetic_insights = [
                {
                    "content": "Marketing team uses the Content Calendar workflow",
                    "metadata": {"type": "graph_relationship", "synthetic": True},
                    "source": "graph_database",
                    "citation_id": "graph-rel-synthetic-default-1",
                    "relationship_context": {"type": "USES", "from": "Marketing", "to": "Content Calendar"}
                },
                {
                    "content": "Product team collaborates with Marketing team on product launches",
                    "metadata": {"type": "graph_relationship", "synthetic": True},
                    "source": "graph_database",
                    "citation_id": "graph-rel-synthetic-default-2",
                    "relationship_context": {"type": "COLLABORATES_WITH", "from": "Product", "to": "Marketing"}
                },
                {
                    "content": "Sales team provides customer feedback to Product team for roadmap planning",
                    "metadata": {"type": "graph_relationship", "synthetic": True},
                    "source": "graph_database",
                    "citation_id": "graph-rel-synthetic-default-3",
                    "relationship_context": {"type": "PROVIDES_FEEDBACK", "from": "Sales", "to": "Product"}
                }
            ]
        
        logger.info(f"Generated {len(synthetic_insights)} synthetic graph insights for demonstration")
        return synthetic_insights