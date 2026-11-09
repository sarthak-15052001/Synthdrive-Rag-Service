# RAG Querying System - Testing and Usage Guide

This document provides instructions on how to run and test the RAG (Retrieval-Augmented Generation) querying system.

## Prerequisites

Ensure you have the following services running:

1. **Weaviate** - Vector database for semantic search
2. **Neo4j** - Graph database for relationship traversal
3. **PostgreSQL** - Relational database for structured data

## Environment Setup

1. Make sure you have Python 3.8+ and pip installed.

2. Install the required dependencies:

```bash
# Activate your virtual environment (if using one)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

3. Copy the `.env.example` file to `.env` and fill in the required credentials:

```bash
cp .env.example .env
```

4. Update the `.env` file with your service credentials:

```
# OpenAI API
OPENAI_API_KEY=your_openai_api_key
LLM_MODEL=gpt-3.5-turbo
EMBEDDING_MODEL=text-embedding-ada-002

# Weaviate
WEAVIATE_URL=http://localhost:8080
WEAVIATE_API_KEY=your_weaviate_api_key

# Neo4j
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_neo4j_password

# PostgreSQL
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_postgres_password
POSTGRES_DB=rag_service

# Testing
ENABLE_INTEGRATION_TESTS=false
```

## Running Unit Tests

To run the unit tests with mocked dependencies:

```bash
pytest tests/querying/test_querying.py -v
```

## Running Integration Tests

1. First, set `ENABLE_INTEGRATION_TESTS=true` in your `.env` file.

2. Run the integration tests:

```bash
pytest tests/querying/test_integration.py -v
```

Note: Integration tests will seed test data into your databases.

## Using the Querying System

### Basic Usage

You can use the querying system in your application as follows:

```python
from src.data_stores.weaviate_client import WeaviateClient
from src.data_stores.neo4j_client import Neo4jClient
from src.data_stores.postgres_client import PostgresClient
from src.querying.agent import QueryAgent

# Initialize clients
weaviate_client = WeaviateClient()
neo4j_client = Neo4jClient()
postgres_client = PostgresClient()

# Create the query agent
agent = QueryAgent(
    postgres_client=postgres_client,
    weaviate_client=weaviate_client,
    neo4j_client=neo4j_client
)

# Query the system
result = agent.query(
    query="What is artificial intelligence?",
    filters={"tenant_id": "default"},
    top_k=5
)

# Access the results
answer = result["answer"]
sources = result["sources"]  # Citations
```

### Async Usage

For asynchronous usage:

```python
import asyncio

async def query_async():
    # Initialize clients (same as above)
    
    # Create the query agent
    agent = QueryAgent(
        postgres_client=postgres_client,
        weaviate_client=weaviate_client,
        neo4j_client=neo4j_client
    )
    
    # Query the system asynchronously
    result = await agent.query_async(
        query="What is artificial intelligence?",
        filters={"tenant_id": "default"},
        top_k=5
    )
    
    return result

# Run the async function
result = asyncio.run(query_async())
```

## Example Queries

Here are some example queries to test the system:

1. **Simple factual query**:
   - "What is artificial intelligence?"
   - "Define machine learning."

2. **Relationship queries**:
   - "How are machine learning and deep learning related?"
   - "What fields are part of artificial intelligence?"

3. **Complex queries**:
   - "Explain the differences between supervised and unsupervised learning in AI."
   - "How can natural language processing be applied in healthcare?"

## Troubleshooting

### Common Issues

1. **OpenAI API errors**:
   - Ensure your API key is valid
   - Check your usage limits and billing status

2. **Database connection issues**:
   - Verify that all database services are running
   - Check connection credentials in the `.env` file
   - Ensure network connectivity to the database services

3. **Test failures**:
   - For integration tests, ensure databases are properly seeded
   - Check that the required environment variables are set correctly

### Logs

Check the application logs for detailed error messages:

```bash
tail -f logs/app.log
```

## Advanced Configuration

For advanced configuration options, refer to `src/core/config.py`.