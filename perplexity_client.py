"""Perplexity AI API client module."""

import httpx
from typing import Optional, Dict, Any, List
from config import config


class PerplexityClient:
    """Client for interacting with Perplexity AI API."""
    
    def __init__(self):
        self.base_url = config.perplexity_base_url
        self.api_key = config.perplexity_api_key
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    async def query(
        self,
        message: str,
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        system_message: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send a query to Perplexity AI.
        
        Args:
            message: The user's question/prompt
            model: Model to use (default: from config)
            max_tokens: Maximum tokens in response (default: from config)
            temperature: Response randomness (default: from config)
            system_message: Optional system message to set context
            
        Returns:
            Dict containing the API response
            
        Raises:
            httpx.HTTPError: If the API request fails
        """
        # Use config defaults if not specified
        model = model or config.default_model
        max_tokens = max_tokens or config.max_tokens
        temperature = temperature or config.temperature
        
        # Build messages array
        messages = []
        if system_message:
            messages.append({"role": "system", "content": system_message})
        messages.append({"role": "user", "content": message})
        
        payload = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()
    
    async def simple_query(self, question: str) -> str:
        """
        Send a simple query and return just the text response.
        
        Args:
            question: The question to ask
            
        Returns:
            String containing the response text
        """
        response = await self.query(question)
        
        # Extract the response text from the API response
        if "choices" in response and len(response["choices"]) > 0:
            return response["choices"][0]["message"]["content"]
        else:
            raise ValueError("Unexpected response format from Perplexity API")
    
    async def health_check(self) -> bool:
        """
        Check if the Perplexity API is accessible with current credentials.
        
        Returns:
            True if the API is accessible, False otherwise
        """
        try:
            await self.simple_query("Hello")
            return True
        except Exception:
            return False


# Global client instance
perplexity_client = PerplexityClient()