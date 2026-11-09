# Ecosystem Partners Search API Guide

This guide provides information about the `/api/v1/rag/ecosystem-partners/search` API endpoint and how to use it to search for ecosystem partners using natural language queries.

## API Endpoint

```
POST /api/v1/rag/ecosystem-partners/search
```

This endpoint accepts a query string and optional filters, processes it through the Weaviate client, and returns a list of relevant ecosystem partners.

## Request Payload

```json
{
  "tenant_id": "default",
  "query": "string",
  "filters": {
    "additionalProp1": {}
  },
  "limit": 5
}
```

### Parameters

- `tenant_id` (string, required): The tenant ID to use for the search. Default is "default".
- `query` (string, required): The natural language query to search for ecosystem partners. Example: "supply chain experts".
- `filters` (object, optional): Additional filters to apply to the search. Can include properties like:
  - `budget_tier`: Filter by budget tier (e.g., "enterprise", "mid-market", "growth")
  - Other properties defined in the `Global_Ecosystem` class schema
- `limit` (integer, optional): Maximum number of results to return. Default is 5.

## Response Format

```json
{
  "query": "string",
  "partners": [
    {
      "partner_id": "string",
      "name": "string",
      "bio": "string",
      "expertise": ["string"],
      "certifications": ["string"],
      "case_studies": "string",
      "website": "string",
      "contact_info": "string",
      "budget_tier": "string",
      "tags": ["string"],
      "relevance_score": 0.0,
      "citation_id": "string"
    }
  ]
}
```

### Response Fields

- `query` (string): The original query string.
- `partners` (array): List of ecosystem partners matching the query.
  - `partner_id` (string): Unique identifier for the partner.
  - `name` (string): Name of the ecosystem partner.
  - `bio` (string): Biography or description of the partner.
  - `expertise` (array of strings): Areas of expertise.
  - `certifications` (array of strings): Certifications held by the partner.
  - `case_studies` (string): Case studies or success stories.
  - `website` (string): Partner's website URL.
  - `contact_info` (string): Contact information.
  - `budget_tier` (string): Budget tier (enterprise, mid-market, etc.).
  - `tags` (array of strings): Tags associated with the partner.
  - `relevance_score` (number): Score indicating relevance to the query (0.0 to 1.0).
  - `citation_id` (string): ID used for citations in responses.

## Example Usage

### Python Example

```python
import requests

url = "http://localhost:8000/api/v1/rag/ecosystem-partners/search"
headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer your_token_here"
}
payload = {
    "tenant_id": "default",
    "query": "supply chain experts",
    "filters": {},
    "limit": 5
}

response = requests.post(url, headers=headers, json=payload)
result = response.json()
print(result)
```

### cURL Example

```bash
curl -X POST "http://localhost:8000/api/v1/rag/ecosystem-partners/search" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your_token_here" \
  -d '{
    "tenant_id": "default",
    "query": "supply chain experts",
    "filters": {},
    "limit": 5
  }'
```

## Testing Scripts

This repository includes several scripts to test and demonstrate the ecosystem partners search API:

1. `test_ecosystem_partners_search.py` - A simple Python script to test the search API
2. `test_ecosystem_partners_search.sh` - A bash script using curl to test the search API
3. `ecosystem_partners_workflow.py` - A comprehensive Python script that demonstrates adding a partner and then searching for it
4. `ecosystem_partners_sample_response.json` - A sample response showing what the API returns

### Running the Python Test Script

```bash
python test_ecosystem_partners_search.py
```

### Running the Bash Test Script

```bash
chmod +x test_ecosystem_partners_search.sh
./test_ecosystem_partners_search.sh
```

### Running the Workflow Script

```bash
# Add a partner and then search
python ecosystem_partners_workflow.py

# Skip adding a partner, just search
python ecosystem_partners_workflow.py --skip-add

# Search with a custom query
python ecosystem_partners_workflow.py "logistics experts"
```

## Implementation Details

The API endpoint uses Weaviate's vector search capabilities to find semantically relevant ecosystem partners based on the natural language query. The search is performed on the `Global_Ecosystem` class in Weaviate, which stores partner information including expertise, bio, certifications, and other details.

The search process:

1. Expands the query with context (e.g., "Expert in supply chain experts")
2. Creates an embedding vector for the query using OpenAI's embedding model
3. Performs a vector similarity search in Weaviate
4. Applies any additional filters specified in the request
5. Returns the most relevant partners, sorted by relevance score

For more details, see the implementation in `src/api/v1/endpoints/query.py` and `src/data_stores/weaviate_client.py`.