"""Task splitter for deep research workflow."""

import json
from typing import List, Dict
from pydantic import BaseModel, Field
from loguru import logger
from machine_core.core.agent_base import BaseAgent
from deep_research.prompts import TASK_SPLITTER_SYSTEM_INSTRUCTIONS
import os


class Subtask(BaseModel):
    """A research subtask."""
    id: str = Field(
        ...,
        description="Short identifier for the subtask (e.g. 'background', 'analysis', 'trends')"
    )
    title: str = Field(
        ...,
        description="Short descriptive title of the subtask"
    )
    description: str = Field(
        ...,
        description="Clear, detailed instructions for the sub-agent that will research this subtask"
    )


class SubtaskList(BaseModel):
    """List of research subtasks."""
    subtasks: List[Subtask] = Field(
        ...,
        description="List of subtasks that together cover the whole research plan"
    )


class TaskSplitter(BaseAgent):
    """Agent that splits research plans into focused subtasks."""
    
    def __init__(self):
        super().__init__(
            model_name=os.getenv("LLM_MODEL"),
            system_prompt=TASK_SPLITTER_SYSTEM_INSTRUCTIONS,
            mcp_config_path="mcp_researcher.json"
        )
    
    async def run(self, research_plan: str) -> List[Dict]:
        """Required abstract method implementation."""
        return await self.split_into_subtasks(research_plan)
    
    async def split_into_subtasks(self, research_plan: str) -> List[Dict]:
        """
        Split a research plan into discrete subtasks.
        
        Args:
            research_plan: The detailed research plan
            
        Returns:
            List of subtask dictionaries
        """
        logger.info("Splitting research plan into subtasks...")
        
        try:
            # Request JSON output from the agent
            query = f"""
Based on this research plan, create subtasks in JSON format.

Research Plan:
{research_plan}

Return ONLY valid JSON matching this schema:
{{
  "subtasks": [
    {{
      "id": "string",
      "title": "string", 
      "description": "string"
    }}
  ]
}}
"""
            
            result = await self.run_query(query)
            
            # Extract the result
            content = ""
            if hasattr(result, 'data'):
                content = result.data
            elif hasattr(result, 'output'):
                content = result.output
            else:
                content = str(result)
            
            # Parse JSON from the response
            # Try to find JSON in the response
            content = content.strip()
            
            # Remove markdown code blocks if present
            if content.startswith('```'):
                lines = content.split('\n')
                content = '\n'.join(lines[1:-1]) if len(lines) > 2 else content
            if content.startswith('```json'):
                content = content[7:]
            if content.endswith('```'):
                content = content[:-3]
            content = content.strip()
            
            # Parse the JSON
            parsed = json.loads(content)
            subtasks = parsed.get('subtasks', [])
            
            logger.info(f"Generated {len(subtasks)} subtasks:")
            for task in subtasks:
                logger.info(f"  - {task['title']}")
            
            return subtasks
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.error(f"Response was: {content}")
            # Fallback: create a single comprehensive task
            return [{
                "id": "comprehensive",
                "title": "Comprehensive Research",
                "description": research_plan
            }]
        except Exception as e:
            logger.error(f"Error splitting tasks: {e}")
            raise
