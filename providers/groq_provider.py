"""
Groq provider implementation.
"""
from groq import Groq
from typing import Dict, List, Any
from providers.base_provider import BaseProvider
import json


class GroqProvider(BaseProvider):
    """Provider for Groq's fast inference models."""

    def __init__(self, api_key: str, model: str = "llama-3.3-70b-versatile"):
        super().__init__(api_key, model)
        self.client = Groq(api_key=api_key)

    @property
    def provider_name(self) -> str:
        return "groq"

    @property
    def supports_tools(self) -> bool:
        return True

    def _convert_tools_to_groq(self, tools: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Convert Anthropic-style tools to Groq function format."""
        groq_tools = []
        for tool in tools:
            groq_tools.append({
                "type": "function",
                "function": {
                    "name": tool["name"],
                    "description": tool["description"],
                    "parameters": tool["input_schema"]
                }
            })
        return groq_tools

    def _convert_messages_to_groq(self, system: str, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Convert Anthropic-style messages to Groq format."""
        groq_messages = []

        # Add system message first
        if system:
            groq_messages.append({
                "role": "system",
                "content": system
            })

        for msg in messages:
            role = msg["role"]
            content = msg["content"]

            # Handle different content types
            if isinstance(content, list):
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
                                    "arguments": json.dumps(block.get("input", {}))
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
                    groq_messages.append({
                        "role": "assistant",
                        "content": "\n".join(text_parts) if text_parts else None,
                        "tool_calls": tool_calls
                    })
                # Add tool results
                elif tool_results:
                    groq_messages.extend(tool_results)
                # Add regular text message
                elif text_parts:
                    groq_messages.append({
                        "role": role,
                        "content": "\n".join(text_parts)
                    })
            else:
                # Simple string content
                groq_messages.append({
                    "role": role,
                    "content": content
                })

        return groq_messages

    def create_message(
        self,
        system: str,
        messages: List[Dict[str, Any]],
        tools: List[Dict[str, Any]],
        max_tokens: int = 4096
    ) -> Dict[str, Any]:
        """
        Create a message using Groq API.
        """
        groq_messages = self._convert_messages_to_groq(system, messages)
        groq_tools = self._convert_tools_to_groq(tools) if tools else None

        response = self.client.chat.completions.create(
            model=self.model,
            messages=groq_messages,
            tools=groq_tools,
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
                try:
                    arguments = json.loads(tool_call.function.arguments) if tool_call.function.arguments else {}
                except json.JSONDecodeError:
                    arguments = {}

                content_blocks.append({
                    "type": "tool_use",
                    "id": tool_call.id,
                    "name": tool_call.function.name,
                    "input": arguments
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
        """Format tool result for Groq API."""
        return {
            "type": "tool_result",
            "tool_use_id": tool_use_id,
            "content": result
        }
