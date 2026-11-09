# SynthDrive Tenant Files Search

## Overview

The Tenant Files Search functionality in SynthDrive RAG service enables semantically searching content from tenant-uploaded files (e.g., PDFs) with proper security isolation and citation. This feature is designed for multi-tenant environments where organization-specific data must be kept isolated.

## Key Features

- **Organization Isolation**: All content is isolated by organization_id to prevent cross-tenant access
- **Semantic Search**: Vector-based semantic search for natural language queries
- **Proper Citation**: All search results include citations to the original files
- **Prompt Generation**: Automatic generation of prompts for LLM processing with security context
- **File Metadata**: Support for file tags and metadata for better organization

## Quick Start

### 1. Upload a File

```bash
curl -X POST "http://localhost:8000/ingest/tenant-file" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@financial_report.pdf" \
  -F "organization_id=org-123" \
  -F "file_tags=financial,report,2023"
```

### 2. Search for Content

```bash
curl -X POST "http://localhost:8000/tenant-files/search" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "financial data from 2023",
    "organization_id": "org-123",
    "tenant_id": "default",
    "filters": {},
    "limit": 5
  }'
```

### 3. Search with Prompt Generation

```bash
curl -X POST "http://localhost:8000/tenant-files/search-with-prompt" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "financial data from 2023",
    "organization_id": "org-123",
    "tenant_id": "default",
    "filters": {},
    "limit": 5
  }'
```

## Example Code

See the [examples/tenant_files_example.py](examples/tenant_files_example.py) file for a complete example of how to use the tenant files search functionality in Python.

```python
# Upload a file
upload_response = upload_file(
    file_path="strategic_plan.pdf",
    organization_id="org-123",
    tenant_id="default",
    tags=["strategic", "plan", "2024"]
)

# Search for content
search_response = search_files(
    query="strategic goals for 2024",
    organization_id="org-123",
    tenant_id="default"
)

# Generate a prompt for LLM processing
prompt_response = search_with_prompt(
    query="What are our financial targets for 2025?",
    organization_id="org-123",
    tenant_id="default"
)
```

## Testing

Run the comprehensive test to verify the functionality:

```bash
python3 test_tenant_files_comprehensive.py
```

## Documentation

For detailed documentation, see [docs/tenant_files_search.md](docs/tenant_files_search.md).

## Security Considerations

- All content is isolated by organization_id to prevent cross-tenant access
- Prompts include security context to guide LLMs in maintaining confidentiality
- All endpoints require authentication
- All information is properly cited to the original files

## Implementation Details

Files are stored in two places:
1. **Raw Storage**: GCS bucket with path `gs://tenant-files/{organization_id}/{file_name}`
2. **Vector Storage**: Weaviate with organization_id as a filter

The search process:
1. User submits a query with organization_id
2. System searches Weaviate for matching content chunks with organization_id filter
3. Results are returned with proper citation to the original files
4. Optional prompt generation for LLM processing

## Troubleshooting

Common issues:

1. **File not found in search results**: Wait a few seconds after upload for indexing
2. **Cross-tenant access**: Ensure organization_id is properly set in all requests
3. **Empty search results**: Check if the query terms match the content of the files

## License

This project is licensed under the terms of the MIT license.