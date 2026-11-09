# Learning Resource Weaviate Storage Fix

## Issue Summary

### Problem
When ingesting learning resources via the `/api/v1/rag/ingest/global/learning-resource` endpoint, data was not being saved according to the payload structure:

1. **Incorrect Structure**: Nested structures like `categories`, `target_audience`, and `content` were being flattened into separate top-level fields
2. **Data Duplication**: Fields appeared twice - once as nested structure and once as flattened fields
3. **Structure Not Matching Payload**: The stored structure didn't match the API payload format

### Expected Payload Structure
```json
{
  "title": "Introduction to AI Ethics",
  "categories": {
    "primary": "AI Ethics",
    "secondary": ["Responsible AI", "AI Governance"]
  },
  "target_audience": {
    "expertise_level": "intermediate",
    "job_roles": ["Data Scientist", "AI Engineer", "Product Manager"]
  },
  "content": {
    "summary": "...",
    "full_text": "...",
    "video_transcript": null,
    "video_url": null,
    "image_analysis": [...]
  }
}
```

### What Was Happening (WRONG)
Data was stored as:
```
- primary_category: "AI Ethics"
- secondary_categories: ["Responsible AI", "AI Governance"]
- expertise_level: "intermediate"
- job_roles: ["Data Scientist", "AI Engineer", "Product Manager"]
- summary: "..."
- full_text: "..."
- video_transcript: null
- video_url: null
```

### What Should Happen (CORRECT)
Data should be stored matching the payload structure with nested objects preserved.

## Root Cause

Weaviate doesn't natively support nested JSON objects - it only supports primitive data types (string, string[], text, number, date, boolean). The previous implementation was flattening nested structures to primitive fields, causing the structure mismatch.

## Solution

### Approach: Store Nested Structures as JSON Strings

Since Weaviate doesn't support nested objects, we store complex nested structures as JSON strings (text dataType), which can be parsed back when retrieved.

### Schema Changes

Updated [`_create_global_learning_resources_class`](src/data_stores/weaviate_client.py:235) in [`src/data_stores/weaviate_client.py`](src/data_stores/weaviate_client.py:235):

**Before (Flattened Schema):**
```python
"properties": [
    {"name": "primary_category", "dataType": ["string"]},
    {"name": "secondary_categories", "dataType": ["string[]"]},
    {"name": "expertise_level", "dataType": ["string"]},
    {"name": "job_roles", "dataType": ["string[]"]},
    {"name": "summary", "dataType": ["text"]},
    {"name": "full_text", "dataType": ["text"]},
    ...
]
```

**After (JSON Schema):**
```python
"properties": [
    {"name": "categories_json", "dataType": ["text"]},  # Stores entire categories object as JSON
    {"name": "target_audience_json", "dataType": ["text"]},  # Stores entire target_audience object as JSON
    {"name": "content_json", "dataType": ["text"]},  # Stores entire content object as JSON (preserves nulls)
    ...
]
```

### Storage Method Changes

Updated [`add_learning_resource`](src/data_stores/weaviate_client.py:1452) method:

```python
# Convert nested structures to JSON strings
categories_json = json.dumps(resource_data.get("categories", {}))
target_audience_json = json.dumps(resource_data.get("target_audience", {}))
content_json = json.dumps(resource_data.get("content", {}))  # Preserves null values

# Store in Weaviate
weaviate_data = {
    "title": resource_data.get("title", ""),
    "description": resource_data.get("description", ""),
    "source_url": resource_data.get("source_url", ""),
    "resource_type": resource_data.get("resource_type", ""),
    "categories_json": categories_json,  # JSON string
    "topics_discussed": resource_data.get("topics_discussed", []),
    "target_audience_json": target_audience_json,  # JSON string
    "useful_context": resource_data.get("useful_context", []),
    "content_json": content_json,  # JSON string (preserves null)
    "tags": resource_data.get("tags", []),
    "estimatedTime": resource_data.get("estimatedTime", ""),
    "last_scraped_at": last_scraped_at,
    "resource_id": resource_id,
    "tenant_id": tenant_id
}
```

### Retrieval Method Changes

Updated [`query_documents`](src/data_stores/weaviate_client.py:974) method to parse JSON back to objects:

```python
# Parse JSON fields to reconstruct original payload structure
categories = json.loads(res.get("categories_json", "{}"))
target_audience = json.loads(res.get("target_audience_json", "{}"))
content = json.loads(res.get("content_json", "{}"))

documents.append({
    "id": res["_additional"]["id"],
    "resource_id": res.get("resource_id", ""),
    "title": res.get("title", ""),
    "description": res.get("description", ""),
    "source_url": res.get("source_url", ""),
    "resource_type": res.get("resource_type", ""),
    "categories": categories,  # Reconstructed nested object
    "topics_discussed": res.get("topics_discussed", []),
    "target_audience": target_audience,  # Reconstructed nested object
    "useful_context": res.get("useful_context", []),
    "content": content,  # Reconstructed nested object (preserves nulls)
    "tags": res.get("tags", []),
    "estimatedTime": res.get("estimatedTime", ""),
    "last_scraped_at": res.get("last_scraped_at", ""),
    "tenant_id": res.get("tenant_id", "default"),
    "relevance_score": res["_additional"]["certainty"]
})
```

## Key Benefits

1. **Exact Structure Match**: Data stored in Weaviate now matches the API payload structure exactly
2. **Nested Objects Preserved**: `categories`, `target_audience`, and `content` maintain their nested structure
3. **Null Values Preserved**: JSON serialization preserves null values for `video_transcript` and `video_url`
4. **No Duplication**: Each piece of data is stored exactly once
5. **Easy Retrieval**: When retrieved, JSON is parsed back to recreate the original structure

## How It Works

### During Storage (POST API)
```
API Payload (nested objects)
        ↓
JSON.stringify() nested structures
        ↓
Store in Weaviate as JSON strings
        ↓
Stored format: categories_json, target_audience_json, content_json
```

### During Retrieval (GET/Search)
```
Retrieve from Weaviate (JSON strings)
        ↓
JSON.parse() JSON strings
        ↓
Return nested objects matching original payload
```

## Testing

### Test Script
Created [`test_learning_resource_fix.py`](test_learning_resource_fix.py:1) to verify the fix.

### How to Test

1. **Start the server**:
   ```bash
   python run_server.py
   ```

2. **Run the test**:
   ```bash
   python test_learning_resource_fix.py
   ```

3. **Verify in Weaviate Cloud Console**:
   - Navigate to `Global_LearningResources` class
   - Find the resource with title "Introduction to AI Ethics"
   - Confirm:
     - ✓ Only ONE entry exists
     - ✓ `categories_json` contains: `{"primary":"AI Ethics","secondary":["Responsible AI","AI Governance"]}`
     - ✓ `target_audience_json` contains: `{"expertise_level":"intermediate","job_roles":["Data Scientist","AI Engineer","Product Manager"]}`
     - ✓ `content_json` contains: `{"summary":"...","full_text":"...","video_transcript":null,"video_url":null,"image_analysis":[...]}`
     - ✗ NO separate `primary_category`, `secondary_categories`, `expertise_level`, `job_roles`, `summary`, `full_text` fields

## Files Modified

1. **[`src/data_stores/weaviate_client.py`](src/data_stores/weaviate_client.py:235)** 
   - Updated [`_create_global_learning_resources_class()`](src/data_stores/weaviate_client.py:235) - Changed schema to use JSON fields
   - Updated [`add_learning_resource()`](src/data_stores/weaviate_client.py:1452) - Store nested structures as JSON
   - Updated [`query_documents()`](src/data_stores/weaviate_client.py:974) - Parse JSON back to objects on retrieval

## Important Notes

### Schema Recreation Required

**IMPORTANT**: Since we changed the Weaviate schema, you need to either:

1. **Option A (Recommended) - Delete and recreate the class**:
   ```python
   # In Weaviate Cloud Console or via API:
   # 1. Delete the Global_LearningResources class
   # 2. Restart your application (it will recreate with new schema)
   ```

2. **Option B - Migrate existing data**:
   - Write a migration script to read existing data
   - Transform it to JSON format
   - Re-insert with new schema

### Why JSON Strings?

Weaviate (v3) doesn't support true nested objects. The options are:
1. **Flatten everything** (what was happening before - incorrect)
2. **Store as JSON strings** (current approach - maintains exact structure)

JSON strings allow us to:
- ✓ Preserve the exact payload structure
- ✓ Handle null values correctly
- ✓ Prevent duplication
- ✓ Maintain nested relationships

### Search Functionality

Weaviate can still perform semantic search on:
- The vector embedding (generated from all text content)
- Top-level arrays like `topics_discussed`, `useful_context`, `tags`
- Top-level strings like `title`, `description`, `resource_type`

The JSON fields are stored for structure preservation, while the embedding enables semantic search across all content.
