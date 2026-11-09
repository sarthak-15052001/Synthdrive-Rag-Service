#!/bin/bash

# Test the global ecosystem partner ingestion API endpoint using curl
echo "Testing global ecosystem partner ingestion API endpoint..."

# Create a JSON payload file
cat > ecosystem_partner_payload.json << EOF
{
  "name": "TechSolutions Inc.",
  "bio": "TechSolutions is a leading technology consulting firm specializing in AI integration, cloud migration, and digital transformation services for enterprise clients.",
  "expertise": ["AI Integration", "Cloud Migration", "Digital Transformation", "Enterprise Solutions"],
  "certifications": ["AWS Certified Solutions Architect", "Google Cloud Professional", "Microsoft Azure Expert"],
  "case_studies": "Successfully implemented AI-driven analytics platform for Fortune 500 retail client, resulting in 35% increase in operational efficiency and $2.5M annual cost savings.",
  "website": "https://techsolutions-example.com",
  "contact_info": "partners@techsolutions-example.com",
  "budget_tier": "Enterprise",
  "tags": ["AI", "Cloud", "Enterprise", "Digital Transformation"],
  "tenant_id": "default"
}
EOF

# Execute the curl command
curl -X POST \
  -H "Content-Type: application/json" \
  -d @ecosystem_partner_payload.json \
  http://localhost:8000/api/v1/rag/ingest/global/ecosystem-partner | jq .

echo "Test completed!"