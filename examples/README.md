# Ingestion Examples - Quick Start

## 🚀 How to Run

### Step 1: Configure Environment

Ensure you have a `.env` file in the project root with these **required** settings:

```bash
# Required for ingestion
OPENAI_API_KEY=sk-your-key-here
WEAVIATE_URL=https://your-instance.weaviate.network
WEAVIATE_API_KEY=your-key-here
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your-password
```

**Note:** PostgreSQL is **NOT required** for ingestion examples!

### Step 2: Start Neo4j

```bash
# Option 1: Using Docker
docker run -d \
  --name neo4j \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/your-password \
  neo4j:latest

# Option 2: Using docker-compose
docker-compose up -d neo4j
```

### Step 3: Run Examples

```bash
# Activate virtual environment
source venv/bin/activate

# Run the examples
python examples/ingestion_example.py
```

## 📋 What the Examples Demonstrate

### Example 1: Text Content Ingestion (Sync)
- Direct text content ingestion
- Entity extraction (OpenAI, Microsoft, GPT-4)
- Synchronous processing

### Example 2: Async Ingestion with GraphRAG
- Business document processing
- Async parallel writes
- GraphRAG knowledge graph construction
- Entity relationships (partnerships, people, locations)

### Example 3: Multi-Tenant Data Isolation
- Multiple tenants (Company A, B, C)
- Data isolation demonstration
- Parallel ingestion

### Example 4: File Ingestion
- File-based ingestion
- Auto-creates test file if needed
- Demonstrates file parsing

## ✅ Expected Output

```
🚀 Starting Ingestion Pipeline Examples
==================================================
Example 1: Text Content Ingestion (Sync)
==================================================
⚠️ PostgreSQL not available (not required for ingestion): ...
✅ Ingestion successful!
   Status: success
   Message: Document ingested successfully
   Destinations: ['weaviate', 'neo4j']

==================================================
Example 2: Async Ingestion with GraphRAG
==================================================
📊 GraphRAG client initialized successfully
✅ Async ingestion successful!
   Status: success
   Message: Document ingested successfully
   Destinations: ['weaviate', 'neo4j']
   GraphRAG: Enabled

==================================================
Example 3: Multi-Tenant Data Isolation
==================================================
✅ Ingested document for tenant_a
✅ Ingested document for tenant_b
✅ Ingested document for tenant_c

📊 Multi-Tenant Ingestion Summary:
   tenant_a: success -> ['weaviate']
   tenant_b: success -> ['weaviate']
   tenant_c: success -> ['weaviate']

🔒 Data isolation ensures each tenant's data is separate and secure

==================================================
Example 4: File Ingestion
==================================================
✅ Created test file: tests/ingestion/test_data.txt
✅ File ingestion successful!
   File: test_data.txt
   Status: success
   Destinations: ['weaviate', 'neo4j']

==================================================
✅ All examples completed successfully!
==================================================
```

## ⚠️ Troubleshooting

### "PostgreSQL connection error"
**This is normal!** PostgreSQL is not required for ingestion. The examples will show a warning and continue.

### "Weaviate connection error"
- Check `WEAVIATE_URL` and `WEAVIATE_API_KEY` in `.env`
- Verify Weaviate instance is accessible

### "Neo4j connection error"
- Ensure Neo4j is running: `docker ps | grep neo4j`
- Check credentials in `.env`
- Verify port 7687 is accessible

### "OpenAI API error"
- Verify `OPENAI_API_KEY` in `.env`
- Check API key at https://platform.openai.com/api-keys
- Ensure you have credits

## 📊 Verify Data Was Ingested

### Check Weaviate

```python
from src.data_stores.weaviate_client import WeaviateClient

client = WeaviateClient()
result = client.client.query.aggregate("Document") \
    .with_meta_count() \
    .do()

print(f"Total documents: {result['data']['Aggregate']['Document'][0]['meta']['count']}")
```

### Check Neo4j

Access Neo4j Browser at http://localhost:7474 and run:

```cypher
// Count all entities
MATCH (e:Entity)
RETURN count(e) as total_entities

// View entity relationships
MATCH (e1:Entity)-[r]->(e2:Entity)
RETURN e1.name, type(r), e2.name
LIMIT 10
```

## 🔧 Customization

### Modify Content

Edit the content in [`ingestion_example.py`](ingestion_example.py):

```python
content = """
Your custom document content here...
Mention entities like Apple Inc., Google, etc.
"""
```

### Change Tenant ID

```python
result = graph.ingest_document(
    input_data=input_data,
    tenant_id="your_custom_tenant"  # Change this
)
```

### Add Your Own Example

```python
def my_custom_example():
    weaviate = WeaviateClient()
    neo4j = Neo4jClient()
    
    graph = IngestionGraph(
        postgres_client=None,  # Not required
        weaviate_client=weaviate,
        neo4j_client=neo4j
    )
    
    result = graph.ingest_document(
        input_data={
            "content": "Your content...",
            "metadata": {"source": "custom"}
        },
        tenant_id="my_tenant"
    )
    
    print(result)
    
    weaviate.close()
    neo4j.close()

# Add to main()
my_custom_example()
```

## 📚 Documentation

- **[Setup Guide](../INGESTION_SETUP_GUIDE.md)** - Complete setup instructions
- **[Implementation Summary](../INGESTION_IMPLEMENTATION_SUMMARY.md)** - Technical details
- **[Ingestion README](../src/ingestion/README.md)** - Pipeline documentation

## 🎯 Next Steps

1. Run the examples: `python examples/ingestion_example.py`
2. Verify data in Weaviate and Neo4j
3. Customize for your use case
4. Integrate into your application

## 💡 Tips

- **Start simple**: Run Example 1 first
- **Check logs**: Detailed logging helps debug issues
- **Use async**: Examples 2-4 show async patterns for better performance
- **Multi-tenancy**: Example 3 demonstrates data isolation