"""Abstract base class for unified LLM interface following OpenAI chat format."""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional, Dict


@dataclass
class ChatCompletionResponse:
    """Standard response format matching OpenAI chat completion."""
    content: Optional[str]
    model: str
    success: bool = True
    error_message: Optional[str] = None


class LLMBackend(ABC):
    """Abstract base class for LLM backends, following OpenAI chat completion API style."""
    
    @abstractmethod
    def chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.0,
    ) -> ChatCompletionResponse:
        """
        Unified chat completion interface following OpenAI format.
        
        Args:
            messages: List of message dictionaries in OpenAI format:
                [{"role": "system"|"user"|"assistant", "content": "text"}, ...]
            model: Model identifier (optional, uses backend default if not provided)
            temperature: Sampling temperature (0.0 is deterministic)
        
        Returns:
            ChatCompletionResponse with standardized output format
        """
        pass
