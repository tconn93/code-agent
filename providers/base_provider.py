"""
Base provider class for AI model abstraction.
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional


class BaseProvider(ABC):
    """
    Abstract base class for AI providers.
    Provides a common interface for different AI APIs (Anthropic, Gemini, Grok, Groq).
    """

    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model

    @abstractmethod
    def create_message(
        self,
        system: str,
        messages: List[Dict[str, Any]],
        tools: List[Dict[str, Any]],
        max_tokens: int = 4096
    ) -> Dict[str, Any]:
        """
        Create a message with the AI model.

        Args:
            system: System prompt
            messages: Conversation history
            tools: Available tools
            max_tokens: Maximum tokens to generate

        Returns:
            Response dict with standardized format:
            {
                "stop_reason": str,  # "end_turn", "tool_use", "max_tokens"
                "content": List[Dict],  # Content blocks
                "usage": Dict  # Token usage info
            }
        """
        pass

    @abstractmethod
    def format_tool_result(self, tool_use_id: str, result: str) -> Dict[str, Any]:
        """
        Format a tool result for the provider's API.

        Args:
            tool_use_id: ID of the tool use
            result: Tool execution result

        Returns:
            Formatted tool result
        """
        pass

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return the provider name."""
        pass

    @property
    @abstractmethod
    def supports_tools(self) -> bool:
        """Return whether this provider supports tool/function calling."""
        pass
