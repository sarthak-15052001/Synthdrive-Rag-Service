from typing import Dict, List, Any, Optional
import logging
import json
from openai import OpenAI

from src.core.config import settings

# Configure logging
logger = logging.getLogger(__name__)


class Synthesizer:
    """
    Synthesizer node for SynthDrive's LangGraph.
    
    This node combines all retrieved documents and graph insights into a coherent,
    cited final response using an LLM. It populates the "final_answer" field in the state object.
    """

    def __init__(self):
        """
        Initialize the Synthesizer.
        """
        # Initialize OpenAI client for generating the final answer
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
    
    async def synthesize(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main entry point for the Synthesizer node.
        
        This method combines all retrieved documents and graph insights into a coherent,
        cited final response and updates the state object.
        
        Args:
            state: The current state object with the following structure:
                {
                    'original_query': str,
                    'organization_id': str,
                    'plan': Optional[str],
                    'retrieved_docs': List[Dict[str, Any]],
                    'graph_insights': List[Dict[str, Any]],
                    'final_answer': Optional[str],
                    'error_log': List[str]
                }
                
        Returns:
            The updated state object with the final answer
        """
        try:
            # Extract information from state
            query = state.get('original_query', '')
            organization_id = state.get('organization_id', 'default')
            retrieved_docs = state.get('retrieved_docs', [])
            graph_insights = state.get('graph_insights', [])
            
            logger.info(f"Synthesizer processing query: {query} for organization: {organization_id}")
            
            # Check if we have any documents or insights to synthesize
            if not retrieved_docs and not graph_insights:
                logger.warning("No documents or graph insights to synthesize")
                state['final_answer'] = "I don't have enough information to provide a comprehensive answer to your query."
                return state
            
            # Generate the final answer
            final_answer = await self._generate_final_answer(query, retrieved_docs, graph_insights)
            
            # Update the state with the final answer
            state['final_answer'] = final_answer
            
            logger.info("Successfully generated final answer")
            
            return state
            
        except Exception as e:
            error_message = f"Error in Synthesizer: {str(e)}"
            logger.error(error_message)
            
            # Add error to the error log
            state['error_log'] = state.get('error_log', []) + [error_message]
            
            # Set a fallback final answer
            state['final_answer'] = "I encountered an error while trying to synthesize the information. Please try again."
            
            return state
    
    async def _generate_final_answer(self, query: str, retrieved_docs: List[Dict[str, Any]], graph_insights: List[Dict[str, Any]]) -> str:
        """
        Generate a final answer by combining retrieved documents and graph insights.
        
        Args:
            query: The original query
            retrieved_docs: List of retrieved documents
            graph_insights: List of graph insights
            
        Returns:
            A coherent, cited final answer
        """
        try:
            # Format the retrieved documents for the prompt
            formatted_docs = []
            for i, doc in enumerate(retrieved_docs):
                citation_id = doc.get('citation_id', f'doc-{i+1}')
                content = doc.get('content', '')
                source = doc.get('source', 'unknown')
                
                formatted_docs.append(f"[{citation_id}] Source: {source}\nContent: {content}\n")
            
            # Format the graph insights for the prompt
            formatted_insights = []
            for i, insight in enumerate(graph_insights):
                citation_id = insight.get('citation_id', f'insight-{i+1}')
                content = insight.get('content', '')
                explanation = insight.get('explanation', '')
                inferred_context = insight.get('inferred_context', '')
                
                formatted_insights.append(
                    f"[{citation_id}] Content: {content}\n"
                    f"Explanation: {explanation}\n"
                    f"Inferred Context: {inferred_context}\n"
                )
            
            # Create a prompt for generating the final answer
            prompt = f"""
            You are the Synthesizer node in SynthDrive's LangGraph system. Your task is to combine all retrieved documents and graph insights into a coherent, cited final answer.
            
            Original Query: {query}
            
            Retrieved Documents:
            {"".join(formatted_docs) if formatted_docs else "No documents retrieved."}
            
            Graph Insights:
            {"".join(formatted_insights) if formatted_insights else "No graph insights available."}
            
            Instructions:
            1. Synthesize the information from both retrieved documents and graph insights.
            2. Provide a comprehensive, coherent answer to the original query.
            3. Include citations to specific sources using the citation IDs in square brackets (e.g., [doc-1], [graph-rel-2]).
            4. Ensure the answer is factually accurate and based only on the provided information.
            5. If the information is insufficient to answer the query, acknowledge the limitations.
            6. Format the answer in a clear, structured way that is easy to read.
            
            Final Answer:
            """
            
            # Call OpenAI to generate the final answer
            response = self.openai_client.chat.completions.create(
                model=settings.LLM_MODEL,
                messages=[
                    {"role": "system", "content": "You are an expert at synthesizing information from multiple sources to provide comprehensive, accurate answers."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            final_answer = response.choices[0].message.content.strip()
            
            logger.info("Successfully generated final answer")
            
            return final_answer
            
        except Exception as e:
            logger.error(f"Error generating final answer: {str(e)}")
            return f"Error generating final answer: {str(e)}"