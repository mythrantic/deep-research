# Deep Research MCP

MCP server for Deep Research, enabling AI assistants to perform deep web research and generate comprehensive reports. Built with Machine Core it supports multiple agents in a divide and conquer approach to research. These agents can be edited to behave as you wish, for this reasercher to play a certain persona to research.

for example if you are researching some finace topic, A "Logic" type agent and a "Creative" type will give very different results. you can also just mix and match.

## Quick Start with Claude Desktop

**Want to use this with Claude Desktop right away?** Here's the fastest path:

1. **Install dependencies:**
   ```bash
   git clone https://github.com/mythrantic/deep-research.git
   pip install -r requirements.txt
   ```

2. **Set up your Claude Desktop config** at `~/Library/Application Support/Claude/claude_desktop_config.json`:
   ```json
   {
     "mcpServers": {
       "gptr-mcp": {
         "command": "python",
         "args": ["/absolute/path/to/deep-research/src/server.py"],
         "env": {
           "OLLAMA_BASE_URL": "your-ollama-base-url-here",
           "LLM_MODEL": "your-llm-model-here"
           // you can use any env var https://github.com/samletnorge/machine-core defines and its dependency. it is the multiagent framework that allows this to work.
         }
       }
     }
   }
   ```

3. **Restart Claude Desktop** and start researching! 🎉

For detailed setup instructions, see the [full Claude Desktop Integration section](#-claude-desktop-integration) below.

### Resources
- `research_resource`: Get web resources related to a given task via research.

### Primary Tools

- `deep_research`: Performs deep web research on a topic, finding the most reliable and relevant information
- `quick_search`: Performs a fast web search optimized for speed over quality, returning search results with snippets. Supports any Deep Research supported web retriever such as Tavily, Bing, Google, etc... Learn more [here](https://)
- `write_report`: Generate a report based on research results
- `get_research_sources`: Get the sources used in the research
- `get_research_context`: Get the full context of the research

### Prompts

- `research_query`: Create a research query prompt

## Prerequisites

- uv/make 

## ⚙️ Installation

1. Clone the repository:
```bash
git clone https://github.com/mythrantic/deep-research.git
cd deep-research
```

2. Install the deep-research dependencies:
```bash
cd deep-research
uv sync
```

3. Set up your environment variables:
   - Copy the `.env.example` file to create a new file named `.env`:
   ```bash
   cp .env.example .env
   ```
   - Edit the `.env` file and add your API keys and configure other settings:


You can also add any other env variable allowed by https://github.com/samletnorge/machine-core and its dependencies, such as `LLM_PROVIDER` etc

## 🚀 Running the MCP Server

You can run the MCP server in several ways:

### Method 1: Directly using Python

```bash
python src/server.py
mcp run src/server.py
uv run src/server.py
```

### Method 3: Using Docker (recommended for production)

#### Quick Start

The simplest way to run with Docker:

```bash
# Build and run with docker-compose
docker-compose up -d

# Or manually:
docker build -t deep-research .
docker run -d \
  --name deep-research \
  -p 8000:8000 \
  --env-file .env \
  deep-research
```
