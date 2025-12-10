"""
xAI Grok provider implementation.
"""
from openai import OpenAI
from typing import Dict, List, Any
from providers.base_provider import BaseProvider


class GrokProvider(BaseProvider):
    """Provider for xAI's Grok models."""

    def __init__(self, api_key: str, model: str = "grok-4-1-fast-reasoning"):
        super().__init__(api_key, model)
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.x.ai/v1"
        )

    @property
    def provider_name(self) -> str:
        return "grok"

    @property
    def supports_tools(self) -> bool:
        return True

    def _convert_tools_to_openai(self, tools: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Convert Anthropic-style tools to OpenAI function format."""
        openai_tools = []
        for tool in tools:
            openai_tools.append({
                "type": "function",
                "function": {
                    "name": tool["name"],
                    "description": tool["description"],
                    "parameters": tool["input_schema"]
                }
            })
        return openai_tools

    def _convert_messages_to_openai(self, system: str, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Convert Anthropic-style messages to OpenAI format."""
        openai_messages = []

        # Add system message first
        if system:
            openai_messages.append({
                "role": "system",
                "content": system
            })

        for msg in messages:
            role = msg["role"]
            content = msg["content"]

            # Handle different content types
            if isinstance(content, list):
                # Check for tool uses and tool results
                text_parts = []
                tool_calls = []
                tool_results = []

                for block in content:
                    if isinstance(block, dict):
                        if block.get("type") == "text" or "text" in block:
                            text_parts.append(block.get("text", ""))
                        elif block.get("type") == "tool_use":
                            tool_calls.append({
                                "id": block.get("id", ""),
                                "type": "function",
                                "function": {
                                    "name": block.get("name", ""),
                                    "arguments": str(block.get("input", {}))
                                }
                            })
                        elif block.get("type") == "tool_result":
                            tool_results.append({
                                "role": "tool",
                                "content": block.get("content", ""),
                                "tool_call_id": block.get("tool_use_id", "")
                            })

                # Add assistant message with tool calls if present
                if tool_calls:
                    openai_messages.append({
                        "role": "assistant",
                        "content": "\n".join(text_parts) if text_parts else None,
                        "tool_calls": tool_calls
                    })
                # Add tool results
                elif tool_results:
                    openai_messages.extend(tool_results)
                # Add regular text message
                elif text_parts:
                    openai_messages.append({
                        "role": role,
                        "content": "\n".join(text_parts)
                    })
            else:
                # Simple string content
                openai_messages.append({
                    "role": role,
                    "content": content
                })

        return openai_messages

    def create_message(
        self,
        system: str,
        messages: List[Dict[str, Any]],
        tools: List[Dict[str, Any]],
        max_tokens: int = 4096
    ) -> Dict[str, Any]:
        """
        Create a message using Grok API (OpenAI-compatible).
        """
        openai_messages = self._convert_messages_to_openai(system, messages)
        openai_tools = self._convert_tools_to_openai(tools) if tools else None

        response = self.client.chat.completions.create(
            model=self.model,
            messages=openai_messages,
            tools=openai_tools,
            max_tokens=max_tokens
        )

        # Convert response to standardized format
        choice = response.choices[0]
        content_blocks = []
        stop_reason = "end_turn"

        # Check for tool calls
        if choice.message.tool_calls:
            stop_reason = "tool_use"
            for tool_call in choice.message.tool_calls:
                content_blocks.append({
                    "type": "tool_use",
                    "id": tool_call.id,
                    "name": tool_call.function.name,
                    "input": eval(tool_call.function.arguments) if tool_call.function.arguments else {}
                })

        # Add text content
        if choice.message.content:
            content_blocks.append({
                "type": "text",
                "text": choice.message.content
            })

        # Check finish reason
        if choice.finish_reason == "length":
            stop_reason = "max_tokens"

        return {
            "stop_reason": stop_reason,
            "content": content_blocks,
            "usage": {
                "input_tokens": response.usage.prompt_tokens,
                "output_tokens": response.usage.completion_tokens
            }
        }

    def format_tool_result(self, tool_use_id: str, result: str) -> Dict[str, Any]:
        """Format tool result for Grok API."""
        return {
            "type": "tool_result",
            "tool_use_id": tool_use_id,
            "content": result
        }
