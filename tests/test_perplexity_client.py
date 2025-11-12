"""Unit tests for perplexity_client.py module."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import httpx
from perplexity_client import PerplexityClient


class TestPerplexityClient:
    """Unit tests for PerplexityClient class."""

    @pytest.fixture
    def mock_config(self):
        """Mock config for testing."""
        with patch("perplexity_client.config") as mock:
            mock.perplexity_base_url = "https://api.perplexity.ai"
            mock.perplexity_api_key = "test-api-key"
            mock.default_model = "sonar"
            mock.max_tokens = 1000
            mock.temperature = 0.7
            yield mock

    @pytest.fixture
    def client(self, mock_config):
        """Create a PerplexityClient instance with mocked config."""
        return PerplexityClient()

    def test_client_initialization(self, client):
        """Test PerplexityClient initialization."""
        assert client.base_url == "https://api.perplexity.ai"
        assert client.api_key == "test-api-key"
        assert client.headers == {
            "Authorization": "Bearer test-api-key",
            "Content-Type": "application/json"
        }

    @pytest.mark.asyncio
    async def test_query_with_default_parameters(self, client):
        """Test query method with default parameters."""
        mock_response = {
            "choices": [
                {
                    "message": {
                        "content": "Test response"
                    }
                }
            ]
        }
        
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_response_obj = MagicMock()
            mock_response_obj.json.return_value = mock_response
            mock_response_obj.raise_for_status = MagicMock()
            mock_client.post = AsyncMock(return_value=mock_response_obj)
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            result = await client.query("Test question")
            
            assert result == mock_response
            mock_client.post.assert_called_once()
            call_kwargs = mock_client.post.call_args[1]
            assert call_kwargs["json"]["model"] == "sonar"
            assert call_kwargs["json"]["max_tokens"] == 1000
            assert call_kwargs["json"]["temperature"] == 0.7
            assert call_kwargs["json"]["messages"] == [
                {"role": "user", "content": "Test question"}
            ]

    @pytest.mark.asyncio
    async def test_query_with_custom_parameters(self, client):
        """Test query method with custom parameters."""
        mock_response = {"choices": [{"message": {"content": "Response"}}]}
        
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_response_obj = MagicMock()
            mock_response_obj.json.return_value = mock_response
            mock_response_obj.raise_for_status = MagicMock()
            mock_client.post = AsyncMock(return_value=mock_response_obj)
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            result = await client.query(
                message="Custom question",
                model="sonar-pro",
                max_tokens=2000,
                temperature=0.5,
                system_message="You are a helpful assistant"
            )
            
            assert result == mock_response
            call_kwargs = mock_client.post.call_args[1]
            assert call_kwargs["json"]["model"] == "sonar-pro"
            assert call_kwargs["json"]["max_tokens"] == 2000
            assert call_kwargs["json"]["temperature"] == 0.5
            assert call_kwargs["json"]["messages"] == [
                {"role": "system", "content": "You are a helpful assistant"},
                {"role": "user", "content": "Custom question"}
            ]

    @pytest.mark.asyncio
    async def test_query_with_system_message_only(self, client):
        """Test query method with system message but default other params."""
        mock_response = {"choices": [{"message": {"content": "Response"}}]}
        
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_response_obj = MagicMock()
            mock_response_obj.json.return_value = mock_response
            mock_response_obj.raise_for_status = MagicMock()
            mock_client.post = AsyncMock(return_value=mock_response_obj)
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            result = await client.query(
                message="Test",
                system_message="Be concise"
            )
            
            call_kwargs = mock_client.post.call_args[1]
            assert call_kwargs["json"]["messages"] == [
                {"role": "system", "content": "Be concise"},
                {"role": "user", "content": "Test"}
            ]

    @pytest.mark.asyncio
    async def test_query_http_error(self, client):
        """Test query method handles HTTP errors."""
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_response_obj = MagicMock()
            mock_response_obj.raise_for_status.side_effect = httpx.HTTPStatusError(
                "Error", request=MagicMock(), response=MagicMock()
            )
            mock_client.post = AsyncMock(return_value=mock_response_obj)
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            with pytest.raises(httpx.HTTPStatusError):
                await client.query("Test")

    @pytest.mark.asyncio
    async def test_simple_query_success(self, client):
        """Test simple_query method returns text response."""
        mock_response = {
            "choices": [
                {
                    "message": {
                        "content": "Simple answer"
                    }
                }
            ]
        }
        
        with patch.object(client, "query", new_callable=AsyncMock) as mock_query:
            mock_query.return_value = mock_response
            
            result = await client.simple_query("Simple question")
            
            assert result == "Simple answer"
            mock_query.assert_called_once_with("Simple question")

    @pytest.mark.asyncio
    async def test_simple_query_unexpected_format(self, client):
        """Test simple_query raises error on unexpected response format."""
        mock_response = {"unexpected": "format"}
        
        with patch.object(client, "query", new_callable=AsyncMock) as mock_query:
            mock_query.return_value = mock_response
            
            with pytest.raises(ValueError, match="Unexpected response format"):
                await client.simple_query("Question")

    @pytest.mark.asyncio
    async def test_simple_query_empty_choices(self, client):
        """Test simple_query raises error when choices array is empty."""
        mock_response = {"choices": []}
        
        with patch.object(client, "query", new_callable=AsyncMock) as mock_query:
            mock_query.return_value = mock_response
            
            with pytest.raises(ValueError, match="Unexpected response format"):
                await client.simple_query("Question")

    @pytest.mark.asyncio
    async def test_health_check_success(self, client):
        """Test health_check returns True on success."""
        with patch.object(client, "simple_query", new_callable=AsyncMock) as mock_query:
            mock_query.return_value = "Response"
            
            result = await client.health_check()
            
            assert result is True
            mock_query.assert_called_once_with("Hello")

    @pytest.mark.asyncio
    async def test_health_check_failure(self, client):
        """Test health_check returns False on exception."""
        with patch.object(client, "simple_query", new_callable=AsyncMock) as mock_query:
            mock_query.side_effect = Exception("API Error")
            
            result = await client.health_check()
            
            assert result is False

    @pytest.mark.asyncio
    async def test_query_timeout_configuration(self, client):
        """Test that query method uses correct timeout."""
        mock_response = {"choices": [{"message": {"content": "Response"}}]}
        
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_response_obj = MagicMock()
            mock_response_obj.json.return_value = mock_response
            mock_response_obj.raise_for_status = MagicMock()
            mock_client.post = AsyncMock(return_value=mock_response_obj)
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            await client.query("Test")
            
            call_kwargs = mock_client.post.call_args[1]
            assert call_kwargs["timeout"] == 30.0

    @pytest.mark.asyncio
    async def test_query_url_construction(self, client):
        """Test that query method constructs correct API URL."""
        mock_response = {"choices": [{"message": {"content": "Response"}}]}
        
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_response_obj = MagicMock()
            mock_response_obj.json.return_value = mock_response
            mock_response_obj.raise_for_status = MagicMock()
            mock_client.post = AsyncMock(return_value=mock_response_obj)
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            await client.query("Test")
            
            call_args = mock_client.post.call_args[0]
            assert call_args[0] == "https://api.perplexity.ai/chat/completions"
