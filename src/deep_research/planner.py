"""Research planner for deep research investigations."""

import os
from loguru import logger
from machine_core.core.agent_base import BaseAgent
from deep_research.prompts import PLANNER_SYSTEM_INSTRUCTIONS


class ResearchPlanner(BaseAgent):
    """Planner agent that creates detailed research plans."""
    
    def __init__(self):
        super().__init__(
            model_name=os.getenv("LLM_MODEL"),
            system_prompt=PLANNER_SYSTEM_INSTRUCTIONS,
            mcp_config_path="mcp_researcher.json"
        )
    
    async def run(self, user_query: str) -> str:
        """Required abstract method implementation."""
        return await self.generate_plan(user_query)
    
    async def generate_plan(self, user_query: str) -> str:
        """
        Generate a comprehensive research plan.
        
        Args:
            user_query: The research request
            
        Returns:
            A detailed research plan as a string
        """
        logger.info(f"Generating research plan for: {user_query}")
        
        try:
            result = await self.run_query(user_query)
            
            # Extract the plan
            if hasattr(result, 'data'):
                plan = result.data
            elif hasattr(result, 'output'):
                plan = result.output
            else:
                plan = str(result)
            
            logger.info("Research plan generated successfully")
            return plan
            
        except Exception as e:
            logger.error(f"Error generating research plan: {e}")
            raise
