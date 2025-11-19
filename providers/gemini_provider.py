"""
Google Gemini provider implementation.
"""
import google.generativeai as genai
from typing import Dict, List, Any
from providers.base_provider import BaseProvider


class GeminiProvider(BaseProvider):
    """Provider for Google's Gemini models."""

    def __init__(self, api_key: str, model: str = "gemini-2.0-flash-exp"):
        super().__init__(api_key, model)
        genai.configure(api_key=api_key)
        self.client = genai.GenerativeModel(model)

    @property
    def provider_name(self) -> str:
        return "gemini"

    @property
    def supports_tools(self) -> bool:
        return True

    def _convert_tools_to_gemini(self, tools: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Convert Anthropic-style tools to Gemini function declarations."""
        gemini_tools = []
        for tool in tools:
            function_declaration = {
                "name": tool["name"],
                "description": tool["description"],
                "parameters": tool["input_schema"]
            }
            gemini_tools.append(function_declaration)
        return gemini_tools

    def _convert_messages_to_gemini(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Convert Anthropic-style messages to Gemini format."""
        gemini_messages = []
        for msg in messages:
            role = "user" if msg["role"] == "user" else "model"

            # Handle content that might be a list or string
            content = msg["content"]
            if isinstance(content, list):
                # Extract text from content blocks
                text_parts = []
                for block in content:
                    if isinstance(block, dict):
                        if block.get("type") == "text" or "text" in block:
                            text_parts.append(block.get("text", ""))
                        elif block.get("type") == "tool_result":
                            # Convert tool result to text
                            text_parts.append(f"Tool result: {block.get('content', '')}")
                    else:
                        text_parts.append(str(block))
                content = "\n".join(text_parts)

            gemini_messages.append({
                "role": role,
                "parts": [{"text": content}]
            })
        return gemini_messages

    def create_message(
        self,
        system: str,
        messages: List[Dict[str, Any]],
        tools: List[Dict[str, Any]],
        max_tokens: int = 4096
    ) -> Dict[str, Any]:
        """
        Create a message using Gemini API.
        """
        # Gemini handles system instructions separately
        gemini_messages = self._convert_messages_to_gemini(messages)
        gemini_tools = self._convert_tools_to_gemini(tools) if tools else None

        # Create chat session
        chat = self.client.start_chat(history=gemini_messages[:-1] if len(gemini_messages) > 1 else [])

        # Generate response
        generation_config = genai.GenerationConfig(
            max_output_tokens=max_tokens,
            temperature=1.0
        )

        # Get the last user message
        last_message = gemini_messages[-1]["parts"][0]["text"] if gemini_messages else ""

        # Add system instruction to the message if present
        if system:
            last_message = f"{system}\n\n{last_message}"

        response = chat.send_message(
            last_message,
            generation_config=generation_config,
            tools=gemini_tools
        )

        # Convert response to standardized format
        content_blocks = []
        stop_reason = "end_turn"

        # Check if response has function calls
        if hasattr(response, 'candidates') and response.candidates:
            candidate = response.candidates[0]
            if hasattr(candidate.content, 'parts'):
                for part in candidate.content.parts:
                    if hasattr(part, 'function_call') and part.function_call:
                        # Function call (tool use)
                        stop_reason = "tool_use"
                        content_blocks.append({
                            "type": "tool_use",
                            "id": f"gemini_{part.function_call.name}_{id(part)}",
                            "name": part.function_call.name,
                            "input": dict(part.function_call.args)
                        })
                    elif hasattr(part, 'text'):
                        # Text response
                        content_blocks.append({
                            "type": "text",
                            "text": part.text
                        })

        # Fallback to simple text if no parts found
        if not content_blocks:
            content_blocks.append({
                "type": "text",
                "text": response.text if hasattr(response, 'text') else ""
            })

        return {
            "stop_reason": stop_reason,
            "content": content_blocks,
            "usage": {
                "input_tokens": 0,  # Gemini doesn't provide token counts in the same way
                "output_tokens": 0
            }
        }

    def format_tool_result(self, tool_use_id: str, result: str) -> Dict[str, Any]:
        """Format tool result for Gemini API."""
        return {
            "type": "tool_result",
            "tool_use_id": tool_use_id,
            "content": result
        }
