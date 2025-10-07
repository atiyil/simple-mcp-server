# Perplexity MCP Server

This is a standalone Model Context Protocol (MCP) server that exposes Perplexity AI functionality to MCP-compatible clients like Claude Desktop, Cline, and other AI assistants.

## What is MCP?

Model Context Protocol (MCP) is an open standard that enables AI assistants to securely access external tools and data sources. This MCP server allows AI assistants to query Perplexity AI for real-time web information and research.

## Features

- **Two Query Tools:**
  - `query_perplexity`: Full-featured queries with model selection and parameter control
  - `search_perplexity`: Quick searches with default settings

- **Multiple Models:**
  - `sonar` (default, web search enabled)
  - `sonar-pro` (advanced model with web search)
  - `sonar-reasoning` (reasoning-focused model)

- **Pre-configured Prompts:**
  - Research topics with detailed information
  - Quick fact checking
  - Concept explanations at different levels

- **Resources:**
  - Server information accessible at `perplexity://info`

## Setup

### 1. Install Dependencies

Make sure you're in your virtual environment:

```bash
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

Install the MCP package:

```bash
pip install -r requirements.txt
```

### 2. Configure Your API Key

Make sure your Perplexity API key is configured. You can either:

**Option A: Use the existing config.txt file**
```
PERPLEXITY_API_KEY=your_actual_api_key_here
```

**Option B: Set as environment variable**
```bash
export PERPLEXITY_API_KEY=your_actual_api_key_here
```

### 3. Test the MCP Server with MCP Inspector

The best way to test your MCP server is using the official MCP Inspector, which provides a web interface to interact with your server:

```bash
# Make sure you have npx installed (comes with Node.js)
npx @modelcontextprotocol/inspector python mcp_server.py
```

This will:
1. Start the MCP Inspector on `http://localhost:6274`
2. Automatically open your browser to the inspector interface
3. Connect your MCP server to the inspector

In the inspector, you can:
- View all available tools (`query_perplexity`, `search_perplexity`)
- Test tools with custom parameters
- View available prompts and resources
- See real-time MCP protocol messages

**To run in the background:**
```bash
PERPLEXITY_API_KEY=your_api_key npx @modelcontextprotocol/inspector python mcp_server.py
```

**To stop the inspector:**
```bash
pkill -f "modelcontextprotocol/inspector"
```

**Alternative: Test directly (without inspector)**

You can also run the server directly:

```bash
python mcp_server.py
```

The server uses stdio transport, so it will wait for MCP protocol messages. Press `Ctrl+C` to stop.

## Usage with Claude Desktop

### 1. Locate Claude Desktop Configuration

On macOS:
```bash
~/Library/Application Support/Claude/claude_desktop_config.json
```

On Windows:
```
%APPDATA%\Claude\claude_desktop_config.json
```

On Linux:
```bash
~/.config/Claude/claude_desktop_config.json
```

### 2. Add the Server Configuration

Edit the Claude Desktop config file and add the Perplexity MCP server:

```json
{
  "mcpServers": {
    "perplexity": {
      "command": "python",
      "args": [
        "/Users/ati/dev/perplexity/mcp_server.py"
      ],
      "env": {
        "PERPLEXITY_API_KEY": "your_actual_api_key_here"
      }
    }
  }
}
```

**Important:** Replace `/Users/ati/dev/perplexity/mcp_server.py` with the actual absolute path to your MCP server script.

### 3. Restart Claude Desktop

Close and reopen Claude Desktop to load the new MCP server.

### 4. Use the Tools

In Claude Desktop, you can now ask questions like:

- "Use the search_perplexity tool to find information about quantum computing"
- "Query Perplexity about the latest developments in AI"
- "What are the current trends in renewable energy?" (Claude will automatically use the tool)

Claude will automatically detect when to use the Perplexity tools based on your questions.

## Usage with Cline (VS Code Extension)

### 1. Open Cline Settings

In VS Code, go to Cline settings and find the MCP Servers configuration.

### 2. Add Server Configuration

Add the following configuration:

```json
{
  "perplexity": {
    "command": "python",
    "args": ["/Users/ati/dev/perplexity/mcp_server.py"],
    "env": {
      "PERPLEXITY_API_KEY": "your_actual_api_key_here"
    }
  }
}
```

### 3. Restart VS Code

Reload the window or restart VS Code.

## Usage with Other MCP Clients

Any MCP-compatible client can use this server. The configuration format is similar:

```json
{
  "command": "python",
  "args": ["/path/to/mcp_server.py"],
  "env": {
    "PERPLEXITY_API_KEY": "your_api_key"
  }
}
```

## Available Tools

### query_perplexity

Full-featured query with all parameters:

```json
{
  "message": "Explain quantum entanglement",
  "model": "sonar-pro",
  "max_tokens": 1000,
  "temperature": 0.7,
  "system_message": "Explain in simple terms"
}
```

### search_perplexity

Simple search with default settings:

```json
{
  "query": "Latest news about SpaceX"
}
```

## Available Prompts

### research_topic
- **Arguments:** topic (required)
- **Description:** Research a topic with detailed information and citations

### quick_fact_check
- **Arguments:** claim (required)
- **Description:** Verify a fact or claim

### explain_concept
- **Arguments:** concept (required), level (optional: beginner/intermediate/advanced)
- **Description:** Get a detailed explanation of a concept

## Troubleshooting

### Server Not Appearing in Claude Desktop

1. Check that the path to `mcp_server.py` is absolute and correct
2. Verify your Python environment has all dependencies installed
3. Check the Claude Desktop logs for errors
4. Make sure your API key is correctly set

### API Key Issues

If you get authentication errors:

1. Verify your API key is valid in the Perplexity dashboard
2. Check that the environment variable is being passed correctly
3. Try using the config.txt file instead of environment variables

### Import Errors

If you get module import errors:

```bash
# Make sure you're in the project directory
cd ~/dev/perplexity

# Install dependencies
pip install -r requirements.txt
```

## Architecture

The MCP server is completely independent from the FastAPI service:

- **FastAPI Service** (`main.py`): REST API on port 8000
- **MCP Server** (`mcp_server.py`): MCP protocol via stdio
- **Shared Client** (`perplexity_client.py`): Both use the same Perplexity API client

They can run simultaneously without conflicts.

## Running Both Services

You can run both the FastAPI service and MCP server at the same time:

**Terminal 1 - FastAPI Service:**
```bash
python main.py
```

**Terminal 2 - MCP Server (if testing manually):**
```bash
python mcp_server.py
```

**Claude Desktop/Cline:** Will automatically start the MCP server when needed.

## Development

### Adding New Tools

Edit `mcp_server.py` and add to `handle_list_tools()`:

```python
types.Tool(
    name="your_tool_name",
    description="Tool description",
    inputSchema={...}
)
```

Then implement in `handle_call_tool()`.

### Adding New Prompts

Add to `handle_list_prompts()` and implement in `handle_get_prompt()`.

## Security Notes

- The MCP server only runs when called by an MCP client
- Your API key is passed via environment variables (not stored in the client)
- All communication happens locally via stdio (no network exposure)

## Related Documentation

- [MCP Documentation](https://modelcontextprotocol.io)
- [Perplexity API Docs](https://docs.perplexity.ai)
- [Claude Desktop MCP Guide](https://docs.anthropic.com/claude/docs/mcp)

## License

This project is open source and available under the MIT License.
