"""Coordinator for deep research with sub-agents."""

import json
from typing import Dict, List, Optional
from loguru import logger
from machine_core.core.agent_base import BaseAgent
from deep_research.planner import ResearchPlanner
from deep_research.task_splitter import TaskSplitter
from deep_research.prompts import SUBAGENT_PROMPT_TEMPLATE, COORDINATOR_PROMPT_TEMPLATE
import os


class SubAgent(BaseAgent):
    """Sub-agent that performs focused research on a specific subtask."""
    
    def __init__(self, subtask_id: str, subtask_title: str, user_query: str, research_plan: str, subtask_description: str):
        """
        Initialize a sub-agent for a specific research subtask.
        
        Args:
            subtask_id: Unique identifier for the subtask
            subtask_title: Title of the subtask
            user_query: Original user research request
            research_plan: Overall research plan
            subtask_description: Detailed instructions for this subtask
        """
        prompt = SUBAGENT_PROMPT_TEMPLATE.format(
            user_query=user_query,
            research_plan=research_plan,
            subtask_id=subtask_id,
            subtask_title=subtask_title,
            subtask_description=subtask_description
        )
        
        super().__init__(
            model_name=os.getenv("LLM_MODEL"),
            system_prompt=prompt,
            mcp_config_path="mcp_researcher.json"
        )
        
        self.subtask_id = subtask_id
        self.subtask_title = subtask_title
    
    async def run(self, task: Optional[str] = None) -> str:
        """Required abstract method implementation."""
        return await self.research()
    
    async def research(self) -> str:
        """
        Perform research for this subtask.
        
        Returns:
            Markdown report for this subtask
        """
        logger.info(f"SubAgent {self.subtask_id} starting research: {self.subtask_title}")
        
        try:
            result = await self.run_query("Perform the research for your assigned subtask.")
            
            # Extract the report
            if hasattr(result, 'data'):
                report = result.data
            elif hasattr(result, 'output'):
                report = result.output
            else:
                report = str(result)
            
            logger.info(f"SubAgent {self.subtask_id} completed research")
            return report
            
        except Exception as e:
            logger.error(f"SubAgent {self.subtask_id} error: {e}")
            return f"# {self.subtask_id} - {self.subtask_title}\n\nError during research: {str(e)}"


class CoordinatorAgent(BaseAgent):
    """Coordinator agent that orchestrates sub-agents and synthesizes results."""
    
    def __init__(self, user_query: str, research_plan: str, subtasks: List[Dict]):
        """
        Initialize the coordinator agent.
        
        Args:
            user_query: Original user research request
            research_plan: Overall research plan
            subtasks: List of subtask dictionaries
        """
        subtasks_json = json.dumps(subtasks, indent=2, ensure_ascii=False)
        
        prompt = COORDINATOR_PROMPT_TEMPLATE.format(
            user_query=user_query,
            research_plan=research_plan,
            subtasks_json=subtasks_json
        )
        
        super().__init__(
            model_name=os.getenv("LLM_MODEL"),
            system_prompt=prompt,
            mcp_config_path="mcp_researcher.json"
        )
        
        self.user_query = user_query
        self.research_plan = research_plan
        self.subtasks = subtasks
    
    async def run(self, query: Optional[str] = None) -> str:
        """Required abstract method implementation."""
        return await self.coordinate_research()
    
    async def coordinate_research(self) -> str:
        """
        Coordinate all sub-agents and synthesize their reports.
        
        Returns:
            Final comprehensive markdown report
        """
        logger.info(f"Coordinator starting research coordination for {len(self.subtasks)} subtasks")
        
        try:
            # Create all sub-agents first
            subagents = []
            for subtask in self.subtasks:
                subagent = SubAgent(
                    subtask_id=subtask["id"],
                    subtask_title=subtask["title"],
                    user_query=self.user_query,
                    research_plan=self.research_plan,
                    subtask_description=subtask["description"]
                )
                subagents.append(subagent)
            
            # Run all sub-agents in parallel using asyncio.gather
            logger.info(f"Starting {len(subagents)} sub-agents in parallel...")
            import asyncio
            sub_reports = await asyncio.gather(*[agent.research() for agent in subagents])
            
            # Now synthesize all reports
            logger.info("Coordinator synthesizing all sub-agent reports...")
            
            all_reports = "\n\n---\n\n".join(sub_reports)
            
            synthesis_query = f"""
You have received reports from all sub-agents. Now synthesize them into a 
single comprehensive research report.

Original Request: {self.user_query}

Sub-Agent Reports:

{all_reports}

Create a polished, well-structured markdown report that integrates all findings.
"""
            
            result = await self.run_query(synthesis_query)
            
            # Extract final report
            if hasattr(result, 'data'):
                final_report = result.data
            elif hasattr(result, 'output'):
                final_report = result.output
            else:
                final_report = str(result)
            
            logger.info("Coordinator completed synthesis")
            return final_report
            
        except Exception as e:
            logger.error(f"Coordinator error: {e}")
            raise


async def run_deep_research(user_query: str) -> str:
    """
    Run the complete deep research workflow.
    
    This function orchestrates the full workflow:
    1. Generate research plan
    2. Split into subtasks
    3. Coordinate sub-agents
    4. Synthesize final report
    
    Args:
        user_query: The research request
        
    Returns:
        Comprehensive markdown research report
    """
    logger.info("Starting deep research workflow...")
    
    try:
        # Step 1: Generate research plan
        logger.info("Step 1: Generating research plan...")
        planner = ResearchPlanner()
        research_plan = await planner.generate_plan(user_query)
        logger.info(f"Research plan:\n{research_plan}\n")
        
        # Step 2: Split into subtasks
        logger.info("Step 2: Splitting into subtasks...")
        splitter = TaskSplitter()
        subtasks = await splitter.split_into_subtasks(research_plan)
        logger.info(f"Generated {len(subtasks)} subtasks")
        
        # Step 3: Coordinate research with sub-agents
        logger.info("Step 3: Coordinating sub-agent research...")
        coordinator = CoordinatorAgent(user_query, research_plan, subtasks)
        final_report = await coordinator.coordinate_research()
        
        logger.info("Deep research workflow completed successfully")
        return final_report
        
    except Exception as e:
        logger.error(f"Deep research workflow failed: {e}")
        raise
