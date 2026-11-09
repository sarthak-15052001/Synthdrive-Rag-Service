# No-Code Templates Connector Guide

## Overview

The No-Code Templates Connector enables the SynthDrive RAG service to send no-code template data to an external service running on another PC. This connector mirrors the architecture used for Global Learning Resources and Global Tools connectors.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  SynthDrive RAG Service                     │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  POST /api/v1/rag/ingest/no-code-templates           │  │
│  │  (no_code_templates.py)                              │  │
│  └──────────────────┬───────────────────────────────────┘  │
│                     │                                       │
│                     ▼                                       │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  NoCodeTemplatesClient                                │  │
│  │  (global_tools_client.py)                            │  │
│  │                                                       │  │
│  │  • Logs ingestion process to terminal                │  │
│  │  • Serializes template data                          │  │
│  │  • Sends HTTP POST via httpx                         │  │
│  └──────────────────┬───────────────────────────────────┘  │
│                     │                                       │
└─────────────────────┼───────────────────────────────────────┘
                      │
                      │ HTTP POST
                      │ (with logs)
                      ▼
┌─────────────────────────────────────────────────────────────┐
│           External Service (Another PC)                     │
│           http://192.168.0.98:8000                          │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  POST /api/no-code-templates                         │  │
│  │                                                       │  │
│  │  Receives and processes template data                │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Implementation Details

### 1. Connector Client (`NoCodeTemplatesClient`)

**Location:** `src/data_stores/global_tools_client.py`

**Features:**
- **Terminal Logging:** All operations are logged to the terminal with clear markers
- **Error Handling:** Comprehensive error handling for HTTP, network, and validation errors
- **Data Serialization:** Automatically serializes Pydantic models and special types (URLs, dates)
- **Async Support:** Fully async operations using httpx

**Key Methods:**
- `post_no_code_template(template: NoCodeTemplate) -> dict`

### 2. API Endpoint Integration

**Location:** `src/api/v1/endpoints/no_code_templates.py`

The endpoint `/api/v1/rag/ingest/no-code-templates` now:
1. Validates the incoming template data
2. Sends data to external service via connector (with logs)
3. Processes locally if external service call succeeds
4. Returns job ID for tracking

### 3. Data Models

**Location:** `src/data_stores/global_tools_client.py`

```python
class NoCodeTemplateCategory(BaseModel):
    primary: str
    secondary: List[str]

class NoCodeTemplate(BaseModel):
    name: str
    source_url: HttpUrl
    platform: str
    use_cases: List[str]
    short_description: str
    complexity: str
    categories: NoCodeTemplateCategory
    tags: List[str] = []
    detailed_description: Optional[str] = None
    prerequisites: List[str] = []
    estimated_time: Optional[str] = None
```

## Configuration

### External Service URL

The connector is configured to send data to:
```
http://192.168.0.98:8000/api/no-code-templates
```

To change the base URL, modify the initialization in `NoCodeTemplatesClient`:
```python
class NoCodeTemplatesClient:
    def __init__(self, base_url: str = "http://192.168.0.98:8000"):
        self.base_url = base_url
        self.endpoint = f"{self.base_url}/api/no-code-templates"
```

## Terminal Logs

The connector provides detailed terminal logging at each stage:

### Success Flow:
```
==================================================
NO-CODE TEMPLATES CONNECTOR - Starting Template Ingestion
==================================================
Template Name: Customer Onboarding Workflow
Endpoint: http://192.168.0.98:8000/api/no-code-templates
Sending request to no-code templates service...
==================================================
NO-CODE TEMPLATES CONNECTOR - Template Successfully Added
==================================================
Template 'Customer Onboarding Workflow' successfully stored in global service
```

### Error Flow:
```
==================================================
NO-CODE TEMPLATES CONNECTOR - Template Ingestion Failed - HTTP Error
==================================================
Status Code: 503
Response Text: Service Unavailable
Request URL: http://192.168.0.98:8000/api/no-code-templates
```

## Usage Examples

### 1. Using the API Endpoint

```bash
curl -X POST "http://localhost:8000/api/v1/rag/ingest/no-code-templates" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "name": "Customer Onboarding Workflow",
    "source_url": "https://templates.example.com/customer-onboarding",
    "platform": "Zapier",
    "use_cases": [
      "Automate customer onboarding process",
      "Send welcome emails",
      "Create customer records in CRM"
    ],
    "short_description": "Streamline your customer onboarding with automated workflows",
    "complexity": "Intermediate",
    "categories": {
      "primary": "Business Automation",
      "secondary": ["CRM Integration", "Email Automation"]
    },
    "tags": ["automation", "onboarding", "crm"],
    "detailed_description": "This comprehensive template automates the entire customer onboarding process.",
    "prerequisites": [
      "Active Zapier account",
      "Connected CRM system"
    ],
    "estimated_time": "30-45 minutes"
  }'
```

### 2. Using the Connector Directly

```python
import asyncio
from src.data_stores.global_tools_client import (
    NoCodeTemplatesClient, 
    NoCodeTemplate, 
    NoCodeTemplateCategory
)

async def send_template():
    # Create template
    template = NoCodeTemplate(
        name="Customer Onboarding Workflow",
        source_url="https://templates.example.com/customer-onboarding",
        platform="Zapier",
        use_cases=["Automate customer onboarding process"],
        short_description="Streamline your customer onboarding",
        complexity="Intermediate",
        categories=NoCodeTemplateCategory(
            primary="Business Automation",
            secondary=["CRM Integration"]
        ),
        tags=["automation", "onboarding"]
    )
    
    # Send to external service
    client = NoCodeTemplatesClient()
    result = await client.post_no_code_template(template)
    print(f"Result: {result}")

asyncio.run(send_template())
```

### 3. Running the Test Script

```bash
python test_no_code_templates_connector.py
```

## Error Handling

The connector handles various error scenarios:

1. **HTTP Errors (4xx, 5xx):** Logs status code and response text
2. **Network Errors:** Logs connection issues and timeouts
3. **Validation Errors:** Logs data validation failures
4. **Unexpected Errors:** Logs full error details with context

## Monitoring

All connector operations are logged to the console with timestamps and severity levels:

- `INFO`: Normal operations and successful completions
- `DEBUG`: Detailed data information (requires debug logging level)
- `ERROR`: All error conditions with context

## Comparison with Similar Connectors

### Global Learning Resources Connector
- Endpoint: `/api/global-learning-resources`
- Similar architecture and logging
- Handles learning resource data

### Global Tools Connector
- Endpoint: `/api/global-tools`
- Similar architecture and logging
- Handles AI tool data

### No-Code Templates Connector (New)
- Endpoint: `/api/no-code-templates`
- **Same architecture and logging pattern**
- Handles no-code template data

## Troubleshooting

### Issue: Connection Refused
**Solution:** Verify the external service is running at `http://192.168.0.98:8000`

### Issue: Timeout
**Solution:** Check network connectivity between the two PCs

### Issue: 404 Not Found
**Solution:** Verify the endpoint `/api/no-code-templates` exists on the external service

### Issue: Validation Error
**Solution:** Check that all required fields are present and properly formatted

## Testing

See `test_no_code_templates_connector.py` for a complete test example that:
- Creates a sample no-code template
- Sends it to the external service
- Logs all operations to terminal
- Reports success or failure

## Files Modified/Created

1. **Modified:** `src/data_stores/global_tools_client.py`
   - Added `NoCodeTemplateCategory` model
   - Added `NoCodeTemplate` model  
   - Added `NoCodeTemplatesClient` class

2. **Modified:** `src/api/v1/endpoints/no_code_templates.py`
   - Integrated connector into ingestion endpoint
   - Added error handling for external service calls

3. **Created:** `test_no_code_templates_connector.py`
   - Test script for connector functionality

4. **Created:** `no_code_templates_connector_guide.md`
   - This documentation file
