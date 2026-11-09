# Synthesizer API Documentation

## Overview

The Synthesizer API is a component of the SynthDrive RAG (Retrieval-Augmented Generation) service. It combines retrieved documents and graph insights into a coherent, cited final response using an LLM (Large Language Model). The Synthesizer is designed to be the final step in a RAG pipeline, taking the results of document retrieval and graph analysis to generate a comprehensive answer to the user's query.

## API Endpoint

```
POST /api/v1/rag/synthesizer
```

## Request Format

The Synthesizer API accepts a JSON payload with the following structure:

```json
{
  "query": "The original user query",
  "organization_id": "Organization identifier",
  "tenant_id": "Tenant identifier (optional, defaults to 'default')",
  "retrieved_docs": [
    {
      "content": "Document content",
      "metadata": {"type": "document_type", ...},
      "source": "Source of the document",
      "citation_id": "Unique identifier for citation"
    },
    ...
  ],
  "graph_insights": [
    {
      "content": "Graph insight content",
      "metadata": {"type": "insight_type", ...},
      "source": "Source of the insight",
      "citation_id": "Unique identifier for citation",
      "explanation": "Explanation of the insight",
      "inferred_context": "Additional context inferred from the insight"
    },
    ...
  ]
}
```

### Request Parameters

- `query` (string, required): The original user query that needs to be answered.
- `organization_id` (string, required): Identifier for the organization.
- `tenant_id` (string, optional): Identifier for the tenant. Defaults to "default".
- `retrieved_docs` (array, required): List of documents retrieved from vector search or other sources.
  - `content` (string): The content of the document.
  - `metadata` (object): Additional metadata about the document.
  - `source` (string): The source of the document.
  - `citation_id` (string): Unique identifier for citing this document.
- `graph_insights` (array, optional): List of insights from graph analysis.
  - `content` (string): The content of the insight.
  - `metadata` (object): Additional metadata about the insight.
  - `source` (string): The source of the insight.
  - `citation_id` (string): Unique identifier for citing this insight.
  - `explanation` (string): Explanation of the insight.
  - `inferred_context` (string): Additional context inferred from the insight.

## Response Format

The API returns a JSON response with the following structure:

```json
{
  "query": "The original user query",
  "organization_id": "Organization identifier",
  "final_answer": "The synthesized answer with citations"
}
```

### Response Parameters

- `query` (string): The original user query.
- `organization_id` (string): Identifier for the organization.
- `final_answer` (string): The synthesized answer that combines information from retrieved documents and graph insights, with citations to the sources.

## Sample Payloads and Responses

We've tested the Synthesizer API with several sample payloads. Here are some examples:

### 1. AI Video Tools

**Payload Description**: Query about AI tools for video generation with documents about Runway and Synthesia, and a graph insight about the marketing team's use of Runway.

**Response**: The synthesizer generated a comprehensive answer that combined information from both the retrieved documents and the graph insight. It mentioned Runway and Synthesia as AI video generation tools, described their features, and noted that the marketing team has been using Runway for their video campaigns.

### 2. Data Analysis Tools

**Payload Description**: Query about tools for data analysis with documents about Tableau, Power BI, and Python, and graph insights about the finance department's use of Power BI and the data science team's use of Python.

**Response**: The synthesizer generated an answer that described Tableau, Power BI, and Python as data analysis tools, explained their features, and incorporated the graph insights about how different departments in the organization are using these tools.

### 3. Project Management Tools

**Payload Description**: Query about project management tools for software development teams with documents about Jira, Asana, Trello, and GitHub Projects, but no graph insights.

**Response**: The synthesizer generated an answer that described the features of each project management tool and their suitability for software development teams, even without any graph insights to incorporate.

### 4. AI Writing Assistants

**Payload Description**: Query about AI tools for improving writing with documents about Grammarly, Hemingway Editor, and ProWritingAid, and a graph insight about the content marketing team's subscription to Grammarly Premium.

**Response**: The synthesizer generated an answer that described each writing tool's features and incorporated the graph insight about the availability of Grammarly Premium to the content team.

### 5. Customer Support Tools

**Payload Description**: Query about AI-powered customer support tools with documents about Zendesk, Intercom, and Freshdesk, and graph insights about the support team's use of Zendesk, the sales team's use of Intercom, and the improvement in customer satisfaction after implementing Zendesk's AI features.

**Response**: The synthesizer generated an answer that described each customer support tool's features and incorporated the graph insights about how different teams in the organization are using these tools and the impact on customer satisfaction.

## Testing Methods

We tested the Synthesizer API using both Python and curl:

### Python Testing

We created a Python script (`test_synthesizer_api.py`) that loads sample payloads from a JSON file and sends them to the API. The script measures the response time and displays the final answer for each payload.

### Curl Testing

We created a shell script (`test_synthesizer_curl.sh`) that sends sample payloads to the API using curl. The script displays the raw JSON response for each payload.

## Performance Observations

- The API typically responds within 7-14 seconds, depending on the complexity of the payload.
- The synthesizer effectively combines information from both retrieved documents and graph insights.
- The synthesizer includes citations to the sources in the final answer.
- The synthesizer can handle payloads with varying numbers of documents and insights.
- The synthesizer can generate coherent answers even when no graph insights are provided.

## Implementation Details

The Synthesizer is implemented as a node in SynthDrive's LangGraph system. It uses OpenAI's API to generate the final answer based on the retrieved documents and graph insights. The implementation can be found in `src/querying/tools/synthesizer.py`.

## Conclusion

The Synthesizer API is a powerful tool for generating comprehensive, cited answers based on retrieved documents and graph insights. It can be integrated into a RAG pipeline to provide high-quality responses to user queries.