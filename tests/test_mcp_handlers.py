"""Medium tests for MCP server handlers.

These tests verify MCP protocol handlers with mocked API calls.
"""

import pytest
from unittest.mock import AsyncMock, patch
import mcp.types as types
from mcp_server import (
    handle_list_tools,
    handle_call_tool,
    handle_list_resources,
    handle_read_resource,
    handle_list_prompts,
    handle_get_prompt
)


class TestMCPHandlers:
    """Medium tests for MCP protocol handlers."""

    @pytest.mark.asyncio
    async def test_handle_list_tools(self):
        """Test that list_tools returns correct tool definitions."""
        tools = await handle_list_tools()
        
        assert len(tools) == 2
        
        # Verify query_perplexity tool
        query_tool = tools[0]
        assert query_tool.name == "query_perplexity"
        assert "Perplexity AI" in query_tool.description
        assert query_tool.inputSchema["required"] == ["message"]
        assert "message" in query_tool.inputSchema["properties"]
        assert "model" in query_tool.inputSchema["properties"]
        assert query_tool.inputSchema["properties"]["model"]["enum"] == [
            "sonar", "sonar-pro", "sonar-reasoning"
        ]
        
        # Verify search_perplexity tool
        search_tool = tools[1]
        assert search_tool.name == "search_perplexity"
        assert "web search" in search_tool.description.lower()
        assert search_tool.inputSchema["required"] == ["query"]

    @pytest.mark.asyncio
    async def test_handle_call_tool_query_perplexity_success(self):
        """Test query_perplexity tool execution with mocked API."""
        mock_response = {
            "choices": [{"message": {"content": "Test answer"}}],
            "model": "sonar"
        }
        
        with patch("mcp_server.perplexity_client.query", new_callable=AsyncMock) as mock_query:
            mock_query.return_value = mock_response
            
            result = await handle_call_tool(
                "query_perplexity",
                {"message": "What is AI?"}
            )
            
            assert len(result) == 1
            assert isinstance(result[0], types.TextContent)
            assert "Test answer" in result[0].text
            assert "Model: sonar" in result[0].text
            mock_query.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_call_tool_query_perplexity_with_parameters(self):
        """Test query_perplexity with custom parameters."""
        mock_response = {
            "choices": [{"message": {"content": "Custom response"}}],
            "model": "sonar-pro"
        }
        
        with patch("mcp_server.perplexity_client.query", new_callable=AsyncMock) as mock_query:
            mock_query.return_value = mock_response
            
            result = await handle_call_tool(
                "query_perplexity",
                {
                    "message": "Complex query",
                    "model": "sonar-pro",
                    "max_tokens": 2000,
                    "temperature": 0.5,
                    "system_message": "Be concise"
                }
            )
            
            assert len(result) == 1
            assert "Custom response" in result[0].text
            
            # Verify parameters were passed correctly
            call_kwargs = mock_query.call_args[1]
            assert call_kwargs["message"] == "Complex query"
            assert call_kwargs["model"] == "sonar-pro"
            assert call_kwargs["max_tokens"] == 2000
            assert call_kwargs["temperature"] == 0.5
            assert call_kwargs["system_message"] == "Be concise"

    @pytest.mark.asyncio
    async def test_handle_call_tool_search_perplexity_success(self):
        """Test search_perplexity tool execution."""
        with patch("mcp_server.perplexity_client.simple_query", new_callable=AsyncMock) as mock_query:
            mock_query.return_value = "Simple search result"
            
            result = await handle_call_tool(
                "search_perplexity",
                {"query": "weather today"}
            )
            
            assert len(result) == 1
            assert isinstance(result[0], types.TextContent)
            assert result[0].text == "Simple search result"
            mock_query.assert_called_once_with("weather today")

    @pytest.mark.asyncio
    async def test_handle_call_tool_missing_arguments(self):
        """Test tool call with missing arguments raises error."""
        with pytest.raises(ValueError, match="Missing arguments"):
            await handle_call_tool("query_perplexity", None)

    @pytest.mark.asyncio
    async def test_handle_call_tool_unknown_tool(self):
        """Test calling unknown tool returns error message."""
        result = await handle_call_tool("unknown_tool", {"arg": "value"})
        
        assert len(result) == 1
        assert isinstance(result[0], types.TextContent)
        assert "Error" in result[0].text
        assert "Unknown tool" in result[0].text

    @pytest.mark.asyncio
    async def test_handle_call_tool_api_error(self):
        """Test tool call handles API errors gracefully."""
        with patch("mcp_server.perplexity_client.simple_query", new_callable=AsyncMock) as mock_query:
            mock_query.side_effect = Exception("API connection failed")
            
            result = await handle_call_tool(
                "search_perplexity",
                {"query": "test"}
            )
            
            assert len(result) == 1
            assert isinstance(result[0], types.TextContent)
            assert "Error" in result[0].text
            assert "API connection failed" in result[0].text

    @pytest.mark.asyncio
    async def test_handle_call_tool_unexpected_response_format(self):
        """Test handling of unexpected API response format."""
        mock_response = {"unexpected": "format"}
        
        with patch("mcp_server.perplexity_client.query", new_callable=AsyncMock) as mock_query:
            mock_query.return_value = mock_response
            
            result = await handle_call_tool(
                "query_perplexity",
                {"message": "test"}
            )
            
            assert len(result) == 1
            assert "Error" in result[0].text

    @pytest.mark.asyncio
    async def test_handle_list_resources(self):
        """Test that list_resources returns server info resource."""
        resources = await handle_list_resources()
        
        assert len(resources) == 1
        assert str(resources[0].uri) == "perplexity://info"
        assert resources[0].name == "Perplexity Server Info"
        assert resources[0].mimeType == "text/plain"

    @pytest.mark.asyncio
    async def test_handle_read_resource_info(self):
        """Test reading the server info resource."""
        from mcp.types import AnyUrl
        
        content = await handle_read_resource(AnyUrl("perplexity://info"))
        
        assert "Perplexity MCP Server" in content
        assert "query_perplexity" in content
        assert "search_perplexity" in content

    @pytest.mark.asyncio
    async def test_handle_read_resource_unknown(self):
        """Test reading unknown resource raises error."""
        from mcp.types import AnyUrl
        
        with pytest.raises(ValueError, match="Unknown resource"):
            await handle_read_resource(AnyUrl("perplexity://unknown"))

    @pytest.mark.asyncio
    async def test_handle_list_prompts(self):
        """Test that list_prompts returns available prompt templates."""
        prompts = await handle_list_prompts()
        
        assert len(prompts) == 3
        
        prompt_names = [p.name for p in prompts]
        assert "research_topic" in prompt_names
        assert "quick_fact_check" in prompt_names
        assert "explain_concept" in prompt_names
        
        # Verify research_topic prompt
        research_prompt = next(p for p in prompts if p.name == "research_topic")
        assert len(research_prompt.arguments) == 1
        assert research_prompt.arguments[0].name == "topic"
        assert research_prompt.arguments[0].required is True

    @pytest.mark.asyncio
    async def test_handle_get_prompt_research_topic(self):
        """Test getting research_topic prompt."""
        result = await handle_get_prompt(
            "research_topic",
            {"topic": "quantum computing"}
        )
        
        assert isinstance(result, types.GetPromptResult)
        assert "quantum computing" in result.description
        assert len(result.messages) == 1
        assert result.messages[0].role == "user"
        assert "quantum computing" in result.messages[0].content.text
        assert "detailed research" in result.messages[0].content.text.lower()

    @pytest.mark.asyncio
    async def test_handle_get_prompt_quick_fact_check(self):
        """Test getting quick_fact_check prompt."""
        result = await handle_get_prompt(
            "quick_fact_check",
            {"claim": "Earth is flat"}
        )
        
        assert isinstance(result, types.GetPromptResult)
        assert "Earth is flat" in result.description
        assert len(result.messages) == 1
        assert "Earth is flat" in result.messages[0].content.text
        assert "verify" in result.messages[0].content.text.lower()

    @pytest.mark.asyncio
    async def test_handle_get_prompt_explain_concept(self):
        """Test getting explain_concept prompt."""
        result = await handle_get_prompt(
            "explain_concept",
            {"concept": "blockchain", "level": "beginner"}
        )
        
        assert isinstance(result, types.GetPromptResult)
        assert "blockchain" in result.description
        assert "beginner" in result.description
        assert len(result.messages) == 1
        assert "blockchain" in result.messages[0].content.text
        assert "beginner" in result.messages[0].content.text

    @pytest.mark.asyncio
    async def test_handle_get_prompt_explain_concept_default_level(self):
        """Test explain_concept prompt with default level."""
        result = await handle_get_prompt(
            "explain_concept",
            {"concept": "machine learning"}
        )
        
        assert "intermediate" in result.description
        assert "intermediate" in result.messages[0].content.text

    @pytest.mark.asyncio
    async def test_handle_get_prompt_missing_arguments(self):
        """Test getting prompt with missing arguments raises error."""
        with pytest.raises(ValueError, match="Missing arguments"):
            await handle_get_prompt("research_topic", None)

    @pytest.mark.asyncio
    async def test_handle_get_prompt_unknown_prompt(self):
        """Test getting unknown prompt raises error."""
        with pytest.raises(ValueError, match="Unknown prompt"):
            await handle_get_prompt("unknown_prompt", {"arg": "value"})
