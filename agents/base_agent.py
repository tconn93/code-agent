"""
Base Agent class providing common functionality for all specialized agents.
"""
import docker
import json
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from pathlib import Path
from providers import (
    BaseProvider,
    AnthropicProvider,
    GeminiProvider,
    GrokProvider,
    GroqProvider,
    OpenAIProvider
)


class BaseAgent(ABC):
    """
    Abstract base class for all agents in the pipeline.
    Provides common functionality for Docker management, Claude API interaction,
    and tool execution.
    """

    def __init__(self, api_key: str, workspace_path: str = "/tmp/agent-workspace",
             provider: str = "anthropic", model: str = "claude-sonnet-4-20250514"):
        """
        Initialize base agent.

        Args:
            api_key: API key for the provider
            workspace_path: Path to shared workspace
            provider: AI provider name (anthropic, gemini, grok, groq)
            model: Model name for the provider
        """
        self.docker_client = docker.from_env()
        self.container = None
        self.workspace_path = workspace_path
        self.conversation_history = []
        self.agent_state = {}

        # Create provider instance
        self.provider = self._create_provider(provider, api_key, model)

        # Configurable settings (can be overridden after initialization)
        self.model = model
        self.max_iterations = 20
        self.output_truncate_length = 5000
        self.docker_image = "coding-agent-sandbox"

    def _create_provider(self, provider_name: str, api_key: str, model: str) -> BaseProvider:
        """Create the appropriate provider instance."""
        providers = {
            "anthropic": AnthropicProvider,
            "gemini": GeminiProvider,
            "xai": GrokProvider,
            "groq": GroqProvider,
            "openai": OpenAIProvider
        }

        provider_class = providers.get(provider_name.lower())
        if not provider_class:
            raise ValueError(f"Unknown provider: {provider_name}. Supported providers: {list(providers.keys())}")

        return provider_class(api_key=api_key, model=model)

    @property
    @abstractmethod
    def agent_name(self) -> str:
        """Return the name of this agent."""
        pass

    @property
    @abstractmethod
    def agent_role(self) -> str:
        """Return a description of this agent's role."""
        pass

    @abstractmethod
    def get_system_prompt(self) -> str:
        """Return the system prompt for this agent."""
        pass

    @abstractmethod
    def get_tool_definitions(self) -> List[Dict]:
        """Return tool definitions specific to this agent."""
        pass

    def setup_sandbox(self, repo_url: Optional[str] = None,
                     existing_workspace: Optional[str] = None):
        """
        Create and setup sandbox container.

        Args:
            repo_url: Git repository URL to clone (optional)
            existing_workspace: Path to existing workspace to mount (optional)
        """
        workspace_mount = existing_workspace or self.workspace_path

        self.container = self.docker_client.containers.run(
            self.docker_image,
            detach=True,
            remove=True,
            volumes={
                workspace_mount: {
                    'bind': '/workspace',
                    'mode': 'rw'
                }
            },
            network_mode="bridge"
        )

        if repo_url:
            self.run_command(f"git clone {repo_url} /workspace/repo")
            self.run_command("cd /workspace/repo")

    def run_command(self, command: str, workdir: str = "/workspace/repo") -> Dict:
        """Execute command in sandbox."""
        if not self.container:
            raise RuntimeError("Container not initialized. Call setup_sandbox() first.")

        exec_result = self.container.exec_run(
            f"bash -c '{command}'",
            workdir=workdir
        )
        return {
            "stdout": exec_result.output.decode('utf-8'),
            "exit_code": exec_result.exit_code
        }

    def read_file(self, filepath: str) -> str:
        """Read file from sandbox."""
        result = self.run_command(f"cat {filepath}")
        if result['exit_code'] == 0:
            return result['stdout']
        return f"Error reading file: {result['stdout']}"

    def write_file(self, filepath: str, content: str) -> bool:
        """Write file to sandbox."""
        escaped_content = content.replace("'", "'\\''")
        result = self.run_command(f"cat > {filepath} << 'EOF'\n{content}\nEOF")
        return result['exit_code'] == 0

    def list_directory(self, path: str = ".") -> str:
        """List directory structure."""
        result = self.run_command(f"find {path} -type f -o -type d | head -100")
        return result['stdout']

    def get_base_tools(self) -> List[Dict]:
        """Return common tools available to all agents."""
        return [
            {
                "name": "read_file",
                "description": "Read contents of a file in the repository",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "filepath": {
                            "type": "string",
                            "description": "Path to file relative to repo root"
                        }
                    },
                    "required": ["filepath"]
                }
            },
            {
                "name": "write_file",
                "description": "Write or modify a file in the repository",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "filepath": {
                            "type": "string",
                            "description": "Path to file relative to repo root"
                        },
                        "content": {
                            "type": "string",
                            "description": "Full content to write to file"
                        }
                    },
                    "required": ["filepath", "content"]
                }
            },
            {
                "name": "list_directory",
                "description": "List files and directories",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "Path to list (default: current directory)"
                        }
                    }
                }
            },
            {
                "name": "run_command",
                "description": "Execute a bash command in the repository",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "command": {
                            "type": "string",
                            "description": "Bash command to execute"
                        }
                    },
                    "required": ["command"]
                }
            }
        ]

    def process_tool_call(self, tool_name: str, tool_input: Dict) -> Any:
        """Execute tool and return result. Can be overridden by subclasses."""
        if tool_name == "read_file":
            return self.read_file(tool_input["filepath"])

        elif tool_name == "write_file":
            success = self.write_file(tool_input["filepath"], tool_input["content"])
            return f"File written successfully" if success else "Error writing file"

        elif tool_name == "list_directory":
            path = tool_input.get("path", ".")
            return self.list_directory(path)

        elif tool_name == "run_command":
            result = self.run_command(tool_input["command"])
            return f"Exit code: {result['exit_code']}\n{result['stdout']}"

        return "Unknown tool"

    def run_agent(self, task: str, max_iterations: int = None,
                  model: str = None) -> Dict:
        """
        Main agent execution loop.

        Args:
            task: Task description for the agent
            max_iterations: Maximum number of conversation iterations (uses instance default if None)
            model: Claude model to use (uses instance default if None)

        Returns:
            Dictionary containing conversation history and final state
        """
        # Use instance defaults if not specified
        max_iterations = max_iterations or self.max_iterations
        model = model or self.model

        system_prompt = self.get_system_prompt()
        tools = self.get_tool_definitions()

        messages = [{
            "role": "user",
            "content": task
        }]

        iteration = 0

        while iteration < max_iterations:
            iteration += 1
            print(f"\n[{self.agent_name}] Iteration {iteration}/{max_iterations}")
            print(f"[{self.agent_name}] Using provider: {self.provider.provider_name}, model: {model}")

            # Call AI provider
            response = self.provider.create_message(
                system=system_prompt,
                messages=messages,
                tools=tools,
                max_tokens=4096
            )

            print(f"[{self.agent_name}] Stop reason: {response['stop_reason']}")

            # Process response
            if response["stop_reason"] == "end_turn":
                # Extract text from content blocks
                final_message = None
                for block in response["content"]:
                    if isinstance(block, dict) and block.get("type") == "text":
                        final_message = block.get("text")
                        break
                    elif hasattr(block, "text"):
                        final_message = block.text
                        break

                print(f"\n[{self.agent_name}] Task Complete")

                return {
                    "status": "completed",
                    "messages": messages,
                    "final_response": final_message,
                    "iterations": iteration,
                    "usage": response.get("usage", {})
                }

            elif response["stop_reason"] == "tool_use":
                # Process tool calls
                assistant_message = {"role": "assistant", "content": response["content"]}
                messages.append(assistant_message)

                tool_results = []

                for block in response["content"]:
                    # Handle both dict and object formats
                    if isinstance(block, dict):
                        if block.get("type") == "tool_use":
                            tool_name = block.get("name", "")
                            tool_input = block.get("input", {})
                            tool_id = block.get("id", "")

                            print(f"[{self.agent_name}] Tool: {tool_name}")

                            result = self.process_tool_call(tool_name, tool_input)

                            tool_results.append(
                                self.provider.format_tool_result(
                                    tool_id,
                                    str(result)[:self.output_truncate_length]
                                )
                            )
                    elif hasattr(block, "type") and block.type == "tool_use":
                        print(f"[{self.agent_name}] Tool: {block.name}")

                        result = self.process_tool_call(block.name, block.input)

                        tool_results.append(
                            self.provider.format_tool_result(
                                block.id,
                                str(result)[:self.output_truncate_length]
                            )
                        )

                messages.append({
                    "role": "user",
                    "content": tool_results
                })

            else:
                print(f"[{self.agent_name}] Unexpected stop reason: {response['stop_reason']}")
                return {
                    "status": "error",
                    "messages": messages,
                    "error": f"Unexpected stop reason: {response['stop_reason']}",
                    "iterations": iteration
                }

        return {
            "status": "max_iterations",
            "messages": messages,
            "iterations": iteration
        }

    def cleanup(self):
        """Cleanup resources."""
        if self.container:
            try:
                self.container.stop()
            except:
                pass

    def __enter__(self):
        """Context manager support."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager cleanup."""
        self.cleanup()
