# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

This is a Model Context Protocol (MCP) server that exposes Perplexity AI functionality to MCP-compatible clients like Claude Desktop, Cline, and other AI assistants. The server provides real-time web search capabilities through Perplexity's API using the MCP standard protocol.

## Common Commands

### Development Setup
```bash
# Activate the virtual environment (Python 3.11)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Test the server manually
python mcp_server.py
# or use the startup script
./run_mcp_server.sh
```

### Testing with MCP Inspector
```bash
# Test with MCP Inspector (recommended for development)
npx @modelcontextprotocol/inspector python mcp_server.py

# Test with API key from environment
PERPLEXITY_API_KEY=your_key npx @modelcontextprotocol/inspector python mcp_server.py
```

### Configuration Management
```bash
# Create/edit API key configuration
echo "PERPLEXITY_API_KEY=your_actual_key_here" > config.txt

# Test configuration loading
python -c "from config import config; print('API key loaded:', bool(config.perplexity_api_key))"
```

## Architecture

### Core Components

**MCP Protocol Layer** (`mcp_server.py`):
- Implements MCP server using stdio transport
- Handles tool registration, execution, and prompt management
- Provides two main tools: `query_perplexity` (full-featured) and `search_perplexity` (simple)
- Includes pre-defined prompts for research, fact-checking, and concept explanation

**API Client Layer** (`perplexity_client.py`):
- Handles HTTP communication with Perplexity API
- Provides both detailed query methods and simple query wrapper
- Includes health check functionality for API connectivity

**Configuration Management** (`config.py`):
- Loads API keys from multiple sources (environment variables, config.txt)
- Supports both plain text and key=value format in config files
- Provides default model and parameter settings

### Data Flow

1. MCP client sends protocol messages via stdio
2. `mcp_server.py` parses and routes tool calls
3. `perplexity_client.py` formats and sends HTTP requests to Perplexity API
4. Responses are formatted and returned via MCP protocol

### Tool Structure

The server exposes two complementary tools:

- **query_perplexity**: Full control over model selection (sonar, sonar-pro, sonar-reasoning), token limits, temperature, and system messages
- **search_perplexity**: Simplified interface using default settings for quick searches

## Development Environment

### Python Environment
- **Required**: Python 3.11 (virtual environment in `venv/`)
- **Key Dependencies**: `mcp>=1.1.0`, `httpx>=0.27.1`, `python-dotenv`

### Configuration Sources (Priority Order)
1. `PERPLEXITY_API_KEY` environment variable
2. `config.txt` file with `PERPLEXITY_API_KEY=value` format
3. `config.txt` file with plain API key content

### MCP Client Integration

For Claude Desktop (`~/Library/Application Support/Claude/claude_desktop_config.json`):
```json
{
  "mcpServers": {
    "perplexity": {
      "command": "/Users/ati/dev/simple-mcp-server/venv/bin/python",
      "args": ["/Users/ati/dev/simple-mcp-server/mcp_server.py"],
      "env": {
        "PERPLEXITY_API_KEY": "your_actual_api_key_here"
      }
    }
  }
}
```

## Key Implementation Details

### MCP Protocol Handlers
- `handle_list_tools()`: Registers available tools with input schemas
- `handle_call_tool()`: Executes tool calls and handles error responses
- `handle_list_prompts()` & `handle_get_prompt()`: Manages prompt templates
- `handle_list_resources()` & `handle_read_resource()`: Provides server info resource

### Error Handling Strategy
- Configuration errors raise `ValueError` on startup
- API errors are caught and returned as text content to MCP clients
- HTTP timeouts set to 30 seconds for Perplexity API calls

### Model Support
Available Perplexity models with their capabilities:
- `sonar`: Default model with web search
- `sonar-pro`: Advanced model with web search  
- `sonar-reasoning`: Reasoning-focused model

## Testing Patterns

### Manual Testing
Use MCP Inspector for interactive testing - it provides a web interface at `http://localhost:6274` for testing tools, prompts, and viewing protocol messages.

### Integration Testing
Test with actual MCP clients (Claude Desktop, Cline) using the configuration patterns shown above.

### API Connectivity
Use the `health_check()` method in `perplexity_client.py` to verify API connectivity and credentials.