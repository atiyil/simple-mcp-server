"""Configuration management for Perplexity AI microservice."""

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

class Config:
    """Configuration class for the Perplexity AI service."""
    
    def __init__(self):
        self.perplexity_api_key = self._load_api_key()
        self.perplexity_base_url = "https://api.perplexity.ai"
        self.default_model = "sonar"  # Updated to current model name
        self.max_tokens = 1000
        self.temperature = 0.7
    
    def _load_api_key(self) -> str:
        """Load Perplexity API key from config file or environment variable."""
        # First try to load from environment variable
        api_key = os.getenv("PERPLEXITY_API_KEY")
        
        if not api_key:
            # Try to load from config.txt file
            try:
                with open("config.txt", "r") as f:
                    content = f.read().strip()
                    # Support both plain key and key=value format
                    if "=" in content:
                        for line in content.split("\n"):
                            if line.strip().startswith("PERPLEXITY_API_KEY"):
                                api_key = line.split("=", 1)[1].strip()
                                break
                    else:
                        api_key = content
            except FileNotFoundError:
                raise ValueError("Perplexity API key not found. Please set PERPLEXITY_API_KEY environment variable or create config.txt file.")
        
        if not api_key:
            raise ValueError("Perplexity API key is empty. Please provide a valid API key.")
        
        return api_key

# Global config instance
config = Config()