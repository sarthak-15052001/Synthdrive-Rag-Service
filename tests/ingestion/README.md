# Ingestion Pipeline Tests

This directory contains tests for the ingestion pipeline, which is responsible for processing documents, extracting entities, and storing data in the appropriate data stores.

## Test Files

- `test_ingestion_pipeline.py`: Unit tests for individual components of the ingestion pipeline
- `test_integration.py`: Integration tests that verify the end-to-end functionality of the ingestion pipeline
- `conftest.py`: Common test fixtures and utilities
- `test_data.txt`: Sample data for testing

## Running the Tests

### Unit Tests

To run the unit tests, use the following command:

```bash
pytest tests/ingestion/test_ingestion_pipeline.py -v
```

These tests use mocks and don't require actual database connections.

### Integration Tests

To run the integration tests, you need to have the following services running:

- PostgreSQL
- Weaviate
- Neo4j

Make sure your `.env` file contains the correct connection details for these services.

Run the integration tests with:

```bash
pytest tests/ingestion/test_integration.py -v
```

### All Tests

To run all tests, use:

```bash
pytest tests/ingestion/ -v
```

## Test Coverage

The tests cover the following aspects of the ingestion pipeline:

1. **Document Loading**: Testing the ability to load documents from files and direct content
2. **Chunking and Embedding**: Testing the document chunking and embedding generation
3. **Entity Extraction**: Testing the extraction of entities and relationships from documents
4. **Routing Logic**: Testing the conditional routing to different data stores
5. **Storage Operations**: Testing the storage of data in Weaviate and Neo4j
6. **Multi-tenancy**: Testing data isolation between different tenants
7. **Error Handling**: Testing the pipeline's behavior when errors occur

## Adding New Tests

When adding new tests, consider the following:

1. Unit tests should be added to `test_ingestion_pipeline.py`
2. Integration tests should be added to `test_integration.py`
3. Common fixtures should be added to `conftest.py`
4. If you need additional test data, add it to the `tests/ingestion/` directory