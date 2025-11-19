"""
Anthropic (Claude) provider implementation.
"""
import anthropic
from typing import Dict, List, Any
from providers.base_provider import BaseProvider


class AnthropicProvider(BaseProvider):
    """Provider for Anthropic's Claude models."""

    def __init__(self, api_key: str, model: str = "claude-sonnet-4-20250514"):
        super().__init__(api_key, model)
        self.client = anthropic.Anthropic(api_key=api_key)

    @property
    def provider_name(self) -> str:
        return "anthropic"

    @property
    def supports_tools(self) -> bool:
        return True

    def create_message(
        self,
        system: str,
        messages: List[Dict[str, Any]],
        tools: List[Dict[str, Any]],
        max_tokens: int = 4096
    ) -> Dict[str, Any]:
        """
        Create a message using Claude API.
        """
        response = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            system=system,
            tools=tools,
            messages=messages
        )

        return {
            "stop_reason": response.stop_reason,
            "content": response.content,
            "usage": {
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens
            }
        }

    def format_tool_result(self, tool_use_id: str, result: str) -> Dict[str, Any]:
        """Format tool result for Anthropic API."""
        return {
            "type": "tool_result",
            "tool_use_id": tool_use_id,
            "content": result
        }
