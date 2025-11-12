"""Integration tests for end-to-end flows.

These tests verify complete workflows with comprehensive mocks simulating
real API interactions. They can optionally use real API calls if configured.
"""

import pytest
import os
from unittest.mock import AsyncMock, patch, MagicMock
import mcp.types as types
from config import Config
from perplexity_client import PerplexityClient
from mcp_server import handle_call_tool, handle_get_prompt


# Set to True to run tests against real Perplexity API (requires valid API key)
USE_REAL_API = os.getenv("TEST_USE_REAL_API", "false").lower() == "true"


@pytest.fixture
def mock_api_key():
    """Provide a mock API key for testing."""
    with patch.dict(os.environ, {"PERPLEXITY_API_KEY": "test-api-key"}):
        yield


class TestIntegrationEndToEnd:
    """Integration tests for complete end-to-end workflows."""

    @pytest.mark.asyncio
    @pytest.mark.skipif(not USE_REAL_API, reason="Real API tests disabled")
    async def test_real_api_simple_query(self, mock_api_key):
        """Test actual Perplexity API call (optional, requires real API key)."""
        # This test only runs if TEST_USE_REAL_API=true and uses a real API key
        client = PerplexityClient()
        
        response = await client.simple_query("What is 2+2?")
        
        assert isinstance(response, str)
        assert len(response) > 0

    @pytest.mark.asyncio
    async def test_config_to_client_integration(self):
        """Test Config and PerplexityClient integration."""
        with patch.dict(os.environ, {"PERPLEXITY_API_KEY": "integration-test-key"}):
            config = Config()
            
            # Mock the config module used by perplexity_client
            with patch("perplexity_client.config", config):
                client = PerplexityClient()
                
                assert client.api_key == "integration-test-key"
                assert client.base_url == config.perplexity_base_url

    @pytest.mark.asyncio
    async def test_full_query_workflow(self):
        """Test complete workflow from tool call to response."""
        mock_api_response = {
            "choices": [{
                "message": {
                    "content": "Artificial Intelligence is a field of computer science."
                }
            }],
            "model": "sonar",
            "usage": {"total_tokens": 50}
        }
        
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_response_obj = MagicMock()
            mock_response_obj.json.return_value = mock_api_response
            mock_response_obj.raise_for_status = MagicMock()
            mock_client.post = AsyncMock(return_value=mock_response_obj)
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            # Execute the complete flow
            result = await handle_call_tool(
                "query_perplexity",
                {"message": "What is AI?"}
            )
            
            assert len(result) == 1
            assert isinstance(result[0], types.TextContent)
            assert "Artificial Intelligence" in result[0].text
            assert "Model: sonar" in result[0].text
            
            # Verify the API was called correctly
            mock_client.post.assert_called_once()
            call_args = mock_client.post.call_args
            assert "chat/completions" in call_args[0][0]

    @pytest.mark.asyncio
    async def test_search_workflow_with_defaults(self):
        """Test search workflow using default configuration."""
        with patch("mcp_server.perplexity_client.simple_query", new_callable=AsyncMock) as mock_query:
            mock_query.return_value = "Current weather is sunny, 72°F"
            
            result = await handle_call_tool(
                "search_perplexity",
                {"query": "weather in San Francisco"}
            )
            
            assert len(result) == 1
            assert "sunny" in result[0].text
            assert "72°F" in result[0].text

    @pytest.mark.asyncio
    async def test_prompt_to_tool_workflow(self):
        """Test workflow from prompt generation to tool execution."""
        # Step 1: Get prompt
        prompt_result = await handle_get_prompt(
            "research_topic",
            {"topic": "renewable energy"}
        )
        
        assert "renewable energy" in prompt_result.messages[0].content.text
        
        # Step 2: Execute tool with prompt content
        mock_response = {
            "choices": [{
                "message": {
                    "content": "Renewable energy includes solar, wind, hydro..."
                }
            }],
            "model": "sonar"
        }
        
        with patch("mcp_server.perplexity_client.query", new_callable=AsyncMock) as mock_query:
            mock_query.return_value = mock_response
            
            result = await handle_call_tool(
                "query_perplexity",
                {"message": prompt_result.messages[0].content.text}
            )
            
            assert "Renewable energy" in result[0].text

    @pytest.mark.asyncio
    async def test_multiple_sequential_queries(self):
        """Test multiple sequential API calls in a session."""
        responses = [
            {
                "choices": [{"message": {"content": "First response"}}],
                "model": "sonar"
            },
            {
                "choices": [{"message": {"content": "Second response"}}],
                "model": "sonar"
            },
            {
                "choices": [{"message": {"content": "Third response"}}],
                "model": "sonar"
            }
        ]
        
        with patch("mcp_server.perplexity_client.query", new_callable=AsyncMock) as mock_query:
            mock_query.side_effect = responses
            
            # Execute three queries
            results = []
            for i in range(3):
                result = await handle_call_tool(
                    "query_perplexity",
                    {"message": f"Query {i+1}"}
                )
                results.append(result)
            
            assert len(results) == 3
            assert "First response" in results[0][0].text
            assert "Second response" in results[1][0].text
            assert "Third response" in results[2][0].text

    @pytest.mark.asyncio
    async def test_different_models_workflow(self):
        """Test workflow with different model selections."""
        models = ["sonar", "sonar-pro", "sonar-reasoning"]
        
        for model in models:
            mock_response = {
                "choices": [{
                    "message": {"content": f"Response from {model}"}
                }],
                "model": model
            }
            
            with patch("mcp_server.perplexity_client.query", new_callable=AsyncMock) as mock_query:
                mock_query.return_value = mock_response
                
                result = await handle_call_tool(
                    "query_perplexity",
                    {
                        "message": "Test query",
                        "model": model
                    }
                )
                
                assert f"Response from {model}" in result[0].text
                assert f"Model: {model}" in result[0].text

    @pytest.mark.asyncio
    async def test_error_recovery_workflow(self):
        """Test error handling and recovery in workflow."""
        with patch("mcp_server.perplexity_client.simple_query", new_callable=AsyncMock) as mock_query:
            # First call fails
            mock_query.side_effect = [
                Exception("Temporary network error"),
                "Successfully recovered"
            ]
            
            # First attempt fails
            result1 = await handle_call_tool(
                "search_perplexity",
                {"query": "test query"}
            )
            assert "Error" in result1[0].text
            
            # Second attempt succeeds
            result2 = await handle_call_tool(
                "search_perplexity",
                {"query": "test query"}
            )
            assert "Successfully recovered" in result2[0].text

    @pytest.mark.asyncio
    async def test_config_file_integration(self, tmp_path):
        """Test integration with config file loading."""
        # Create a temporary config file
        config_file = tmp_path / "config.txt"
        config_file.write_text("PERPLEXITY_API_KEY=file-based-key")
        
        # Clear environment variable and mock file access
        with patch.dict(os.environ, {}, clear=True):
            with patch("builtins.open", create=True) as mock_open:
                mock_open.return_value.__enter__.return_value.read.return_value = "PERPLEXITY_API_KEY=file-based-key"
                
                config = Config()
                assert config.perplexity_api_key == "file-based-key"

    @pytest.mark.asyncio
    async def test_health_check_integration(self):
        """Test health check workflow."""
        with patch("perplexity_client.config") as mock_config:
            mock_config.perplexity_base_url = "https://api.perplexity.ai"
            mock_config.perplexity_api_key = "test-key"
            mock_config.default_model = "sonar"
            mock_config.max_tokens = 1000
            mock_config.temperature = 0.7
            
            client = PerplexityClient()
            
            with patch.object(client, "simple_query", new_callable=AsyncMock) as mock_query:
                mock_query.return_value = "Hello response"
                
                is_healthy = await client.health_check()
                
                assert is_healthy is True
                mock_query.assert_called_once_with("Hello")

    @pytest.mark.asyncio
    async def test_temperature_and_tokens_integration(self):
        """Test integration with custom temperature and token settings."""
        test_cases = [
            {"temperature": 0.0, "max_tokens": 500},
            {"temperature": 0.5, "max_tokens": 1500},
            {"temperature": 1.0, "max_tokens": 2000}
        ]
        
        for params in test_cases:
            mock_response = {
                "choices": [{"message": {"content": "Test response"}}],
                "model": "sonar"
            }
            
            with patch("mcp_server.perplexity_client.query", new_callable=AsyncMock) as mock_query:
                mock_query.return_value = mock_response
                
                await handle_call_tool(
                    "query_perplexity",
                    {
                        "message": "Test",
                        "temperature": params["temperature"],
                        "max_tokens": params["max_tokens"]
                    }
                )
                
                call_kwargs = mock_query.call_args[1]
                assert call_kwargs["temperature"] == params["temperature"]
                assert call_kwargs["max_tokens"] == params["max_tokens"]

    @pytest.mark.asyncio
    async def test_system_message_integration(self):
        """Test system message integration across the stack."""
        system_messages = [
            "You are a helpful assistant",
            "Be concise and technical",
            "Explain like I'm five"
        ]
        
        for sys_msg in system_messages:
            mock_response = {
                "choices": [{"message": {"content": "Response"}}],
                "model": "sonar"
            }
            
            with patch("httpx.AsyncClient") as mock_client_class:
                mock_client = AsyncMock()
                mock_response_obj = MagicMock()
                mock_response_obj.json.return_value = mock_response
                mock_response_obj.raise_for_status = MagicMock()
                mock_client.post = AsyncMock(return_value=mock_response_obj)
                mock_client_class.return_value.__aenter__.return_value = mock_client
                
                await handle_call_tool(
                    "query_perplexity",
                    {
                        "message": "Test query",
                        "system_message": sys_msg
                    }
                )
                
                # Verify system message was included in request
                call_kwargs = mock_client.post.call_args[1]
                messages = call_kwargs["json"]["messages"]
                assert messages[0]["role"] == "system"
                assert messages[0]["content"] == sys_msg
                assert messages[1]["role"] == "user"

    @pytest.mark.asyncio
    async def test_all_prompts_integration(self):
        """Test integration of all prompt templates."""
        prompts = [
            ("research_topic", {"topic": "quantum physics"}),
            ("quick_fact_check", {"claim": "Python is a programming language"}),
            ("explain_concept", {"concept": "recursion", "level": "beginner"})
        ]
        
        for prompt_name, args in prompts:
            # Get the prompt
            prompt_result = await handle_get_prompt(prompt_name, args)
            
            assert isinstance(prompt_result, types.GetPromptResult)
            assert len(prompt_result.messages) > 0
            
            # Verify we could execute a tool with the prompt
            mock_response = {
                "choices": [{"message": {"content": "Prompt response"}}],
                "model": "sonar"
            }
            
            with patch("mcp_server.perplexity_client.query", new_callable=AsyncMock) as mock_query:
                mock_query.return_value = mock_response
                
                result = await handle_call_tool(
                    "query_perplexity",
                    {"message": prompt_result.messages[0].content.text}
                )
                
                assert len(result) == 1
                assert isinstance(result[0], types.TextContent)
