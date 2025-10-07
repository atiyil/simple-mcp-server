"""Standalone MCP Server for Perplexity AI.

This MCP server exposes Perplexity AI functionality via the Model Context Protocol.
It can be used with Claude Desktop, Cline, or any other MCP-compatible client.

The server runs independently from the FastAPI service and uses the same
perplexity_client module for API communication.
"""

import asyncio
import logging
from typing import Any

from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types

from perplexity_client import perplexity_client

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("perplexity-mcp")

# Create MCP server instance
server = Server("perplexity-mcp")


@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """
    List available tools for the MCP client.
    
    Returns tools for querying Perplexity AI with various parameters.
    """
    return [
        types.Tool(
            name="query_perplexity",
            description=(
                "Query Perplexity AI for information. This tool provides access to "
                "real-time web search and AI-powered answers using various Llama models. "
                "Use this for research, fact-checking, and getting current information."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "description": "The question or prompt to send to Perplexity AI",
                    },
                    "model": {
                        "type": "string",
                        "description": "Model to use (optional)",
                        "enum": [
                            "sonar",
                            "sonar-pro",
                            "sonar-reasoning",
                        ],
                    },
                    "max_tokens": {
                        "type": "integer",
                        "description": "Maximum tokens in response (default: 1000)",
                        "minimum": 1,
                        "maximum": 4000,
                    },
                    "temperature": {
                        "type": "number",
                        "description": "Response randomness 0-1 (default: 0.7)",
                        "minimum": 0,
                        "maximum": 1,
                    },
                    "system_message": {
                        "type": "string",
                        "description": "Optional system message to set context",
                    },
                },
                "required": ["message"],
            },
        ),
        types.Tool(
            name="search_perplexity",
            description=(
                "Quick web search using Perplexity AI with default settings. "
                "Best for simple queries that need real-time information from the web."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query",
                    },
                },
                "required": ["query"],
            },
        ),
    ]


@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """
    Handle tool execution requests from MCP clients.
    
    Args:
        name: The name of the tool to execute
        arguments: The arguments for the tool
        
    Returns:
        List of content items (typically text responses)
    """
    if not arguments:
        raise ValueError("Missing arguments for tool call")

    try:
        if name == "query_perplexity":
            # Full query with all parameters
            logger.info(f"Executing query_perplexity with message: {arguments.get('message', '')[:100]}...")
            
            response = await perplexity_client.query(
                message=arguments["message"],
                model=arguments.get("model"),
                max_tokens=arguments.get("max_tokens"),
                temperature=arguments.get("temperature"),
                system_message=arguments.get("system_message"),
            )
            
            # Extract response text from API response
            if "choices" in response and len(response["choices"]) > 0:
                response_text = response["choices"][0]["message"]["content"]
                model_used = response.get("model", "unknown")
                
                # Format response with model info
                formatted_response = f"{response_text}\n\n---\n*Model: {model_used}*"
                
                return [
                    types.TextContent(
                        type="text",
                        text=formatted_response,
                    )
                ]
            else:
                raise ValueError("Unexpected response format from Perplexity API")
                
        elif name == "search_perplexity":
            # Simple search with defaults
            logger.info(f"Executing search_perplexity with query: {arguments.get('query', '')[:100]}...")
            
            response_text = await perplexity_client.simple_query(arguments["query"])
            
            return [
                types.TextContent(
                    type="text",
                    text=response_text,
                )
            ]
        else:
            raise ValueError(f"Unknown tool: {name}")
            
    except Exception as e:
        logger.error(f"Error executing tool {name}: {str(e)}")
        error_message = f"Error: {str(e)}"
        return [
            types.TextContent(
                type="text",
                text=error_message,
            )
        ]


@server.list_resources()
async def handle_list_resources() -> list[types.Resource]:
    """
    List available resources (currently provides server info).
    
    Resources can be used by MCP clients to access contextual information.
    """
    return [
        types.Resource(
            uri="perplexity://info",
            name="Perplexity Server Info",
            description="Information about the Perplexity MCP server",
            mimeType="text/plain",
        ),
    ]


@server.read_resource()
async def handle_read_resource(uri: types.AnyUrl) -> str:
    """
    Read resource content.
    
    Args:
        uri: The URI of the resource to read
        
    Returns:
        The resource content as a string
    """
    if str(uri) == "perplexity://info":
        return """Perplexity MCP Server

This server provides access to Perplexity AI through the Model Context Protocol.

Available Tools:
- query_perplexity: Full-featured query with model selection and parameters
- search_perplexity: Quick search with default settings

Available Models:
- llama-3.1-sonar-small-128k-online (default, web search enabled)
- llama-3.1-sonar-small-128k-chat
- llama-3.1-sonar-large-128k-online (web search enabled)
- llama-3.1-sonar-large-128k-chat
- llama-3.1-8b-instruct
- llama-3.1-70b-instruct

Use the online models for real-time web information.
"""
    else:
        raise ValueError(f"Unknown resource: {uri}")


@server.list_prompts()
async def handle_list_prompts() -> list[types.Prompt]:
    """
    List available prompt templates.
    
    Prompts provide pre-configured query templates for common use cases.
    """
    return [
        types.Prompt(
            name="research_topic",
            description="Research a topic with detailed information and citations",
            arguments=[
                types.PromptArgument(
                    name="topic",
                    description="The topic to research",
                    required=True,
                ),
            ],
        ),
        types.Prompt(
            name="quick_fact_check",
            description="Quickly verify a fact or claim",
            arguments=[
                types.PromptArgument(
                    name="claim",
                    description="The claim or fact to verify",
                    required=True,
                ),
            ],
        ),
        types.Prompt(
            name="explain_concept",
            description="Get a detailed explanation of a concept",
            arguments=[
                types.PromptArgument(
                    name="concept",
                    description="The concept to explain",
                    required=True,
                ),
                types.PromptArgument(
                    name="level",
                    description="Explanation level (beginner, intermediate, advanced)",
                    required=False,
                ),
            ],
        ),
    ]


@server.get_prompt()
async def handle_get_prompt(
    name: str, arguments: dict[str, str] | None
) -> types.GetPromptResult:
    """
    Generate a prompt based on the template name and arguments.
    
    Args:
        name: The prompt template name
        arguments: Arguments for the prompt template
        
    Returns:
        The generated prompt with messages
    """
    if not arguments:
        raise ValueError("Missing arguments for prompt")

    if name == "research_topic":
        topic = arguments.get("topic", "")
        return types.GetPromptResult(
            description=f"Research information about {topic}",
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(
                        type="text",
                        text=f"Please provide detailed research about {topic}. Include key facts, recent developments, and reliable sources.",
                    ),
                ),
            ],
        )
    elif name == "quick_fact_check":
        claim = arguments.get("claim", "")
        return types.GetPromptResult(
            description=f"Verify the claim: {claim}",
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(
                        type="text",
                        text=f"Is this claim accurate: {claim}? Please verify with current information and sources.",
                    ),
                ),
            ],
        )
    elif name == "explain_concept":
        concept = arguments.get("concept", "")
        level = arguments.get("level", "intermediate")
        return types.GetPromptResult(
            description=f"Explain {concept} at {level} level",
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(
                        type="text",
                        text=f"Please explain {concept} at a {level} level. Include examples and practical applications.",
                    ),
                ),
            ],
        )
    else:
        raise ValueError(f"Unknown prompt: {name}")


async def main():
    """Run the MCP server using stdio transport."""
    logger.info("Starting Perplexity MCP Server...")
    
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        logger.info("MCP Server running on stdio")
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="perplexity-mcp",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


if __name__ == "__main__":
    asyncio.run(main())
