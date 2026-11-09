# Expected Outputs for Vector Search Tenant Docs API

This document outlines the expected outputs for the `/api/v1/rag/vector-search-tenant-docs` API endpoint with the provided payloads.

## Issue Identified

The API was returning an incorrect response format:
```json
{
  "query": "marketing strategy and target demographics",
  "organization_id": "default",
  "files": []
}
```

The issues were:
1. The `organization_id` was incorrectly set to "default" instead of the value from the request
2. The `files` array was empty because the filters weren't being properly applied
3. The API wasn't correctly handling the filtering logic for file_type and tags

## Fix Applied

The fix modifies the API endpoint to:
1. Correctly use the `organization_id` from the request
2. Properly apply the filters for `file_type` and `tags`
3. Return the correct response format with the filtered files

## Expected Outputs for Each Payload

### Payload 1: Search for financial documents

**Request:**
```json
{
  "query": "financial performance report for 2023",
  "organization_id": "test_org_123",
  "tenant_id": "default",
  "filters": {
    "file_type": "pdf",
    "tags": ["financial", "2023"]
  },
  "limit": 5
}
```

**Expected Response:**
```json
{
  "query": "financial performance report for 2023",
  "organization_id": "test_org_123",
  "files": [
    {
      "file_id": "file-001",
      "file_name": "Financial Report 2023.pdf",
      "file_path": "/reports/financial/2023.pdf",
      "content_chunk": "The financial performance for 2023 showed a 15% increase in revenue compared to the previous year. Key growth areas included cloud services and AI solutions.",
      "organization_id": "test_org_123",
      "upload_date": "2023-12-15T00:00:00Z",
      "file_type": "pdf",
      "tags": ["financial", "2023"],
      "relevance_score": 0.95,
      "citation_id": "tenant-doc-1"
    }
  ]
}
```

### Payload 2: Search for marketing strategy documents

**Request:**
```json
{
  "query": "marketing strategy and target demographics",
  "organization_id": "test_org_123",
  "tenant_id": "default",
  "filters": {
    "file_type": "docx",
    "tags": ["marketing", "strategy"]
  },
  "limit": 5
}
```

**Expected Response:**
```json
{
  "query": "marketing strategy and target demographics",
  "organization_id": "test_org_123",
  "files": [
    {
      "file_id": "file-002",
      "file_name": "Marketing Strategy 2023.docx",
      "file_path": "/marketing/strategy/2023.docx",
      "content_chunk": "Our marketing strategy for 2023 focuses on digital channels, with increased investment in social media and content marketing. Target demographics include tech professionals aged 25-45.",
      "organization_id": "test_org_123",
      "upload_date": "2023-01-10T00:00:00Z",
      "file_type": "docx",
      "tags": ["marketing", "strategy", "2023"],
      "relevance_score": 0.92,
      "citation_id": "tenant-doc-2"
    }
  ]
}
```

### Payload 3: Search for product roadmap

**Request:**
```json
{
  "query": "product roadmap and AI-powered analytics platform",
  "organization_id": "test_org_123",
  "tenant_id": "default",
  "filters": {
    "file_type": "pptx",
    "tags": ["product", "roadmap"]
  },
  "limit": 5
}
```

**Expected Response:**
```json
{
  "query": "product roadmap and AI-powered analytics platform",
  "organization_id": "test_org_123",
  "files": [
    {
      "file_id": "file-003",
      "file_name": "Product Roadmap 2023-2024.pptx",
      "file_path": "/product/roadmap/2023-2024.pptx",
      "content_chunk": "The product roadmap for 2023-2024 includes the launch of our AI-powered analytics platform in Q2 2023, followed by the mobile app integration in Q4 2023.",
      "organization_id": "test_org_123",
      "upload_date": "2023-02-28T00:00:00Z",
      "file_type": "pptx",
      "tags": ["product", "roadmap", "2023", "2024"],
      "relevance_score": 0.89,
      "citation_id": "tenant-doc-3"
    }
  ]
}
```

### Payload 4: Search using general 2023 documents

**Request:**
```json
{
  "query": "all reports and documents for 2023",
  "organization_id": "test_org_123",
  "tenant_id": "default",
  "filters": {
    "tags": ["2023"]
  },
  "limit": 5
}
```

**Expected Response:**
```json
{
  "query": "all reports and documents for 2023",
  "organization_id": "test_org_123",
  "files": [
    {
      "file_id": "file-001",
      "file_name": "Financial Report 2023.pdf",
      "file_path": "/reports/financial/2023.pdf",
      "content_chunk": "The financial performance for 2023 showed a 15% increase in revenue compared to the previous year. Key growth areas included cloud services and AI solutions.",
      "organization_id": "test_org_123",
      "upload_date": "2023-12-15T00:00:00Z",
      "file_type": "pdf",
      "tags": ["financial", "2023"],
      "relevance_score": 0.88,
      "citation_id": "tenant-doc-1"
    },
    {
      "file_id": "file-002",
      "file_name": "Marketing Strategy 2023.docx",
      "file_path": "/marketing/strategy/2023.docx",
      "content_chunk": "Our marketing strategy for 2023 focuses on digital channels, with increased investment in social media and content marketing. Target demographics include tech professionals aged 25-45.",
      "organization_id": "test_org_123",
      "upload_date": "2023-01-10T00:00:00Z",
      "file_type": "docx",
      "tags": ["marketing", "strategy", "2023"],
      "relevance_score": 0.85,
      "citation_id": "tenant-doc-2"
    },
    {
      "file_id": "file-003",
      "file_name": "Product Roadmap 2023-2024.pptx",
      "file_path": "/product/roadmap/2023-2024.pptx",
      "content_chunk": "The product roadmap for 2023-2024 includes the launch of our AI-powered analytics platform in Q2 2023, followed by the mobile app integration in Q4 2023.",
      "organization_id": "test_org_123",
      "upload_date": "2023-02-28T00:00:00Z",
      "file_type": "pptx",
      "tags": ["product", "roadmap", "2023", "2024"],
      "relevance_score": 0.82,
      "citation_id": "tenant-doc-3"
    },
    {
      "file_id": "file-004",
      "file_name": "Annual Report 2023.pdf",
      "file_path": "/reports/annual/2023.pdf",
      "content_chunk": "Annual report for 2023 fiscal year. This document contains financial statements, business performance analysis, and future outlook for all business units.",
      "organization_id": "test_org_123",
      "upload_date": "2023-12-31T00:00:00Z",
      "file_type": "pdf",
      "tags": ["2023", "annual", "report"],
      "relevance_score": 0.80,
      "citation_id": "tenant-doc-4"
    }
  ]
}
```

### Payload 5: Search across all document types

**Request:**
```json
{
  "query": "business strategy and performance insights",
  "organization_id": "test_org_123",
  "tenant_id": "default",
  "filters": {},
  "limit": 5
}
```

**Expected Response:**
```json
{
  "query": "business strategy and performance insights",
  "organization_id": "test_org_123",
  "files": [
    {
      "file_id": "file-005",
      "file_name": "Business Strategy 2023.pptx",
      "file_path": "/strategy/business/2023.pptx",
      "content_chunk": "Business strategy and performance insights for 2023. This presentation outlines our core business objectives, market analysis, and strategic initiatives for the coming year.",
      "organization_id": "test_org_123",
      "upload_date": "2023-01-05T00:00:00Z",
      "file_type": "pptx",
      "tags": ["business", "strategy", "performance"],
      "relevance_score": 0.95,
      "citation_id": "tenant-doc-5"
    },
    {
      "file_id": "file-001",
      "file_name": "Financial Report 2023.pdf",
      "file_path": "/reports/financial/2023.pdf",
      "content_chunk": "The financial performance for 2023 showed a 15% increase in revenue compared to the previous year. Key growth areas included cloud services and AI solutions.",
      "organization_id": "test_org_123",
      "upload_date": "2023-12-15T00:00:00Z",
      "file_type": "pdf",
      "tags": ["financial", "2023"],
      "relevance_score": 0.78,
      "citation_id": "tenant-doc-1"
    },
    {
      "file_id": "file-002",
      "file_name": "Marketing Strategy 2023.docx",
      "file_path": "/marketing/strategy/2023.docx",
      "content_chunk": "Our marketing strategy for 2023 focuses on digital channels, with increased investment in social media and content marketing. Target demographics include tech professionals aged 25-45.",
      "organization_id": "test_org_123",
      "upload_date": "2023-01-10T00:00:00Z",
      "file_type": "docx",
      "tags": ["marketing", "strategy", "2023"],
      "relevance_score": 0.75,
      "citation_id": "tenant-doc-2"
    },
    {
      "file_id": "file-004",
      "file_name": "Annual Report 2023.pdf",
      "file_path": "/reports/annual/2023.pdf",
      "content_chunk": "Annual report for 2023 fiscal year. This document contains financial statements, business performance analysis, and future outlook for all business units.",
      "organization_id": "test_org_123",
      "upload_date": "2023-12-31T00:00:00Z",
      "file_type": "pdf",
      "tags": ["2023", "annual", "report"],
      "relevance_score": 0.72,
      "citation_id": "tenant-doc-4"
    }
  ]
}
```

## Notes

- The actual relevance scores may vary depending on the embedding model and the specific content of the documents.
- The order of the files in the response may vary depending on the relevance scores.
- The citation_id values are generated by the system and may vary.
- The actual number of files returned may be less than the limit if there are fewer matching files in the database.