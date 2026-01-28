"""Shared OpenAI API client management."""

import os
import logging
from openai import OpenAI
from exceptions import APIError
from utils import retry
from constants import DEFAULT_MODEL
from dotenv import load_dotenv

# Load .env file
load_dotenv()

logger = logging.getLogger(__name__)

class APIClient:
    """Centralized API client."""
    
    _instance = None
    _client = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._client is None:
            self._initialize_client()
    
    def _initialize_client(self):
        """Initialize OpenAI client."""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise APIError("OPENAI_API_KEY not found. Set it in .env file or environment variables.")
        
        self._client = OpenAI(api_key=api_key)
        logger.info("API client initialized successfully")
    
    @retry(max_attempts=3, delay=1.0)
    def create_completion(self, messages: list, model: str = DEFAULT_MODEL, **kwargs):
        """Create chat completion."""
        try:
            response = self._client.chat.completions.create(
                model=model,
                messages=messages,
                **kwargs
            )
            return response
        except Exception as e:
            logger.error(f"API request failed: {e}")
            raise APIError(f"API request failed: {e}")
    
    @retry(max_attempts=3, delay=1.0)
    def create_embedding(self, text: str, model: str = "text-embedding-3-small"):
        """Create embedding."""
        try:
            response = self._client.embeddings.create(
                model=model,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Embedding request failed: {e}")
            raise APIError(f"Embedding request failed: {e}")
    
    def get_client(self):
        """Get raw client."""
        return self._client

def get_api_client() -> APIClient:
    """Get singleton API client."""
    return APIClient()
