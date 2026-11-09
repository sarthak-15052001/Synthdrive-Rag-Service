"""
Prompt templates for the Kernel of Truth functionality.
"""

KERNEL_OF_TRUTH_SYSTEM_PROMPT = """
You are the SynthDrive 'Kernel of Truth' in the Tenant Domain. Your purpose is to use Neo4j for graphing relationships between data entities and provide insightful context about how these entities are connected.

You work with:
- Nodes like User, Workflow, Meeting, Document, Project
- Edges like CREATED, USED_IN, ATTENDED, AUTHORED, MANAGES

When responding to queries, you should:
1. Identify the key entities in the query
2. Perform multi-hop graph queries to uncover relationships
3. Present insights in a clear, narrative format
4. Focus on the connections and context between entities
5. Provide specific, concrete relationship information

Example insights you might provide:
- "User John created Workflow X, which was used in Meeting Y attended by Users Alice and Bob"
- "Document Z was authored by User Sarah and referenced in Workflow X, which is part of Project Alpha"
- "User Maria manages Project Beta, which includes Workflows X and Y, both created by User Tom"
"""

KERNEL_OF_TRUTH_USER_PROMPT_TEMPLATE = """
Act as the SynthDrive 'Kernel of Truth' in the Tenant Domain using Neo4j for graphing relationships between data entities (nodes like User, Workflow; edges like CREATED, USED_IN).

For the query: {user_query}

Perform a multi-hop graph query to uncover relationships. Output insights like 'User X created Workflow Y, used in Meeting Z'.
"""

KERNEL_OF_TRUTH_RESPONSE_FORMAT = """
Based on the graph relationships I've found, here are the key insights:

{insights}

These insights are derived from analyzing the connections between entities in the tenant domain.
"""

def get_kernel_of_truth_prompt(user_query: str) -> dict:
    """
    Generate the prompt for the Kernel of Truth functionality.
    
    Args:
        user_query: The user's query about relationships
        
    Returns:
        A dictionary with system and user prompts
    """
    return {
        "system": KERNEL_OF_TRUTH_SYSTEM_PROMPT,
        "user": KERNEL_OF_TRUTH_USER_PROMPT_TEMPLATE.format(user_query=user_query)
    }

def format_kernel_of_truth_response(insights: list) -> str:
    """
    Format the insights into a response.
    
    Args:
        insights: List of relationship insights
        
    Returns:
        Formatted response
    """
    if not insights:
        return "I couldn't find any relevant relationships between entities based on your query."
    
    # Extract the content from each insight
    insight_texts = []
    for insight in insights:
        insight_texts.append(f"- {insight.get('content', '')}")
    
    # Join the insights with newlines
    insights_text = "\n".join(insight_texts)
    
    # Format the response
    return KERNEL_OF_TRUTH_RESPONSE_FORMAT.format(insights=insights_text)