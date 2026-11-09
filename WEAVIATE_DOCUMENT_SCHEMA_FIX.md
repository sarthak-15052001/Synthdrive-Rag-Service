# Weaviate Document Schema Duplication Fix

## Problem Identified

The Weaviate `Document` collection had duplicate fields appearing in two places:

### Before Fix:
1. **Properties (top-level):**
   - `content` (text)
   - `metadata` (text/JSON string)
   - `source` (text) ❌ **DUPLICATE**
   - `created_at` (date) ❌ **DUPLICATE**
   - `tenant_id` (string) ❌ **DUPLICATE**

2. **Inside metadata JSON:**
   - `source` ❌ **DUPLICATE**
   - `created_at` ❌ **DUPLICATE**
   - `tenant_id` ❌ **DUPLICATE**
   - `author`
   - `document_type`
   - `tags`
   - `additional_metadata`
   - etc.

### Root Cause:
The [`upsert_vector()`](src/data_stores/weaviate_client.py:877) method was extracting `source`, `created_at`, and `tenant_id` from metadata and storing them **BOTH** as top-level properties **AND** inside the metadata JSON string, causing duplication visible in the Weaviate UI.

## Solution Implemented

### 1. Updated Document Schema
Modified [`_ensure_schema()`](src/data_stores/weaviate_client.py:769) to remove duplicate properties:

**New schema properties:**
- `content` (text) - The document content
- `metadata` (text/JSON) - **ALL** metadata as JSON string including source, created_at, etc.
- `tenant_id` (string) - Kept at top level for filtering purposes only

### 2. Updated Data Storage Logic
Modified [`upsert_vector()`](src/data_stores/weaviate_client.py:877) to:
- Extract `tenant_id` and store ONLY at top-level for filtering
- Remove `tenant_id` from metadata JSON to avoid duplication
- Store all other metadata fields (source, created_at, author, etc.) inside metadata JSON only

### 3. Updated Query Methods
Updated all query methods to work with the new schema:
- [`semantic_search()`](src/data_stores/weaviate_client.py:947)
- [`_query_with_vector()`](src/data_stores/weaviate_client.py:2052)
- [`_query_with_text()`](src/data_stores/weaviate_client.py:2081)
- [`_query_without_filters()`](src/data_stores/weaviate_client.py:2107)
- [`_process_query_results()`](src/data_stores/weaviate_client.py:2130)
- [`query_documents()`](src/data_stores/weaviate_client.py:1108)
- [`add_document()`](src/data_stores/weaviate_client.py:994)

### 4. Updated Filter Logic
Modified [`_build_where_filter()`](src/data_stores/weaviate_client.py:2162) to:
- Remove `source` filter (since it's now inside metadata JSON)
- Keep `tenant_id` filter (it's still at top-level)

## How to Apply the Fix

### Step 1: Recreate Document Collection
Run the provided script to recreate the Document collection:

```bash
python recreate_document_schema.py
```

**WARNING:** This will delete all existing documents in the Document collection. Make sure to backup your data first if needed.

### Step 2: Test with New Data
After recreating the schema, test by ingesting a new document:

```bash
curl -X POST "http://localhost:8000/api/v1/rag/ingest/document" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-token" \
  -d '{
    "tenant_id": "default",
    "content": "SynthDrive Inc. is working on a new AI project called Project Horizon...",
    "metadata": {
      "source": "company_report",
      "author": "John Smith",
      "created_at": "2026-01-02T14:00:00Z",
      "document_type": "internal_memo",
      "tags": ["AI", "project", "confidential"],
      "additional_metadata": {
        "priority": "high",
        "department": "R&D"
      }
    }
  }'
```

### Step 3: Verify in Weaviate UI
Check the Weaviate Cloud UI to verify:
1. `tenant_id` appears **once** in properties (not duplicated)
2. `source` appears **only** inside the `metadata` object (not at top level)
3. `created_at` appears **only** inside the `metadata` object (not at top level)

## Expected Result

### After Fix - Document Object Structure:
```
Document:
  uuid: "f952f785-4ad0-4d46-a02f-6bc6dc4d9870"
  properties:
    content: "SynthDrive Inc. is working on a new AI project..."
    metadata: {
      "source": "company_report",
      "author": "John Smith",
      "created_at": "2026-01-02T14:00:00Z",
      "document_type": "internal_memo",
      "tags": ["AI", "project", "confidential"],
      "additional_metadata": {
        "priority": "high",
        "department": "R&D"
      }
      // Note: tenant_id is NOT in metadata - it's only at top level
    }
    tenant_id: "default"    ✓ Only once at top level (NOT in metadata)
  vectors: [0.123, 0.456, ...]
```

## Benefits

1. **No more duplicates** - Each field appears only once
2. **Cleaner schema** - More organized and maintainable
3. **Better performance** - Less data redundancy
4. **Consistent structure** - Metadata is always in one place (JSON)
5. **Efficient filtering** - `tenant_id` still available at top-level for fast filtering

## Files Modified

1. [`src/data_stores/weaviate_client.py`](src/data_stores/weaviate_client.py) - Main fixes
   - Updated schema definition
   - Fixed data storage logic
   - Updated all query methods
   - Fixed filter building

## Additional Notes

- If you need to filter by `source` in the future, you'll need to:
  1. Parse the metadata JSON in post-processing, OR
  2. Add `source` back to the schema as a top-level property (but keep it in metadata too for completeness)

- The `tenant_id` is kept at top-level because it's used heavily for filtering queries and multi-tenancy support.

## Testing Checklist

- [ ] Run `recreate_document_schema.py` to recreate schema
- [ ] Ingest a test document using the API
- [ ] Verify in Weaviate UI that fields are not duplicated
- [ ] Test document search/retrieval
- [ ] Verify metadata is correctly parsed in query results
