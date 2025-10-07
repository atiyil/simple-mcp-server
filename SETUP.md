# Quick Setup Guide

## Prerequisites
- Python 3.11+ (installed at `/opt/homebrew/bin/python3.11`)
- Perplexity API key

## Installation (Already Done!)

The MCP server is already set up and ready to use! Here's what was configured:

1. ✅ Python 3.11 virtual environment created
2. ✅ All dependencies installed (mcp, httpx, python-dotenv)
3. ✅ Perplexity client configured

## Configuration

Edit `config.txt` and add your Perplexity API key:
```
PERPLEXITY_API_KEY=your_actual_api_key_here
```

## Testing the Server

You can test the MCP server runs correctly:
```bash
cd ~/dev/simple-mcp-server
./run_mcp_server.sh
```

The server will start and wait for MCP protocol messages via stdio. Press `Ctrl+C` to stop.

## Using with Claude Desktop

### 1. Locate your Claude Desktop config:
```bash
~/Library/Application Support/Claude/claude_desktop_config.json
```

### 2. Add the MCP server configuration:

Open the file and add (or merge with existing `mcpServers`):

```json
{
  "mcpServers": {
    "perplexity": {
      "command": "/Users/ati/dev/simple-mcp-server/venv/bin/python",
      "args": [
        "/Users/ati/dev/simple-mcp-server/mcp_server.py"
      ],
      "env": {
        "PERPLEXITY_API_KEY": "your_actual_api_key_here"
      }
    }
  }
}
```

**Important:** Replace `your_actual_api_key_here` with your real Perplexity API key!

### 3. Restart Claude Desktop

Close and reopen Claude Desktop. The Perplexity MCP server will automatically start when needed.

### 4. Use in Claude

You can now ask Claude things like:
- "Use Perplexity to search for the latest news about AI"
- "Query Perplexity about quantum computing"
- "What are the current trends in renewable energy?"

Claude will automatically use the Perplexity tools when appropriate!

## Available Tools

- **query_perplexity**: Full-featured queries with model selection
- **search_perplexity**: Quick searches with defaults

## Available Prompts

- **research_topic**: Research with detailed information
- **quick_fact_check**: Verify facts quickly
- **explain_concept**: Get explanations at different levels

## Project Structure

```
simple-mcp-server/
├── mcp_server.py        # Main MCP server
├── perplexity_client.py # Perplexity API client
├── config.py            # Configuration loader
├── config.txt           # API key (keep secret!)
├── requirements.txt     # Python dependencies
├── mcp_config.json      # Example config
├── run_mcp_server.sh    # Startup script
├── README.md            # Full documentation
├── SETUP.md             # This file
└── venv/                # Python 3.11 virtual environment
```

## Python Versions

- **MCP Server** (this project): Python 3.11
- **Perplexity FastAPI** (`~/dev/perplexity`): Python 3.9

Both projects share the same `perplexity_client.py` and `config.py` files but run independently.

## Troubleshooting

### Server not appearing in Claude Desktop
1. Check the path in `claude_desktop_config.json` is correct
2. Verify your API key is set
3. Restart Claude Desktop
4. Check Claude's logs for errors

### Import errors
```bash
cd ~/dev/simple-mcp-server
source venv/bin/activate
pip install -r requirements.txt
```

### API key not found
Make sure `config.txt` exists and contains:
```
PERPLEXITY_API_KEY=your_key_here
```

## Next Steps

See `README.md` for complete documentation and advanced usage.
