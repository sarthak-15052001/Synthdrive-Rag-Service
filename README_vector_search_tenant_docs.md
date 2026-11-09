# Vector Search Tenant Documents API Testing

This README provides instructions for testing the `/api/v1/rag/vector-search-tenant-docs` API endpoint.

## API Endpoint

The API endpoint is:
```
POST /api/v1/rag/vector-search-tenant-docs
```

## Request Format

The API accepts the following JSON payload:

```json
{
  "query": "string",           // The search query
  "organization_id": "string", // The organization ID to filter by
  "tenant_id": "string",       // The tenant ID (default: "default")
  "filters": {                 // Optional filters
    "file_type": "string",     // Filter by file type (e.g., "pdf", "docx", "pptx")
    "tags": ["string"]         // Filter by tags
  },
  "limit": 5                   // Maximum number of results to return
}
```

## Response Format

The API returns the following JSON response:

```json
{
  "query": "string",           // The original search query
  "organization_id": "string", // The organization ID from the request
  "files": [                   // Array of matching files
    {
      "file_id": "string",
      "file_name": "string",
      "file_path": "string",
      "content_chunk": "string",
      "organization_id": "string",
      "upload_date": "string",
      "file_type": "string",
      "tags": ["string"],
      "relevance_score": 0.0,
      "citation_id": "string"
    }
  ]
}
```

## Sample Data

Sample data for testing is provided in the `sample_tenant_docs` array in the `add_sample_tenant_docs.py` script. This includes:

1. Financial Report 2023.pdf
2. Marketing Strategy 2023.docx
3. Product Roadmap 2023-2024.pptx
4. Annual Report 2023.pdf
5. Business Strategy 2023.pptx

## Sample Payloads

Sample payloads for testing are provided in the `sample_vector_search_tenant_docs_payloads.json` file. This includes:

1. Search for financial documents
2. Search for marketing strategy documents
3. Search for product roadmap
4. Search using general 2023 documents
5. Search across all document types
6. Simple search for important documents

## Testing Scripts

### 1. Add Sample Data

To add sample data to the database for testing:

```bash
python3 add_sample_tenant_docs.py
```

### 2. Test with curl

To test the API using curl, you can use the commands in the `test_vector_search_tenant_docs_curl_commands.sh` file:

```bash
# Make the script executable
chmod +x test_vector_search_tenant_docs_curl_commands.sh

# View the curl commands
./test_vector_search_tenant_docs_curl_commands.sh

# Execute a specific curl command
curl -X POST -H "Content-Type: application/json" -d '{
  "query": "financial performance report for 2023",
  "organization_id": "test_org_123",
  "tenant_id": "default",
  "filters": {
    "file_type": "pdf",
    "tags": ["financial", "2023"]
  },
  "limit": 5
}' http://localhost:8001/api/v1/rag/vector-search-tenant-docs
```

### 3. Test with Python

To test the API using Python:

```bash
python3 test_vector_search_tenant_docs_python.py
```

### 4. Test with Mock Data

To test the API with mock data (without requiring the API server to be running):

```bash
python3 mock_test_vector_search_tenant_docs.py
```

## Troubleshooting

### API Server Not Running

If the API server is not running, you'll see an error like:

```
Connection refused
```

To start the API server:

```bash
python3 src/main.py
```

### Weaviate Timeout

If you encounter a timeout error when connecting to Weaviate:

```
requests.exceptions.ReadTimeout: HTTPSConnectionPool(host='yamvfodjrrbxcvx57dua.c0.asia-southeast1.gcp.weaviate.cloud', port=443): Read timed out. (read timeout=180.0)
```

You can apply the fix for the Weaviate timeout issue:

```bash
python3 fix_weaviate_timeout.py
```

### API Response Format Issue

If the API returns an incorrect response format (e.g., organization_id is "default" instead of the value from the request), you can apply the fix for the API response format issue:

```bash
python3 apply_vector_search_tenant_docs_fix.py
```

## Expected Outputs

The expected outputs for each payload are documented in the `vector_search_tenant_docs_expected_outputs.md` file.

## Files

- `add_sample_tenant_docs.py`: Script to add sample tenant documents to the database
- `sample_vector_search_tenant_docs_payloads.json`: Sample payloads for testing
- `test_vector_search_tenant_docs_curl_commands.sh`: Curl commands for testing
- `test_vector_search_tenant_docs_python.py`: Python script for testing
- `test_vector_search_tenant_docs_direct.py`: Direct test script without relying on Weaviate client
- `mock_test_vector_search_tenant_docs.py`: Mock test script
- `fix_vector_search_tenant_docs_api.py`: Fix for the API response format issue
- `apply_vector_search_tenant_docs_fix.py`: Script to apply the API response format fix
- `fix_weaviate_timeout.py`: Fix for the Weaviate timeout issue
- `vector_search_tenant_docs_expected_outputs.md`: Expected outputs for each payload