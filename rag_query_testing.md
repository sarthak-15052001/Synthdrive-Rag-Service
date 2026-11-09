# RAG Query API Testing

This document describes the testing approach for the `/api/v1/rag/query` endpoint in the SynthDrive RAG Service.

## Overview

The `/api/v1/rag/query` endpoint is a key component of the SynthDrive RAG Service that allows users to query the system with natural language questions. The endpoint processes the query through the querying graph and returns a streaming response with answers and citations.

Two testing methods have been implemented:
1. A Python script that uses the `requests` library
2. A bash script that uses `curl`

## Python Testing Script

The Python script (`test_rag_query_api.py`) tests the RAG query API endpoint by sending multiple test queries and processing the streaming response.

### Features:
- Sends multiple test queries to the endpoint
- Handles Server-Sent Events (SSE) streaming response
- Processes and displays different parts of the response (answer, citations, reasoning, synthesis)
- Provides detailed logging

### Usage:
```bash
python test_rag_query_api.py
```

## Curl Testing Script

The bash script (`test_rag_query_curl.sh`) tests the RAG query API endpoint using curl commands.

### Features:
- Sends multiple test queries to the endpoint
- Displays the raw streaming response
- Simple to use and modify

### Usage:
```bash
./test_rag_query_curl.sh
```

## Test Queries

Both scripts use the following test queries:
1. "What is SynthDrive RAG Service?"
2. "How does the ingestion pipeline work?"
3. "What are the key features of the system?"

These queries are designed to test different aspects of the RAG system's knowledge and retrieval capabilities.

## Expected Results

When running the tests, you should expect:

1. A streaming response that includes:
   - An answer to the query
   - Citations to relevant sources
   - Reasoning behind the answer (if available)
   - Synthesis of information (if available)

2. The response should be relevant to the query and include information from the system's knowledge base.

### Understanding "No reasoning available" Messages

If you see messages like "No reasoning available" or "I don't have enough information to answer that question", this typically means:

1. **No Data Ingested**: The system may not have any documents or data ingested yet. You'll need to use the ingestion endpoints to add documents to the system before meaningful responses can be generated.

2. **Missing Pipeline Component**: The query processing pipeline might not be generating reasoning or synthesis components.

3. **Empty Knowledge Base**: The vector database or graph database might be empty or not properly configured.

To resolve this:
- Use the ingestion endpoints to add documents to the system
- Check the database connections and configurations
- Verify that all components of the RAG pipeline are functioning correctly

## Sample Document Ingestion

A helper script `test_ingest_sample_document.py` has been provided to ingest a sample document about the SynthDrive RAG Service. This will help populate the system with data so that the query endpoint can return meaningful responses.

### Usage:
```bash
python3 test_ingest_sample_document.py
```

After running this script, wait a moment for the document to be fully processed, then try running the query tests again. You should now receive more meaningful responses that include actual content about the SynthDrive RAG Service.

## Direct Testing Scripts

For more streamlined testing, two additional scripts have been provided that combine document ingestion and querying in a single flow:

### Python Direct Test Script

The `test_rag_query_direct.py` script:
1. Ingests a sample document
2. Waits for processing
3. Queries the system with multiple test queries

```bash
python3 test_rag_query_direct.py
```

### Curl Direct Test Script

The `test_rag_query_direct_curl.sh` script performs the same operations using curl commands:

```bash
./test_rag_query_direct_curl.sh
```

These direct testing scripts are useful for quick end-to-end testing of the RAG query API without having to manually run separate ingestion and query steps.

## Troubleshooting

If you encounter issues:

1. Ensure the SynthDrive RAG Service is running on `http://localhost:8000`
2. Check that the authentication token is valid
3. Verify that the Weaviate and Neo4j databases are properly configured and accessible
4. Check the logs for any error messages

## Extending the Tests

To add more test queries:

1. In the Python script, add new queries to the `test_queries` list
2. In the curl script, add new sections with different query payloads

To test with different parameters:
1. Modify the `payload` dictionary in the Python script
2. Edit the JSON in the curl script to include different parameters