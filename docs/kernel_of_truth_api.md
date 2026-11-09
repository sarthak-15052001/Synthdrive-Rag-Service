# Kernel of Truth API Documentation

## Overview

The Kernel of Truth API provides a way to query relationships and context between entities in the tenant domain using Neo4j graph traversals. It performs multi-hop queries to gain contextual insights about relationships between users, workflows, meetings, and other entities.

## Endpoint

```
POST /api/v1/rag/kernel-of-truth/query
```

## Description

Use graph traversals for multi-hop queries to gain contextual insights (e.g., relationships between users, workflows, meetings).

## Components Involved

- **Neo4j Graph** for nodes (e.g., User, Workflow) and edges (e.g., CREATED, USED_IN).
- The graph database stores entities as nodes with properties and relationships between them as edges.

## Prompt Template

"Act as the SynthDrive 'Kernel of Truth' in the Tenant Domain using Neo4j for graphing relationships between data entities (nodes like User, Workflow; edges like CREATED, USED_IN). For the query: [user_query], perform a multi-hop graph query to uncover relationships. Output insights like 'User X created Workflow Y, used in Meeting Z'."

## Request Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| query | string | Yes | The natural language query about relationships |
| tenant_id | string | No | The tenant ID to filter results by (default: "default") |
| max_depth | integer | No | Maximum path depth for relationships (default: 3, min: 1, max: 5) |
| limit | integer | No | Maximum number of results to return (default: 10, min: 1, max: 50) |

## Request Example

```json
{
  "query": "What workflows did user John create?",
  "tenant_id": "default",
  "max_depth": 3,
  "limit": 10
}
```

## Response Format

| Field | Type | Description |
|-------|------|-------------|
| query | string | The original query string |
| insights | array | List of relationship insights |

Each insight in the `insights` array has the following structure:

| Field | Type | Description |
|-------|------|-------------|
| content | string | Human-readable description of the relationship |
| metadata | object | Additional metadata about the relationship |
| source | string | Source of the insight (always "graph_database") |
| citation_id | string | Unique identifier for the citation |
| query | string | The original query string |

## Response Example

```json
{
  "query": "What workflows did user John create?",
  "insights": [
    {
      "content": "John created Workflow X.",
      "metadata": {
        "entities": ["John", "Workflow X"],
        "relationship_type": "creation"
      },
      "source": "graph_database",
      "citation_id": "kernel-1",
      "query": "What workflows did user John create?"
    },
    {
      "content": "John created Workflow Y.",
      "metadata": {
        "entities": ["John", "Workflow Y"],
        "relationship_type": "creation"
      },
      "source": "graph_database",
      "citation_id": "kernel-2",
      "query": "What workflows did user John create?"
    }
  ]
}
```

## Error Handling

If an error occurs during processing, the API will return an HTTP 500 status code with an error message in the response body.

## Example Usage

### Using curl

```bash
curl -X POST "http://localhost:8000/api/v1/rag/kernel-of-truth/query" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "query": "What workflows did user John create?",
    "tenant_id": "default",
    "max_depth": 3,
    "limit": 10
  }'
```

### Using Python

```python
import requests

url = "http://localhost:8000/api/v1/rag/kernel-of-truth/query"
payload = {
    "query": "What workflows did user John create?",
    "tenant_id": "default",
    "max_depth": 3,
    "limit": 10
}
headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer YOUR_TOKEN"
}

response = requests.post(url, json=payload, headers=headers)
result = response.json()
print(result)