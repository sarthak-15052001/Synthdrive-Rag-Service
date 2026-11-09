import asyncio
from src.data_stores.neo4j_client import Neo4jClient

async def create_test_data():
    # Initialize Neo4j client
    neo4j_client = Neo4jClient()
    
    # Create test data
    with neo4j_client.driver.session() as session:
        # Create Team nodes
        session.run("""
            CREATE (t:Team {id: 'team-1', name: 'marketing', description: 'Marketing team', tenant_id: 'test_org'})
            CREATE (t2:Team {id: 'team-2', name: 'sales', description: 'Sales team', tenant_id: 'test_org'})
        """)
        
        # Create User nodes
        session.run("""
            CREATE (u:User {id: 'user-1', name: 'John Doe', email: 'john@example.com', tenant_id: 'test_org'})
            CREATE (u2:User {id: 'user-2', name: 'Jane Smith', email: 'jane@example.com', tenant_id: 'test_org'})
        """)
        
        # Create Workflow nodes
        session.run("""
            CREATE (w:Workflow {id: 'workflow-1', name: 'marketing automation', 
                    description: 'Marketing automation workflow', created_by: 'user-1', tenant_id: 'test_org'})
            CREATE (w2:Workflow {id: 'workflow-2', name: 'customer onboarding', 
                    description: 'Customer onboarding workflow', created_by: 'user-2', tenant_id: 'test_org'})
        """)
        
        # Create relationships
        session.run("""
            MATCH (u:User {id: 'user-1', tenant_id: 'test_org'})
            MATCH (t:Team {id: 'team-1', tenant_id: 'test_org'})
            CREATE (u)-[:BELONGS_TO]->(t)
        """)
        
        session.run("""
            MATCH (u:User {id: 'user-2', tenant_id: 'test_org'})
            MATCH (t:Team {id: 'team-2', tenant_id: 'test_org'})
            CREATE (u)-[:BELONGS_TO]->(t)
        """)
        
        session.run("""
            MATCH (w:Workflow {id: 'workflow-1', tenant_id: 'test_org'})
            MATCH (u:User {id: 'user-1', tenant_id: 'test_org'})
            CREATE (w)-[:CREATED_BY]->(u)
        """)
        
        session.run("""
            MATCH (w:Workflow {id: 'workflow-2', tenant_id: 'test_org'})
            MATCH (u:User {id: 'user-2', tenant_id: 'test_org'})
            CREATE (w)-[:CREATED_BY]->(u)
        """)
        
        session.run("""
            MATCH (t:Team {id: 'team-1', tenant_id: 'test_org'})
            MATCH (w:Workflow {id: 'workflow-1', tenant_id: 'test_org'})
            CREATE (t)-[:USES]->(w)
        """)
        
        session.run("""
            MATCH (t:Team {id: 'team-2', tenant_id: 'test_org'})
            MATCH (w:Workflow {id: 'workflow-2', tenant_id: 'test_org'})
            CREATE (t)-[:USES]->(w)
        """)
    
    print("Test data created successfully!")

if __name__ == "__main__":
    asyncio.run(create_test_data())