import anthropic
import docker
import base64
import json
from pathlib import Path

class CodingAgent:
    def __init__(self, repo_url, task_description):
        self.client = anthropic.Anthropic(api_key="your-api-key")
        self.docker_client = docker.from_env()
        self.container = None
        self.repo_url = repo_url
        self.task = task_description
        self.conversation_history = []
        
    def setup_sandbox(self):
        """Create and setup sandbox container"""
        # Start container
        self.container = self.docker_client.containers.run(
            "coding-agent-sandbox",
            detach=True,
            remove=True,
            volumes={
                '/tmp/agent-workspace': {
                    'bind': '/workspace',
                    'mode': 'rw'
                }
            }
        )
        
        # Clone repository
        self.run_command(f"git clone {self.repo_url} /workspace/repo")
        self.run_command("cd /workspace/repo")
        
    def run_command(self, command):
        """Execute command in sandbox"""
        exec_result = self.container.exec_run(
            f"bash -c '{command}'",
            workdir="/workspace/repo"
        )
        return {
            "stdout": exec_result.output.decode('utf-8'),
            "exit_code": exec_result.exit_code
        }
    
    def read_file(self, filepath):
        """Read file from sandbox"""
        result = self.run_command(f"cat {filepath}")
        if result['exit_code'] == 0:
            return result['stdout']
        return f"Error reading file: {result['stdout']}"
    
    def write_file(self, filepath, content):
        """Write file to sandbox"""
        # Escape content for bash
        escaped_content = content.replace("'", "'\\''")
        result = self.run_command(f"cat > {filepath} << 'EOF'\n{content}\nEOF")
        return result['exit_code'] == 0
    
    def list_directory(self, path="."):
        """List directory structure"""
        result = self.run_command(f"find {path} -type f -o -type d | head -100")
        return result['stdout']
    
    def run_tests(self):
        """Run project tests"""
        # Try common test commands
        test_commands = [
            "npm test",
            "pytest",
            "python -m pytest",
            "python manage.py test",  # Django
            "go test ./...",
        ]
        
        results = []
        for cmd in test_commands:
            result = self.run_command(cmd)
            if result['exit_code'] != 127:  # Command exists
                results.append({
                    'command': cmd,
                    'output': result['stdout'],
                    'success': result['exit_code'] == 0
                })
                break
        
        return results
    
    def take_screenshot(self, url="http://localhost:3000"):
        """Take screenshot of running application"""
        screenshot_script = f"""
from playwright.sync_api import sync_playwright
import base64

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto('{url}')
    page.wait_for_timeout(2000)
    screenshot = page.screenshot()
    print(base64.b64encode(screenshot).decode())
    browser.close()
"""
        
        # Write script to container
        self.run_command(f"cat > /tmp/screenshot.py << 'EOF'\n{screenshot_script}\nEOF")
        result = self.run_command("python3 /tmp/screenshot.py")
        
        if result['exit_code'] == 0:
            return result['stdout'].strip()
        return None
    
    def start_dev_server(self):
        """Start development server in background"""
        # Common dev server commands
        start_commands = [
            "npm run dev &",
            "npm start &",
            "python manage.py runserver &",
            "python -m flask run &",
        ]
        
        for cmd in start_commands:
            self.run_command(cmd)
            # Give server time to start
            import time
            time.sleep(5)
            break
    
    def get_tool_definitions(self):
        """Define tools for Claude"""
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
            },
            {
                "name": "run_tests",
                "description": "Run the project's test suite",
                "input_schema": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "take_screenshot",
                "description": "Take screenshot of the running application UI",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "url": {
                            "type": "string",
                            "description": "URL to screenshot (default: http://localhost:3000)"
                        }
                    }
                }
            }
        ]
    
    def process_tool_call(self, tool_name, tool_input):
        """Execute tool and return result"""
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
        
        elif tool_name == "run_tests":
            results = self.run_tests()
            return json.dumps(results, indent=2)
        
        elif tool_name == "take_screenshot":
            url = tool_input.get("url", "http://localhost:3000")
            screenshot_b64 = self.take_screenshot(url)
            return screenshot_b64 if screenshot_b64 else "Failed to capture screenshot"
        
        return "Unknown tool"
    
    def run(self):
        """Main agent loop"""
        self.setup_sandbox()
        
        # Initial prompt with context
        system_prompt = f"""You are an expert coding agent. You have access to a sandboxed development environment.

Your task: {self.task}

Available tools:
- read_file: Read any file in the repository
- write_file: Create or modify files
- list_directory: Explore the project structure
- run_command: Execute bash commands (install deps, build, etc.)
- run_tests: Run the test suite
- take_screenshot: Capture UI screenshots for before/after comparison

Workflow:
1. Explore the project structure to understand the codebase
2. Read relevant files to understand current implementation
3. Make necessary code changes
4. Run tests to verify changes
5. Start the dev server and take screenshots to verify UI changes
6. If tests fail or UI doesn't match requirements, iterate

Be methodical and thorough. Always verify your changes work before completing."""

        # Start conversation
        messages = [{
            "role": "user",
            "content": f"Please complete this task: {self.task}\n\nStart by exploring the project structure."
        }]
        
        max_iterations = 20
        iteration = 0
        
        while iteration < max_iterations:
            iteration += 1
            print(f"\n=== Iteration {iteration} ===")
            
            # Call Claude
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4096,
                system=system_prompt,
                tools=self.get_tool_definitions(),
                messages=messages
            )
            
            print(f"Stop reason: {response.stop_reason}")
            
            # Process response
            if response.stop_reason == "end_turn":
                # Agent is done
                final_message = next(
                    (block.text for block in response.content if hasattr(block, "text")),
                    None
                )
                print(f"\n=== Agent Complete ===\n{final_message}")
                break
            
            elif response.stop_reason == "tool_use":
                # Process tool calls
                assistant_message = {"role": "assistant", "content": response.content}
                messages.append(assistant_message)
                
                tool_results = []
                
                for block in response.content:
                    if block.type == "tool_use":
                        print(f"Tool: {block.name}")
                        print(f"Input: {json.dumps(block.input, indent=2)}")
                        
                        # Execute tool
                        result = self.process_tool_call(block.name, block.input)
                        
                        # Handle screenshots specially (send as image)
                        if block.name == "take_screenshot" and result and result != "Failed to capture screenshot":
                            tool_results.append({
                                "type": "tool_result",
                                "tool_use_id": block.id,
                                "content": [
                                    {
                                        "type": "image",
                                        "source": {
                                            "type": "base64",
                                            "media_type": "image/png",
                                            "data": result
                                        }
                                    }
                                ]
                            })
                        else:
                            tool_results.append({
                                "type": "tool_result",
                                "tool_use_id": block.id,
                                "content": result[:5000]  # Limit output size
                            })
                        
                        print(f"Result preview: {str(result)[:200]}...")
                
                # Add tool results to conversation
                messages.append({
                    "role": "user",
                    "content": tool_results
                })
            
            else:
                print(f"Unexpected stop reason: {response.stop_reason}")
                break
        
        if iteration >= max_iterations:
            print("\n=== Max iterations reached ===")
        
        # Cleanup
        self.container.stop()
        
        return messages

# Usage
if __name__ == "__main__":
    agent = CodingAgent(
        repo_url="https://github.com/yourusername/your-project.git",
        task_description="Add a dark mode toggle button to the navbar. The button should persist the user's preference in localStorage and apply the dark theme across all pages."
    )
    
    conversation = agent.run()