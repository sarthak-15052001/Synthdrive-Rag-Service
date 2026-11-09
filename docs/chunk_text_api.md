# Chunking Text API

## Overview

The Chunking Text API is part of SynthDrive's RAG service ingestion flow. It applies a semantic chunking algorithm to break raw text into meaningful paragraphs or chunks based on semantic coherence rather than arbitrary character counts.

## Endpoint

```
POST /api/v1/rag/ingest/chunk-text
```

## Request Format

The API accepts a JSON payload with the following structure:

```json
{
  "file_id": "unique-file-identifier",
  "organization_id": "organization-identifier",
  "tenant_id": "tenant-identifier",
  "raw_text": "The text content to be chunked...",
  "status": "processing",
  "processing_log": ["Optional log entries"]
}
```

### Request Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| file_id | string | Yes | Unique identifier for the file being processed |
| organization_id | string | Yes | Identifier for the organization that owns the file |
| tenant_id | string | No | Tenant identifier for multi-tenancy (defaults to "default") |
| raw_text | string | Yes | The text content to be chunked |
| status | string | No | Current status of processing (defaults to "processing") |
| processing_log | array | No | Array of log entries for tracking processing history |

## Response Format

The API returns a JSON response with the following structure:

```json
{
  "file_id": "unique-file-identifier",
  "organization_id": "organization-identifier",
  "chunks": [
    {
      "content": "Chunk content...",
      "metadata": {
        "chunk_id": 0,
        "chunk_type": "semantic",
        "semantic_type": "introduction",
        "chunk_index": 0,
        "total_chunks": 5,
        "file_id": "unique-file-identifier",
        "organization_id": "organization-identifier",
        "chunking_method": "ai_semantic"
      }
    },
    // Additional chunks...
  ],
  "status": "chunked",
  "processing_log": [
    "Started chunking at 2025-10-24T11:00:00Z",
    "Created 5 chunks using AI semantic chunking",
    "Completed semantic chunking at 2025-10-24T11:00:05Z"
  ]
}
```

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| file_id | string | Unique identifier for the file being processed |
| organization_id | string | Identifier for the organization that owns the file |
| chunks | array | Array of chunk objects containing content and metadata |
| status | string | Status of the chunking process (e.g., "chunked", "failed") |
| processing_log | array | Array of log entries tracking the processing history |

### Chunk Object

Each chunk in the response contains:

| Field | Type | Description |
|-------|------|-------------|
| content | string | The text content of the chunk |
| metadata | object | Metadata about the chunk |

### Chunk Metadata

| Field | Type | Description |
|-------|------|-------------|
| chunk_id | integer | Unique identifier for the chunk |
| chunk_type | string | Type of chunk (e.g., "semantic", "paragraph") |
| semantic_type | string | Semantic classification of the chunk (e.g., "introduction", "concept_explanation") |
| chunk_index | integer | Index of the chunk in the sequence |
| total_chunks | integer | Total number of chunks created |
| file_id | string | Reference to the file ID |
| organization_id | string | Reference to the organization ID |
| chunking_method | string | Method used for chunking (e.g., "ai_semantic", "simple_paragraph") |

## Chunking Methods

The API uses different chunking methods depending on the text:

1. **AI Semantic Chunking** - For longer texts, uses OpenAI's GPT-4o model to identify semantic boundaries and create meaningful chunks.
2. **Simple Paragraph Chunking** - For shorter texts or as a fallback, uses paragraph breaks to create chunks.

## Error Handling

If the chunking process fails, the API will return a 500 status code with an error message in the response body.

## Example Usage

### Request

```bash
curl -X POST "http://localhost:8001/api/v1/rag/ingest/chunk-text" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-token" \
  -d '{
    "file_id": "file-123",
    "organization_id": "org-456",
    "raw_text": "This is a sample text that needs to be chunked into semantic paragraphs. It contains multiple sentences and ideas that should be grouped together based on their meaning and context. The chunking algorithm will analyze this text and break it into meaningful segments."
  }'
```

### Response

```json
{
  "file_id": "file-123",
  "organization_id": "org-456",
  "chunks": [
    {
      "content": "This is a sample text that needs to be chunked into semantic paragraphs.",
      "metadata": {
        "chunk_id": 0,
        "chunk_type": "semantic",
        "semantic_type": "introduction",
        "chunk_index": 0,
        "total_chunks": 2,
        "file_id": "file-123",
        "organization_id": "org-456",
        "chunking_method": "ai_semantic"
      }
    },
    {
      "content": "It contains multiple sentences and ideas that should be grouped together based on their meaning and context. The chunking algorithm will analyze this text and break it into meaningful segments.",
      "metadata": {
        "chunk_id": 1,
        "chunk_type": "semantic",
        "semantic_type": "explanation",
        "chunk_index": 1,
        "total_chunks": 2,
        "file_id": "file-123",
        "organization_id": "org-456",
        "chunking_method": "ai_semantic"
      }
    }
  ],
  "status": "chunked",
  "processing_log": [
    "Started chunking at 2025-10-24T11:00:00Z",
    "Created 2 chunks using AI semantic chunking",
    "Completed semantic chunking at 2025-10-24T11:00:05Z"
  ]
}
```

## Integration with Ingestion Pipeline

This API is part of the SynthDrive RAG service ingestion pipeline. It can be used:

1. As a standalone service to chunk text
2. As part of the full ingestion pipeline that includes:
   - Document loading and parsing
   - Semantic chunking
   - Entity extraction
   - Vector embedding generation
   - Storage in vector and graph databases