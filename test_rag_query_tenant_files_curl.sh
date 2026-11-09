#!/bin/bash

# Test the RAG query API endpoint using curl with tenant file filters
echo "Testing RAG query API endpoint with tenant file filters..."

# Create a directory for test payloads if it doesn't exist
mkdir -p tenant_file_payloads

# Base URL for the API
API_URL="http://localhost:8000/api/v1/rag/query"
AUTH_HEADER="Authorization: Bearer test-token"
CONTENT_TYPE="Content-Type: application/json"

# Test 1: Query for business strategy documents
echo "==================================================================="
echo "TEST 1: Query for business strategy documents"
echo "==================================================================="

cat > tenant_file_payloads/business_strategy_query.json << EOF
{
  "query_str": "What are the key business objectives for 2023?",
  "tenant_id": "default",
  "filters": {
    "tags": ["business", "strategy"],
    "organization_id": "test_org_123"
  },
  "top_k": 5
}
EOF

echo "Sending query: What are the key business objectives for 2023?"
curl -X POST \
  -H "$CONTENT_TYPE" \
  -H "$AUTH_HEADER" \
  -d @tenant_file_payloads/business_strategy_query.json \
  --no-buffer \
  $API_URL

echo -e "\n==================================================================="

# Test 2: Query for financial performance insights
echo "TEST 2: Query for financial performance insights"
echo "==================================================================="

cat > tenant_file_payloads/financial_performance_query.json << EOF
{
  "query_str": "Summarize the financial growth and revenue trends in 2023.",
  "tenant_id": "default",
  "filters": {
    "file_type": "pdf",
    "tags": ["financial", "2023"]
  },
  "top_k": 5
}
EOF

echo "Sending query: Summarize the financial growth and revenue trends in 2023."
curl -X POST \
  -H "$CONTENT_TYPE" \
  -H "$AUTH_HEADER" \
  -d @tenant_file_payloads/financial_performance_query.json \
  --no-buffer \
  $API_URL

echo -e "\n==================================================================="

# Test 3: Query for marketing strategy details
echo "TEST 3: Query for marketing strategy details"
echo "==================================================================="

cat > tenant_file_payloads/marketing_strategy_query.json << EOF
{
  "query_str": "Explain the digital marketing focus areas for 2023.",
  "tenant_id": "default",
  "filters": {
    "file_path": "/marketing/strategy/2023.docx",
    "tags": ["marketing", "strategy"]
  },
  "top_k": 5
}
EOF

echo "Sending query: Explain the digital marketing focus areas for 2023."
curl -X POST \
  -H "$CONTENT_TYPE" \
  -H "$AUTH_HEADER" \
  -d @tenant_file_payloads/marketing_strategy_query.json \
  --no-buffer \
  $API_URL

echo -e "\n==================================================================="

# Test 4: Query for product roadmap updates
echo "TEST 4: Query for product roadmap updates"
echo "==================================================================="

cat > tenant_file_payloads/product_roadmap_query.json << EOF
{
  "query_str": "What are the upcoming product launches planned for 2023-2024?",
  "tenant_id": "default",
  "filters": {
    "tags": ["product", "roadmap"],
    "organization_id": "test_org_123"
  },
  "top_k": 5
}
EOF

echo "Sending query: What are the upcoming product launches planned for 2023-2024?"
curl -X POST \
  -H "$CONTENT_TYPE" \
  -H "$AUTH_HEADER" \
  -d @tenant_file_payloads/product_roadmap_query.json \
  --no-buffer \
  $API_URL

echo -e "\n==================================================================="

# Test 5: Query for annual company performance summary
echo "TEST 5: Query for annual company performance summary"
echo "==================================================================="

cat > tenant_file_payloads/annual_report_query.json << EOF
{
  "query_str": "Give an overview of the 2023 annual report highlights.",
  "tenant_id": "default",
  "filters": {
    "file_name": "Annual Report 2023.pdf",
    "tags": ["annual", "report"]
  },
  "top_k": 5
}
EOF

echo "Sending query: Give an overview of the 2023 annual report highlights."
curl -X POST \
  -H "$CONTENT_TYPE" \
  -H "$AUTH_HEADER" \
  -d @tenant_file_payloads/annual_report_query.json \
  --no-buffer \
  $API_URL

echo -e "\n==================================================================="
echo "Test completed at $(date)"

# Save the test payloads for reference
echo "Test payloads saved in the tenant_file_payloads directory"