# Graph RAG Contextualizer

## Overview

The Graph RAG Contextualizer is a specialized node in SynthDrive's LangGraph system that enhances retrieved data with deep contextual insights from graph relationships. It queries Neo4j to uncover non-obvious connections and relationships between entities, providing richer context for the RAG pipeline.

## Key Features

- **Relationship Discovery**: Identifies connections between entities in the knowledge graph
- **Multi-hop Traversal**: Discovers relationships that span multiple hops in the graph
- **Knowledge Silo Detection**: Identifies potential knowledge silos in the organization
- **Context Enrichment**: Adds explanations and business implications to discovered relationships
- **Integration with RAG Pipeline**: Seamlessly integrates with the existing RAG system

## API Endpoint

```
POST /api/v1/graph-rag-contextualizer
```

### Request Format

```json
{
  "query": "Find workflows used by the Marketing team",
  "organization_id": "org123",
  "tenant_id": "default",
  "retrieved_docs": [
    {
      "content": "Document content...",
      "metadata": { ... },
      "citation_id": "doc-1"
    }
  ]
}
```

### Response Format

```json
{
  "query": "Find workflows used by the Marketing team",
  "organization_id": "org123",
  "graph_insights": [
    {
      "content": "Marketing team uses the Content Calendar workflow",
      "metadata": { "type": "graph_relationship", ... },
      "source": "graph_database",
      "citation_id": "graph-rel-1",
      "explanation": "This relationship shows that the Marketing team actively uses the Content Calendar workflow for planning and scheduling content releases.",
      "inferred_context": "The Marketing team has been using this workflow since 2024-01-15, suggesting it's a well-established process.",
      "business_implications": "This workflow is critical to Marketing operations. Any changes would impact their content planning process.",
      "knowledge_gaps": "There's no indication if other teams have attempted to use this workflow."
    }
  ]
}
```

## Implementation Details

The Graph RAG Contextualizer is implemented as a class in `src/querying/tools/graph_rag_contextualizer.py` with the following key methods:

- `contextualize(state)`: Main entry point that processes the query and updates the state with graph insights
- `_generate_cypher_query(query, organization_id)`: Generates a Cypher query based on the natural language query
- `_execute_relationship_query(cypher_query, organization_id)`: Executes the Cypher query to retrieve relationship insights
- `_enrich_with_context(relationship_insights, query, organization_id)`: Enriches the relationship insights with additional context
- `find_multi_hop_paths(entity_name, organization_id, max_depth)`: Finds multi-hop paths starting from a specific entity
- `discover_knowledge_silos(organization_id)`: Discovers potential knowledge silos in the organization

## Graph Schema

The Graph RAG Contextualizer works with the following Neo4j graph schema:

- **Nodes**:
  - `Document`: Represents a document with properties like id, content, source, created_at, tenant_id
  - `Entity`: Represents an entity mentioned in documents with properties like name, type, tenant_id
  - `Workflow`: Represents a workflow with properties like id, name, description, created_by, tenant_id
  - `User`: Represents a user with properties like id, name, email, tenant_id
  - `Team`: Represents a team with properties like id, name, description, tenant_id
  - `Meeting`: Represents a meeting with properties like id, name, date, tenant_id
  - `Topic`: Represents a topic with properties like id, name, description, tenant_id

- **Relationships**:
  - `MENTIONS`: From Document to Entity
  - `CREATED_BY`: From Workflow to User
  - `BELONGS_TO`: From User to Team
  - `USES`: From Team to Workflow
  - `PARTICIPATED_IN`: From User to Meeting
  - `DISCUSSED`: From Meeting to Topic
  - `RELATED_TO`: Between Topics
  - `IMPLEMENTS`: From Workflow to Topic

## Usage Examples

### Finding Team Workflows

```json
{
  "query": "Find workflows used by the Marketing team",
  "organization_id": "org123",
  "tenant_id": "default",
  "retrieved_docs": []
}
```

### Discovering Knowledge Silos

```json
{
  "query": "Find potential knowledge silos in our organization",
  "organization_id": "org123",
  "tenant_id": "default",
  "retrieved_docs": []
}
```

### Analyzing Team Relationships

```json
{
  "query": "What are the relationships between the Sales and Engineering teams?",
  "organization_id": "org123",
  "tenant_id": "default",
  "retrieved_docs": []
}
```

## Testing

You can test the Graph RAG Contextualizer using the provided test scripts:

- `test_graph_rag_contextualizer.py`: Tests the class implementation directly
- `test_graph_rag_contextualizer_api.py`: Tests the API endpoint using requests
- `test_rag_query_graphrag_curl.sh`: Tests the API endpoint using curl commands

Sample payloads for testing are available in `rag_query_graphrag_payloads.json`.

## Integration with RAG Pipeline

The Graph RAG Contextualizer is designed to be integrated into the RAG pipeline as follows:

1. User query is processed by the RAG system
2. Vector search retrieves relevant documents
3. Graph RAG Contextualizer enhances the results with relationship insights
4. Synthesizer combines all information into a final answer

This integration provides a more comprehensive response that includes both content-based and relationship-based insights.