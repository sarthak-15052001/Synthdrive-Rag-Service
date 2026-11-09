# Tenant Uploaded Files Search

This document provides an overview of the Tenant Uploaded Files Search functionality in the SynthDrive RAG service.

## Overview

The Tenant Uploaded Files Search feature allows users to semantically search content from tenant-uploaded files (e.g., PDFs) with proper security isolation and citation. This feature ensures that:

1. Files are stored securely in GCS for raw access and citations
2. Content is chunked and embedded in Weaviate for semantic search
3. All content is isolated by organization_id to prevent cross-tenant access
4. Search results include proper citations to the original files

## Architecture

The feature consists of the following components:

1. **File Upload Endpoint**: API endpoint for uploading files with organization isolation
2. **Weaviate Storage**: Vector database for storing and searching file chunks
3. **Search Tool**: Tool for searching tenant files with organization isolation
4. **Prompt Templates**: Templates for guiding LLM responses with proper citation

## API Endpoints

### Upload Endpoint

```
POST /ingest/tenant-file
```

Parameters:
- `file`: The file to upload (multipart/form-data)
- `organization_id`: The organization ID for isolation
- `tenant_id`: The tenant ID (default: "default")
- `file_tags`: Optional comma-separated tags for the file

Example:
```bash
curl -X POST "http://localhost:8000/ingest/tenant-file" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@financial_report.pdf" \
  -F "organization_id=org-123" \
  -F "file_tags=financial,report,2023"
```

### Search Endpoint

```
POST /tenant-files/search
```

Request Body:
```json
{
  "query": "financial data from 2023",
  "organization_id": "org-123",
  "tenant_id": "default",
  "filters": {},
  "limit": 5
}
```

Response:
```json
{
  "query": "financial data from 2023",
  "files": [
    {
      "file_id": "92e5a2dd-dce6-479f-b7ed-44d95bc4f548",
      "file_name": "financial_report_2023.pdf",
      "file_path": "gs://tenant-files/org-123/financial_report_2023.pdf",
      "content_chunk": "FINANCIAL REPORT 2023...",
      "organization_id": "org-123",
      "upload_date": "2025-10-23T19:12:43Z",
      "file_type": ".pdf",
      "tags": ["financial", "report", "2023"],
      "relevance_score": 0.92,
      "citation_id": "file-1"
    }
  ]
}
```

### Search with Prompt Generation

```
POST /tenant-files/search-with-prompt
```

Request Body: Same as the search endpoint

Response:
```json
{
  "search_results": {
    "query": "financial data from 2023",
    "files": [...]
  },
  "prompt": "You are handling the SynthDrive Tenant Knowledge Domain for Uploaded Corporate Intelligence..."
}
```

## Usage Examples

### Python Client

```python
import requests
import json

# Upload a file
def upload_file(file_path, organization_id, tenant_id="default", tags=None):
    url = "http://localhost:8000/ingest/tenant-file"
    
    files = {
        'file': open(file_path, 'rb')
    }
    
    data = {
        'organization_id': organization_id,
        'tenant_id': tenant_id
    }
    
    if tags:
        data['file_tags'] = ','.join(tags)
    
    response = requests.post(
        url,
        files=files,
        data=data,
        headers={'Authorization': f'Bearer {API_TOKEN}'}
    )
    
    return response.json()

# Search for files
def search_files(query, organization_id, tenant_id="default", filters=None, limit=5):
    url = "http://localhost:8000/tenant-files/search"
    
    payload = {
        "query": query,
        "organization_id": organization_id,
        "tenant_id": tenant_id,
        "filters": filters or {},
        "limit": limit
    }
    
    response = requests.post(
        url,
        json=payload,
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {API_TOKEN}'
        }
    )
    
    return response.json()

# Search with prompt generation
def search_with_prompt(query, organization_id, tenant_id="default", filters=None, limit=5):
    url = "http://localhost:8000/tenant-files/search-with-prompt"
    
    payload = {
        "query": query,
        "organization_id": organization_id,
        "tenant_id": tenant_id,
        "filters": filters or {},
        "limit": limit
    }
    
    response = requests.post(
        url,
        json=payload,
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {API_TOKEN}'
        }
    )
    
    return response.json()
```

## Security Considerations

1. **Organization Isolation**: All content is isolated by organization_id to prevent cross-tenant access
2. **Prompt Security**: Prompts include security context to guide LLMs in maintaining confidentiality
3. **Citation**: All information is properly cited to the original files
4. **Authentication**: All endpoints require authentication

## Implementation Details

### File Storage

Files are stored in two places:
1. **Raw Storage**: GCS bucket with path `gs://tenant-files/{organization_id}/{file_name}`
2. **Vector Storage**: Weaviate with organization_id as a filter

### Search Process

1. User submits a query with organization_id
2. System searches Weaviate for matching content chunks with organization_id filter
3. Results are returned with proper citation to the original files
4. Optional prompt generation for LLM processing

### Prompt Template

The prompt template includes:
1. Security context with organization_id
2. The user's query
3. Relevant content chunks from the search results
4. Instructions for the LLM to maintain confidentiality and provide proper citation

## Testing

You can test the functionality using the provided test scripts:

1. `test_tenant_files_add_and_search.py`: Tests adding a file and searching for it
2. `test_tenant_files_comprehensive.py`: Comprehensive test for the entire flow

Example:
```bash
python3 test_tenant_files_comprehensive.py
```

## Troubleshooting

Common issues:

1. **File not found in search results**: Wait a few seconds after upload for indexing
2. **Cross-tenant access**: Ensure organization_id is properly set in all requests
3. **Empty search results**: Check if the query terms match the content of the files

## Future Improvements

1. Implement file versioning
2. Add support for more file types (currently focused on text-based files)
3. Implement more advanced chunking strategies
4. Add support for file deletion and updates