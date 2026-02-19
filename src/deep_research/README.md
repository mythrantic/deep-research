# Deep Research Backend

This is the backend implementation for the Deep Research MCP server. It implements a multi-agent research system using the `machine-core` package.

## Architecture

The system uses a divide-and-conquer approach with the following components:

### 1. **Researcher** (`researcher.py`)
The main entry point that orchestrates the entire research workflow. It provides the interface expected by the MCP server:
- `conduct_research()` - Runs the full research workflow
- `get_research_context()` - Returns the research report
- `get_research_sources()` - Returns sources used
- `get_source_urls()` - Returns source URLs
- `quick_search()` - Performs lighter-weight search
- `write_report()` - Generates/returns the report
- `get_costs()` - Returns cost information

### 2. **ResearchPlanner** (`planner.py`)
Creates a detailed research plan based on the user's query. Uses the LLM to break down the research request into specific investigation areas.

### 3. **TaskSplitter** (`task_splitter.py`)
Takes the research plan and splits it into 3-8 discrete subtasks that can be researched independently. Each subtask has:
- `id` - Short identifier
- `title` - Descriptive title
- `description` - Detailed instructions for the sub-agent

### 4. **CoordinatorAgent** (`coordinator.py`)
Orchestrates the research by:
- Creating sub-agents for each subtask
- Running them in parallel using `asyncio.gather()`
- Collecting all sub-agent reports
- Synthesizing them into a comprehensive final report

### 5. **SubAgent** (`coordinator.py`)
Individual research agents that:
- Focus on a specific subtask
- Use MCP tools (DuckDuckGo search, web scraping, etc.)
- Return a markdown report for their assigned area

### 6. **Prompts** (`prompts.py`)
System prompts for each agent type:
- `PLANNER_SYSTEM_INSTRUCTIONS` - For the research planner
- `TASK_SPLITTER_SYSTEM_INSTRUCTIONS` - For task splitting
- `SUBAGENT_PROMPT_TEMPLATE` - For individual sub-agents
- `COORDINATOR_PROMPT_TEMPLATE` - For the coordinator

## Workflow

```
User Query
    ↓
ResearchPlanner → Research Plan
    ↓
TaskSplitter → List of Subtasks
    ↓
CoordinatorAgent
    ├─→ SubAgent 1 (parallel)
    ├─→ SubAgent 2 (parallel)
    ├─→ SubAgent 3 (parallel)
    └─→ SubAgent N (parallel)
    ↓
Synthesis → Final Report
```

## Dependencies

- **machine-core** - Multi-agent orchestration framework
- **loguru** - Logging
- **pydantic** - Data validation
- MCP tools for web search and scraping

## Configuration

The system uses:
- `LLM_MODEL` environment variable for the model to use
- `mcp_researcher.json` for MCP server configuration
- Various API keys as needed (OpenAI, etc.)

## Usage

The `Researcher` class is the main interface:

```python
from deep_research import Researcher

# Create researcher
researcher = Researcher("What are the latest trends in AI?")

# Conduct research
await researcher.conduct_research()

# Get results
context = researcher.get_research_context()
sources = researcher.get_research_sources()
```

This is used by the MCP server in `server.py` to provide research capabilities via the Model Context Protocol.
