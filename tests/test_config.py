"""Unit tests for config.py module."""

import os
import pytest
from unittest.mock import patch, mock_open
from config import Config


class TestConfig:
    """Unit tests for Config class."""

    def test_init_with_env_variable(self):
        """Test Config initialization with environment variable."""
        with patch.dict(os.environ, {"PERPLEXITY_API_KEY": "test-key-from-env"}):
            config = Config()
            assert config.perplexity_api_key == "test-key-from-env"
            assert config.perplexity_base_url == "https://api.perplexity.ai"
            assert config.default_model == "sonar"
            assert config.max_tokens == 1000
            assert config.temperature == 0.7

    def test_init_with_config_file_key_value_format(self):
        """Test Config initialization with config.txt file (key=value format)."""
        mock_file_content = "PERPLEXITY_API_KEY=test-key-from-file\n"
        
        with patch.dict(os.environ, {}, clear=True):
            with patch("builtins.open", mock_open(read_data=mock_file_content)):
                config = Config()
                assert config.perplexity_api_key == "test-key-from-file"

    def test_init_with_config_file_plain_format(self):
        """Test Config initialization with config.txt file (plain key format)."""
        mock_file_content = "test-plain-key-from-file"
        
        with patch.dict(os.environ, {}, clear=True):
            with patch("builtins.open", mock_open(read_data=mock_file_content)):
                config = Config()
                assert config.perplexity_api_key == "test-plain-key-from-file"

    def test_init_missing_api_key_file_not_found(self):
        """Test Config raises ValueError when config.txt is not found."""
        with patch.dict(os.environ, {}, clear=True):
            with patch("builtins.open", side_effect=FileNotFoundError()):
                with pytest.raises(ValueError, match="Perplexity API key not found"):
                    Config()

    def test_init_empty_api_key_from_env(self):
        """Test Config raises ValueError when environment variable is empty."""
        # Empty string env var is treated as not set, so it tries to load from file
        with patch.dict(os.environ, {"PERPLEXITY_API_KEY": ""}, clear=True):
            with patch("builtins.open", side_effect=FileNotFoundError()):
                with pytest.raises(ValueError, match="Perplexity API key not found"):
                    Config()

    def test_init_empty_api_key_from_file(self):
        """Test Config raises ValueError when config file contains empty key."""
        mock_file_content = ""
        
        with patch.dict(os.environ, {}, clear=True):
            with patch("builtins.open", mock_open(read_data=mock_file_content)):
                with pytest.raises(ValueError, match="Perplexity API key is empty"):
                    Config()

    def test_env_variable_takes_precedence_over_file(self):
        """Test that environment variable takes precedence over config file."""
        mock_file_content = "file-key"
        
        with patch.dict(os.environ, {"PERPLEXITY_API_KEY": "env-key"}):
            with patch("builtins.open", mock_open(read_data=mock_file_content)):
                config = Config()
                assert config.perplexity_api_key == "env-key"

    def test_config_file_multiline_key_value(self):
        """Test parsing config file with multiple lines."""
        mock_file_content = """# Comment line
OTHER_VAR=other_value
PERPLEXITY_API_KEY=correct-key
ANOTHER_VAR=another_value
"""
        
        with patch.dict(os.environ, {}, clear=True):
            with patch("builtins.open", mock_open(read_data=mock_file_content)):
                config = Config()
                assert config.perplexity_api_key == "correct-key"

    def test_config_default_values(self):
        """Test that default configuration values are set correctly."""
        with patch.dict(os.environ, {"PERPLEXITY_API_KEY": "test-key"}):
            config = Config()
            assert config.perplexity_base_url == "https://api.perplexity.ai"
            assert config.default_model == "sonar"
            assert config.max_tokens == 1000
            assert config.temperature == 0.7
