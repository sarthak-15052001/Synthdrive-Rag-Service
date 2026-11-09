# Conditional Edge Router API Test Results

This document contains the results of testing the Conditional Edge Router API using both curl and Python scripts.

## API Endpoint

```
/api/v1/rag/conditional-edge-router
```

## Test Scenarios

We've tested the following scenarios:

1. **Empty state** - No plan, no retrieved docs, no errors
2. **State with plan but no retrieved docs** - Has a plan but no documents retrieved yet
3. **State with plan and retrieved docs** - Has a plan and documents retrieved
4. **State with error** - Has an error in the error_log
5. **Custom query with different organization and tenant** - Using different organization and tenant IDs

## Expected Behavior

The Conditional Edge Router should route to different nodes based on the current state:

- If there's no plan, it should route to the planner
- If there's a plan but no retrieved docs, it should route to retrieval
- If there's a plan and retrieved docs, it should route to synthesis
- If there's an error, it should route to error handling

## Test Results

### Test Case 1: Empty state

**Request:**
```json
{
  "original_query": "What AI tools are available for video generation?",
  "organization_id": "test_org",
  "tenant_id": "test_tenant",
  "plan": null,
  "retrieved_docs": [],
  "graph_insights": [],
  "final_answer": null,
  "error_log": []
}
```

**Expected Response:**
```json
{
  "next_node": "planner",
  "reason": "No plan exists yet, routing to planner to create a plan",
  "updated_state": {
    "original_query": "What AI tools are available for video generation?",
    "organization_id": "test_org",
    "tenant_id": "test_tenant",
    "plan": null,
    "retrieved_docs": [],
    "graph_insights": [],
    "final_answer": null,
    "error_log": []
  }
}
```

**Actual Response:**
[To be filled after running the tests]

### Test Case 2: State with plan but no retrieved docs

**Request:**
```json
{
  "original_query": "What AI tools are available for video generation?",
  "organization_id": "test_org",
  "tenant_id": "test_tenant",
  "plan": "First search for AI tools in Weaviate, then query Neo4j for relationships between the found tools.",
  "retrieved_docs": [],
  "graph_insights": [],
  "final_answer": null,
  "error_log": []
}
```

**Expected Response:**
```json
{
  "next_node": "retrieval",
  "reason": "Plan exists but no documents have been retrieved yet, routing to retrieval",
  "updated_state": {
    "original_query": "What AI tools are available for video generation?",
    "organization_id": "test_org",
    "tenant_id": "test_tenant",
    "plan": "First search for AI tools in Weaviate, then query Neo4j for relationships between the found tools.",
    "retrieved_docs": [],
    "graph_insights": [],
    "final_answer": null,
    "error_log": []
  }
}
```

**Actual Response:**
[To be filled after running the tests]

### Test Case 3: State with plan and retrieved docs

**Request:**
```json
{
  "original_query": "What AI tools are available for video generation?",
  "organization_id": "test_org",
  "tenant_id": "test_tenant",
  "plan": "First search for AI tools in Weaviate, then query Neo4j for relationships between the found tools.",
  "retrieved_docs": [
    {
      "content": "Runway ML is an AI tool for video generation. It allows users to create videos from text prompts.",
      "source": "weaviate",
      "citation_id": "doc-1"
    },
    {
      "content": "Synthesia is an AI video generation platform that creates videos with virtual avatars.",
      "source": "weaviate",
      "citation_id": "doc-2"
    },
    {
      "content": "Descript offers AI-powered video editing tools including text-based editing and overdub features.",
      "source": "weaviate",
      "citation_id": "doc-3"
    }
  ],
  "graph_insights": [
    {
      "content": "Runway ML and Synthesia are both used in the creative industry for video production.",
      "source": "graph_database",
      "citation_id": "graph-1"
    }
  ],
  "final_answer": null,
  "error_log": []
}
```

**Expected Response:**
```json
{
  "next_node": "synthesizer",
  "reason": "Plan and documents exist, routing to synthesizer to generate the final answer",
  "updated_state": {
    "original_query": "What AI tools are available for video generation?",
    "organization_id": "test_org",
    "tenant_id": "test_tenant",
    "plan": "First search for AI tools in Weaviate, then query Neo4j for relationships between the found tools.",
    "retrieved_docs": [
      {
        "content": "Runway ML is an AI tool for video generation. It allows users to create videos from text prompts.",
        "source": "weaviate",
        "citation_id": "doc-1"
      },
      {
        "content": "Synthesia is an AI video generation platform that creates videos with virtual avatars.",
        "source": "weaviate",
        "citation_id": "doc-2"
      },
      {
        "content": "Descript offers AI-powered video editing tools including text-based editing and overdub features.",
        "source": "weaviate",
        "citation_id": "doc-3"
      }
    ],
    "graph_insights": [
      {
        "content": "Runway ML and Synthesia are both used in the creative industry for video production.",
        "source": "graph_database",
        "citation_id": "graph-1"
      }
    ],
    "final_answer": null,
    "error_log": []
  }
}
```

**Actual Response:**
[To be filled after running the tests]

### Test Case 4: State with error

**Request:**
```json
{
  "original_query": "What AI tools are available for video generation?",
  "organization_id": "test_org",
  "tenant_id": "test_tenant",
  "plan": "First search for AI tools in Weaviate, then query Neo4j for relationships between the found tools.",
  "retrieved_docs": [],
  "graph_insights": [],
  "final_answer": null,
  "error_log": ["Error connecting to Weaviate: Connection refused"]
}
```

**Expected Response:**
```json
{
  "next_node": "error_handler",
  "reason": "Errors detected in the error log, routing to error handler",
  "updated_state": {
    "original_query": "What AI tools are available for video generation?",
    "organization_id": "test_org",
    "tenant_id": "test_tenant",
    "plan": "First search for AI tools in Weaviate, then query Neo4j for relationships between the found tools.",
    "retrieved_docs": [],
    "graph_insights": [],
    "final_answer": null,
    "error_log": ["Error connecting to Weaviate: Connection refused"]
  }
}
```

**Actual Response:**
[To be filled after running the tests]

### Test Case 5: Custom query with different organization and tenant

**Request:**
```json
{
  "original_query": "What are the best AI tools for natural language processing?",
  "organization_id": "custom_org",
  "tenant_id": "custom_tenant",
  "plan": null,
  "retrieved_docs": [],
  "graph_insights": [],
  "final_answer": null,
  "error_log": []
}
```

**Expected Response:**
```json
{
  "next_node": "planner",
  "reason": "No plan exists yet, routing to planner to create a plan",
  "updated_state": {
    "original_query": "What are the best AI tools for natural language processing?",
    "organization_id": "custom_org",
    "tenant_id": "custom_tenant",
    "plan": null,
    "retrieved_docs": [],
    "graph_insights": [],
    "final_answer": null,
    "error_log": []
  }
}
```

**Actual Response:**
[To be filled after running the tests]

## Running the Tests

### Using curl

```bash
chmod +x test_conditional_edge_router_curl.sh
./test_conditional_edge_router_curl.sh
```

### Using Python

```bash
# Install required packages
pip install requests colorama

# Run the test script
python test_conditional_edge_router_python_enhanced.py --save-results
```

## Conclusion

[To be filled after running the tests]