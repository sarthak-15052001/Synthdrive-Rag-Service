# Sample Payloads for RAG Planner API

## Sample Payload for AI Tools Query
```json
{
  "query": "What AI tools are available for video generation?",
  "organization_id": "org-123",
  "tenant_id": "default"
}
```

## Sample Payload for Ecosystem Partners Query
```json
{
  "query": "Find ecosystem partners with expertise in supply chain optimization",
  "organization_id": "org-123",
  "tenant_id": "default"
}
```

## Sample Payload for Learning Resources Query
```json
{
  "query": "I need learning resources about fine-tuning large language models",
  "organization_id": "org-123",
  "tenant_id": "default"
}
```

## Sample Payload for Tenant Files Query
```json
{
  "query": "Find our company's financial reports from 2023",
  "organization_id": "org-123",
  "tenant_id": "default"
}
```

## Sample Payload for Complex Query
```json
{
  "query": "What AI tools can help with video generation and which partners can implement them?",
  "organization_id": "org-123",
  "tenant_id": "default"
}
```

## Sample Payload for Relationship Query
```json
{
  "query": "How are our marketing campaigns related to customer acquisition?",
  "organization_id": "org-123",
  "tenant_id": "default"
}
```

## Sample Payload for Multi-Collection Query
```json
{
  "query": "Find learning resources about AI tools for data visualization",
  "organization_id": "org-123",
  "tenant_id": "default"
}
```

## Sample Payload for Specific Tool Query
```json
{
  "query": "Tell me about Midjourney and similar AI image generation tools",
  "organization_id": "org-123",
  "tenant_id": "default"
}
```

## Sample Payload for Specific Partner Query
```json
{
  "query": "Which ecosystem partners specialize in AI implementation for healthcare?",
  "organization_id": "org-123",
  "tenant_id": "default"
}
```

## Sample Payload for Specific Document Query
```json
{
  "query": "Find the Q4 financial report from our finance department",
  "organization_id": "org-123",
  "tenant_id": "default"
}
```

## Expected Response Format
```json
{
  "original_query": "What AI tools are available for video generation?",
  "organization_id": "org-123",
  "plan": "Search Global_Tools in Weaviate for AI tools related to video generation, then use Neo4j to explore related technologies and user reviews.",
  "collections_to_search": ["Global_Tools"],
  "retrieved_docs": [
    {
      "content": "RunwayML: A powerful AI video generation tool that allows users to create and edit videos using machine learning.",
      "metadata": {
        "tool_id": "tool-1",
        "name": "RunwayML",
        "url": "https://runwayml.com",
        "category": "Video Generation"
      },
      "source": "Global_Tools",
      "relevance_score": 0.92,
      "citation_id": "global-tool-1"
    },
    {
      "content": "Synthesia: AI video generation platform that creates videos with virtual avatars from text.",
      "metadata": {
        "tool_id": "tool-2",
        "name": "Synthesia",
        "url": "https://synthesia.io",
        "category": "Video Generation"
      },
      "source": "Global_Tools",
      "relevance_score": 0.89,
      "citation_id": "global-tool-2"
    }
  ],
  "graph_insights": [
    {
      "content": "RunwayML is used by Creative Agencies",
      "metadata": {
        "source_node": {"name": "RunwayML", "type": "Tool"},
        "relationship_type": "USED_BY",
        "target_node": {"name": "Creative Agencies", "type": "UserGroup"}
      },
      "source": "Neo4j",
      "relevance_score": 0.8,
      "citation_id": "graph-insight-1"
    }
  ],
  "final_answer": "There are several AI tools available for video generation. RunwayML is a powerful option that allows users to create and edit videos using machine learning. It's particularly popular among creative agencies. Synthesia is another platform that specializes in creating videos with virtual avatars from text input. Both tools offer different approaches to AI video generation depending on your specific needs.",
  "error_log": []
}