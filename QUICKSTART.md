# Deep Research - Quick Start

## Prerequisites

1. Set up environment variables in `.env`:
   ```bash
   OPENAI_API_KEY=your_key_here
   LLM_MODEL=gpt-4  # or your preferred model
   LLM_PROVIDER=openai  # or azure, anthropic, etc.
   ```

2. Ensure `mcp_researcher.json` is configured with the MCP tools you want to use (DuckDuckGo search, web scraping, etc.)

## Installation

```bash
cd server/deep-research
uv sync  # or pip install -e .
```

## Running the Server

### Using Docker
```bash
make docker-run
```

### Direct Python
```bash
make run
# or
python src/server.py
```

## Testing the Backend

You can test the backend directly:

```python
import asyncio
from deep_research import Researcher

async def test_research():
    # Create a researcher
    researcher = Researcher("What are the latest AI trends in 2024?")
    
    # Conduct research
    await researcher.conduct_research()
    
    # Get results
    report = researcher.get_research_context()
    sources = researcher.get_research_sources()
    
    print("Research Report:")
    print(report)
    print(f"\nFound {len(sources)} sources")

# Run the test
asyncio.run(test_research())
```

## How It Works

When you call `researcher.conduct_research()`, the system:

1. **Plans** - Creates a detailed research plan
2. **Splits** - Divides plan into 3-8 subtasks
3. **Researches** - Launches parallel sub-agents for each subtask
4. **Synthesizes** - Combines all findings into a comprehensive report

Each sub-agent uses MCP tools to:
- Search the web (DuckDuckGo)
- Scrape and analyze web pages
- Extract relevant information
- Cite sources

## MCP Server Usage

Once running, the MCP server provides these tools:

- `deep_research(query)` - Full research with report
- `quick_search(query)` - Fast search results
- `write_report(research_id)` - Generate formatted report
- `get_research_sources(research_id)` - Get source list
- `get_research_context(research_id)` - Get full context

And resources:
- `research://{topic}` - Direct access to research on a topic

## Debugging

Set log level in your environment:
```bash
export LOG_LEVEL=DEBUG
```

Or check logs:
```bash
tail -f researcher_mcp_server.log
```

## Architecture

The backend uses a multi-agent architecture powered by `machine-core`:

```
┌─────────────────┐
│ Your MCP Server │
│   (server.py)   │
└────────┬────────┘
         │
         ▼
  ┌─────────────┐
  │ Researcher  │
  └──────┬──────┘
         │
         ▼
  ┌─────────────────────────────────┐
  │  run_deep_research() workflow   │
  └──────┬──────────────────────────┘
         │
         ├──► Planner → Research Plan
         │
         ├──► TaskSplitter → Subtasks
         │
         ├──► CoordinatorAgent
         │         │
         │         ├──► SubAgent 1 ───┐
         │         ├──► SubAgent 2 ───┤
         │         ├──► SubAgent 3 ───┼─► Parallel
         │         └──► SubAgent N ───┘
         │
         └──► Synthesize → Final Report
```

## Customization

### Change the number of subtasks
Edit `TASK_SPLITTER_SYSTEM_INSTRUCTIONS` in `prompts.py`:
```python
"- 3 to 8 subtasks is usually a good range. Use your judgment."
```

### Customize report format
Edit `COORDINATOR_PROMPT_TEMPLATE` in `prompts.py` to change the final report structure.

### Add more research dimensions
Edit `PLANNER_SYSTEM_INSTRUCTIONS` in `prompts.py` to guide what aspects to research.

## Next Steps

- Test with various queries
- Monitor costs via `get_costs()`
- Customize prompts for your use case
- Add more MCP tools to `mcp_researcher.json`
