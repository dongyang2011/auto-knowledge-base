"""OpenAI implementation of unified LLM interface."""
import os
import openai
from typing import List, Optional, Dict

from .base import LLMBackend, ChatCompletionResponse


class OpenAIBackend(LLMBackend):
    """OpenAI API backend that supports all OpenAI chat models (GPT-3.5, GPT-4, etc)."""
    
    def __init__(
        self,
        api_key: str,
        default_model: str = "gpt-4o",
        base_url: Optional[str] = None,
    ):
        """
        Initialize OpenAI backend.
        
        Args:
            api_key: OpenAI API key
            default_model: Default model to use when not specified in chat call
            base_url: Optional custom base URL for API (for proxies or Azure)
        """
        # If base_url not provided, check environment variable OPENAI_BASE_URL
        if base_url is None:
            base_url = os.getenv("OPENAI_BASE_URL")
        self.client = openai.OpenAI(api_key=api_key, base_url=base_url)
        self.default_model = default_model
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.0,
    ) -> ChatCompletionResponse:
        """
        Chat completion via OpenAI API.
        
        Args:
            messages: List of messages in OpenAI format
            model: Override default model for this request
            temperature: Sampling temperature
        
        Returns:
            Standardized chat completion response
        """
        model_name = model if model is not None else self.default_model
        
        try:
            response = self.client.chat.completions.create(
                model=model_name,
                messages=messages,
                temperature=temperature,
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            return ChatCompletionResponse(
                content=content,
                model=model_name,
                success=True
            )
            
        except Exception as e:
            return ChatCompletionResponse(
                content=None,
                model=model_name,
                success=False,
                error_message=str(e)
            )
