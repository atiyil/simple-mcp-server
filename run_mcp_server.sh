#!/bin/bash

# Perplexity MCP Server Startup Script
# This script runs the MCP server with the correct Python environment

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Check if virtual environment exists
if [ ! -d "$SCRIPT_DIR/venv" ]; then
    echo "Error: Virtual environment not found at $SCRIPT_DIR/venv"
    echo "Please run setup first:"
    echo "  cd $SCRIPT_DIR"
    echo "  /opt/homebrew/bin/python3.11 -m venv venv"
    echo "  source venv/bin/activate"
    echo "  pip install -r requirements.txt"
    exit 1
fi

# Run the MCP server using the venv Python
echo "Starting Perplexity MCP Server..."
echo "Press Ctrl+C to stop"
"$SCRIPT_DIR/venv/bin/python" "$SCRIPT_DIR/mcp_server.py"
