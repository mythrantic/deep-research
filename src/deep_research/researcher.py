"""Deep Researcher - Main research orchestration class."""

from typing import Dict, List, Any, Optional
from loguru import logger
from deep_research.coordinator import run_deep_research


class Researcher:
    """
    Deep research agent that uses multi-agent workflow for comprehensive research.
    
    This agent uses a divide-and-conquer approach:
    1. Planner: Creates a detailed research plan
    2. Task Splitter: Breaks the plan into focused subtasks
    3. Coordinator: Spawns sub-agents for each subtask
    4. Sub-agents: Perform parallel research using MCP tools
    5. Coordinator: Synthesizes all findings into a comprehensive report
    """
    
    def __init__(self, query: str):
        """
        Initialize the researcher with a query.
        
        Args:
            query: The research query or topic
        """
        self.query = query
        self._context = ""
        self._sources = []
        self._source_urls = []
        self._report = ""
        self._costs = {"total_cost": 0.0}
        logger.info(f"Initialized Researcher for query: {query}")
    
    async def conduct_research(self) -> None:
        """
        Conduct comprehensive research using the multi-agent workflow.
        
        This is the main entry point that runs the full research process.
        """
        logger.info(f"Starting research for: {self.query}")
        
        try:
            # Run the deep research workflow
            self._report = await run_deep_research(self.query)
            
            # Store the report as context
            self._context = self._report
            
            # Extract sources from the report (basic implementation)
            # In a more sophisticated version, we could track sources throughout
            self._extract_sources_from_report()
            
            logger.info("Research completed successfully")
            
        except Exception as e:
            logger.error(f"Error conducting research: {e}")
            raise
    
    def _extract_sources_from_report(self) -> None:
        """
        Extract source URLs from the markdown report.
        
        This is a simple implementation that looks for markdown links.
        """
        import re
        
        # Find all markdown links in the report
        link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
        matches = re.findall(link_pattern, self._report)
        
        for title, url in matches:
            # Filter out internal links and only keep http/https URLs
            if url.startswith('http'):
                self._sources.append({
                    "title": title,
                    "url": url,
                    "content": ""
                })
                if url not in self._source_urls:
                    self._source_urls.append(url)
        
        logger.info(f"Extracted {len(self._sources)} sources from report")
    
    def get_research_context(self) -> str:
        """
        Get the full research context/report.
        
        Returns:
            The comprehensive research report
        """
        return self._context
    
    def get_research_sources(self) -> List[Dict[str, Any]]:
        """
        Get the sources used in the research.
        
        Returns:
            List of source dictionaries
        """
        return self._sources
    
    def get_source_urls(self) -> List[str]:
        """
        Get the URLs of sources used in research.
        
        Returns:
            List of source URLs
        """
        return self._source_urls
    
    async def quick_search(self, query: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Perform a quick search without the full research workflow.
        
        This is a lighter-weight alternative to conduct_research().
        
        Args:
            query: Optional query to search (defaults to self.query)
            
        Returns:
            List of search result dictionaries
        """
        search_query = query or self.query
        logger.info(f"Performing quick search for: {search_query}")
        
        # For now, we'll use the same workflow but could optimize this
        # by using only a planner and single agent instead of full coordination
        try:
            await self.conduct_research()
            
            # Return sources as search results
            return [
                {
                    "title": source.get("title", ""),
                    "url": source.get("url", ""),
                    "snippet": source.get("content", "")[:200]
                }
                for source in self._sources
            ]
            
        except Exception as e:
            logger.error(f"Error in quick search: {e}")
            raise
    
    async def write_report(self, custom_prompt: Optional[str] = None) -> str:
        """
        Generate a report based on the research.
        
        Args:
            custom_prompt: Optional custom prompt for report generation
            
        Returns:
            The generated report
        """
        if not self._context:
            logger.warning("No research context available, conducting research first")
            await self.conduct_research()
        
        # If custom prompt is provided, regenerate the report with custom formatting
        if custom_prompt:
            logger.info(f"Regenerating report with custom prompt: {custom_prompt}")
            from deep_research.report_generator import generate_custom_report
            
            custom_report = await generate_custom_report(
                context=self._context,
                sources=self._sources,
                custom_prompt=custom_prompt,
                query=self.query
            )
            return custom_report
        
        return self._report
    
    def get_costs(self) -> Dict[str, float]:
        """
        Get cost information for the research.
        
        Returns:
            Dictionary with cost information
        """
        return self._costs
