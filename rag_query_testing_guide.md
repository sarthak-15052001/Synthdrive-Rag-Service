# SynthDrive RAG Query API Testing Guide

This guide provides instructions for testing the `/api/v1/rag/query` endpoint in the SynthDrive RAG Service, with a focus on GraphRAG capabilities.

## Overview

The `/api/v1/rag/query` endpoint is a key component of the SynthDrive RAG Service that allows users to query the system with natural language questions. The endpoint processes the query through the querying graph and returns a streaming response with answers and citations.

GraphRAG enhances traditional RAG by incorporating graph-based knowledge retrieval alongside vector search, providing more contextual and accurate responses.

## Test Scripts

### Combined Test Scripts

For convenience, two combined test scripts are provided:

#### 1. General RAG Query Testing

```bash
# Make the script executable
chmod +x run_rag_query_tests.sh

# Run the script
./run_rag_query_tests.sh
```

This script:
1. Ingests sample data about SynthDrive RAG Service
2. Waits for processing to complete
3. Runs the curl tests
4. Runs the Python tests
5. Runs the GraphRAG contextualizer tests

#### 2. Tenant Files Testing

```bash
# Make the script executable
chmod +x run_tenant_files_tests.sh

# Run the script
./run_tenant_files_tests.sh
```

This script:
1. Ingests sample tenant files (business strategy, financial reports, etc.)
2. Waits for processing to complete
3. Runs the curl tests with tenant file filters
4. Runs the Python tests with tenant file filters

These combined scripts are the recommended way to run the tests as they ensure all the necessary data is ingested before testing.

### Individual Test Scripts

If you prefer to run the tests individually, you can use the following scripts:

#### Curl Script

The `test_rag_query_graphrag_curl.sh` script tests the RAG query API endpoint using curl commands with various parameters:

```bash
# Make the script executable
chmod +x test_rag_query_graphrag_curl.sh

# Run the script
./test_rag_query_graphrag_curl.sh
```

This script includes 5 test cases:
1. Basic query with default parameters
2. Query with specific filters
3. Query with higher top_k value
4. Query with custom tenant ID
5. Complex query with multiple filters

#### Python Script

The `test_rag_query_graphrag.py` script tests the RAG query API endpoint using Python's requests library:

```bash
# Run the script
python test_rag_query_graphrag.py
```

This script includes the same test cases as the curl script but with more detailed logging and response processing.

#### GraphRAG Contextualizer Test

The `test_graph_rag_contextualizer.py` script specifically tests the GraphRAG contextualizer endpoint:

```bash
# Run the script
python test_graph_rag_contextualizer.py
```

This script tests how the GraphRAG contextualizer enhances queries with graph-based context.

## Sample Payloads

### Basic RAG Query Payloads

The `rag_query_graphrag_payloads.json` file contains 15 sample payloads for testing various aspects of the RAG query API:

1. Basic Query
2. Document Type Filter
3. Tag-based Filter
4. Author Filter
5. Multiple Filters
6. High Precision
7. Custom Tenant
8. Relationship Query
9. Multi-hop Query
10. Complex Technical Query
11. Entity-focused Query
12. Process Query
13. Comparison Query
14. Implementation Query
15. Performance Query

### Tenant Files Query Payloads

The `test_rag_query_tenant_files.py` and `test_rag_query_tenant_files_curl.sh` scripts generate sample payloads for querying tenant files in the `tenant_file_payloads` directory:

1. Business Strategy Query - Filters by tags and organization ID
2. Financial Performance Query - Filters by file type and tags
3. Marketing Strategy Query - Filters by file path and tags
4. Product Roadmap Query - Filters by tags and organization ID
5. Annual Report Query - Filters by file name and tags

These payloads demonstrate how to use various filter combinations to target specific tenant files in the Weaviate TenantUploadedFiles collection.

### GraphRAG Contextualizer Payloads

The `test_graph_rag_contextualizer.py` script generates sample payloads for the GraphRAG contextualizer in the `graph_rag_payloads` directory:

1. Basic Graph Context
2. Entity Relationships
3. Multi-hop Reasoning
4. Complex Graph Query
5. Knowledge Graph Exploration

## Testing Approach

### 1. Basic Functionality Testing

Start with basic queries to ensure the API is functioning correctly:

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer test-token" \
  -d '{"query_str": "What is SynthDrive RAG Service?", "tenant_id": "default", "top_k": 5}' \
  --no-buffer \
  http://localhost:8000/api/v1/rag/query
```

### 2. Filter Testing

Test queries with various filters to ensure they are applied correctly:

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer test-token" \
  -d '{"query_str": "How does the ingestion pipeline work?", "tenant_id": "default", "top_k": 5, "filters": {"document_type": "documentation", "tags": ["rag", "ingestion"]}}' \
  --no-buffer \
  http://localhost:8000/api/v1/rag/query
```

### 3. Tenant Files Testing

Test queries with tenant file-specific filters to retrieve information from the TenantUploadedFiles collection:

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer test-token" \
  -d '{"query_str": "What are the key business objectives for 2023?", "tenant_id": "default", "top_k": 5, "filters": {"tags": ["business", "strategy"], "organization_id": "test_org_123"}}' \
  --no-buffer \
  http://localhost:8000/api/v1/rag/query
```

You can use various filter combinations to target specific tenant files:

- Filter by tags: `"filters": {"tags": ["financial", "2023"]}`
- Filter by file type: `"filters": {"file_type": "pdf"}`
- Filter by file path: `"filters": {"file_path": "/marketing/strategy/2023.docx"}`
- Filter by file name: `"filters": {"file_name": "Annual Report 2023.pdf"}`
- Filter by organization ID: `"filters": {"organization_id": "test_org_123"}`

### 4. GraphRAG-specific Testing

Test GraphRAG-specific features using the contextualizer endpoint:

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer test-token" \
  -d '{"query": "How does SynthDrive use Neo4j?", "organization_id": "default", "tenant_id": "default", "retrieved_docs": [...]}' \
  http://localhost:8000/api/v1/rag/graph-rag-contextualizer
```

## Expected Results

When running the tests, you should expect:

1. A streaming response that includes:
   - An answer to the query
   - Citations to relevant sources
   - Reasoning behind the answer (if available)
   - Synthesis of information (if available)

2. For GraphRAG-specific tests, you should see:
   - Graph insights that provide context from the knowledge graph
   - Explanations of relationships between entities
   - Inferred context that enhances the retrieved documents

## Troubleshooting

If you encounter issues:

1. Ensure the SynthDrive RAG Service is running on `http://localhost:8000`
2. Check that the authentication token is valid
3. Verify that the Weaviate and Neo4j databases are properly configured and accessible
4. Check the logs for any error messages

If you see "No reasoning available" or similar messages, this typically means:
- The system may not have any data ingested yet
- The query processing pipeline might not be generating reasoning
- You may need to ingest some documents first using the ingestion endpoints

## Sample Data Ingestion

Before testing, you need to ingest sample data to get meaningful responses. Use the provided script:

```bash
python ingest_sample_data_for_testing.py
```

This script ingests 7 sample documents with rich content about:
- SynthDrive RAG Service overview
- Ingestion pipeline details
- GraphRAG implementation
- Entity extraction and relationship mapping
- Neo4j usage in SynthDrive
- Multi-tenant architecture
- GraphRAG vs traditional RAG (in a custom tenant)

The script waits 30 seconds for processing to complete, but you may need to wait longer depending on your system's performance.

If you see empty responses like:
```
data: {"answer": "I don't have enough information to answer that question."}
data: {"citations": []}
data: {"reasoning": ""}
data: {"synthesis": ""}
```

It means the data hasn't been fully processed yet or there might be an issue with the ingestion. Try waiting longer or check the server logs for any errors.

## Extending the Tests

To add more test cases:
1. Add new payloads to the `rag_query_graphrag_payloads.json` file
2. Modify the test scripts to include additional test cases
3. Create custom test scripts for specific testing scenarios

## GraphRAG vs. Traditional RAG

When testing, note the differences between GraphRAG and traditional RAG:

1. **Traditional RAG**:
   - Uses vector search to find relevant documents
   - Limited to the content explicitly stated in documents
   - May struggle with complex relationships between entities

2. **GraphRAG**:
   - Combines vector search with graph-based knowledge retrieval
   - Can infer relationships not explicitly stated in any single document
   - Provides more contextual and accurate responses for complex queries
   - Supports multi-hop reasoning across the knowledge graph

Look for these enhancements in the responses when testing GraphRAG features.