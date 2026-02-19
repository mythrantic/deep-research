"""Custom report generator for reformatting research results."""

import os
from typing import List, Dict, Any
from loguru import logger
from machine_core.core.agent_base import BaseAgent


REPORT_GENERATOR_PROMPT = """
You are an expert report writer. Your task is to take research findings and 
format them according to specific user requirements.

You have access to comprehensive research context and sources. Your job is to:
1. Read and understand the research findings
2. Format the information according to the user's custom prompt
3. Maintain accuracy and cite sources appropriately
4. Create a well-structured, professional report

Always preserve the factual content while adapting the format, structure, 
and presentation style to match the user's requirements.
"""


class ReportGenerator(BaseAgent):
    """Agent for generating custom-formatted reports from research data."""
    
    def __init__(self):
        super().__init__(
            model_name=os.getenv("LLM_MODEL"),
            system_prompt=REPORT_GENERATOR_PROMPT,
            mcp_config_path="mcp_researcher.json"
        )
    
    async def generate(self, context: str, sources: List[Dict[str, Any]], 
                      custom_prompt: str, query: str) -> str:
        """
        Generate a custom report based on research context.
        
        Args:
            context: The research findings/context
            sources: List of sources used
            custom_prompt: User's custom formatting instructions
            query: Original research query
            
        Returns:
            Formatted report according to custom prompt
        """
        logger.info("Generating custom report...")
        
        # Format sources for inclusion
        sources_text = "\n\n## Available Sources:\n"
        for i, source in enumerate(sources, 1):
            sources_text += f"{i}. [{source.get('title', 'Unknown')}]({source.get('url', '')})\n"
        
        # Create the generation prompt
        generation_query = f"""
Original Research Query: {query}

Research Findings:
{context}

{sources_text}

User's Custom Formatting Request:
{custom_prompt}

Please create a report that:
1. Uses the research findings above
2. Follows the user's formatting request
3. Maintains accuracy and cites sources
4. Is well-structured and professional

Generate the report now:
"""
        
        try:
            result = await self.run_query(generation_query)
            
            # Extract the report
            if hasattr(result, 'data'):
                report = result.data
            elif hasattr(result, 'output'):
                report = result.output
            else:
                report = str(result)
            
            logger.info("Custom report generated successfully")
            return report
            
        except Exception as e:
            logger.error(f"Error generating custom report: {e}")
            raise


async def generate_custom_report(context: str, sources: List[Dict[str, Any]], 
                                 custom_prompt: str, query: str) -> str:
    """
    Generate a custom-formatted report from research data.
    
    This is a convenience function that creates a ReportGenerator and uses it.
    
    Args:
        context: The research findings/context
        sources: List of sources used
        custom_prompt: User's custom formatting instructions
        query: Original research query
        
    Returns:
        Formatted report according to custom prompt
    """
    generator = ReportGenerator()
    return await generator.generate(context, sources, custom_prompt, query)
