"""
Coding Agent for implementation and code review.
"""
import base64
from typing import Dict, List
from agents.base_agent import BaseAgent


class CodingAgent(BaseAgent):
    """
    Agent responsible for:
    - Implementing features based on specifications
    - Writing clean, maintainable code
    - Code review and refactoring
    - Bug fixes
    - Taking UI screenshots for verification
    """

    @property
    def agent_name(self) -> str:
        return "CodingAgent"

    @property
    def agent_role(self) -> str:
        return "Implementation & Code Review"

    def get_system_prompt(self) -> str:
        return """You are an expert Software Engineer agent specializing in implementation and code review.

Your responsibilities:
1. IMPLEMENTATION:
   - Write clean, maintainable, well-documented code
   - Follow established patterns and conventions
   - Implement features according to specifications
   - Handle edge cases and error conditions
   - Write efficient, performant code

2. CODE REVIEW:
   - Review code for quality, correctness, and maintainability
   - Identify bugs, security issues, and code smells
   - Suggest improvements and refactoring
   - Ensure code follows best practices
   - Check for proper error handling

3. REFACTORING:
   - Improve code structure without changing behavior
   - Reduce complexity and technical debt
   - Extract reusable components
   - Improve naming and readability

4. BUG FIXES:
   - Diagnose and fix bugs
   - Write regression tests
   - Verify fixes work correctly

5. UI VERIFICATION:
   - Take screenshots to verify UI changes
   - Compare before/after states
   - Ensure responsive design

Best Practices:
- Write self-documenting code with clear names
- Keep functions small and focused
- Follow DRY (Don't Repeat Yourself)
- Handle errors gracefully
- Consider security implications
- Optimize for readability first, performance second
- Write code that's easy to test

You have access to read/write files, run commands, and take screenshots.
Be methodical, test your changes, and verify everything works."""

    def get_tool_definitions(self) -> List[Dict]:
        """Return tools for coding work."""
        base_tools = self.get_base_tools()

        # Add coding-specific tools
        coding_tools = [
            {
                "name": "run_tests",
                "description": "Run the project's test suite",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "test_path": {
                            "type": "string",
                            "description": "Specific test file or directory to run (optional)"
                        }
                    }
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
            },
            {
                "name": "start_dev_server",
                "description": "Start the development server in the background",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "command": {
                            "type": "string",
                            "description": "Custom start command (optional, will auto-detect if not provided)"
                        }
                    }
                }
            },
            {
                "name": "lint_code",
                "description": "Run linter on code",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "Path to lint (optional, defaults to all)"
                        }
                    }
                }
            }
        ]

        return base_tools + coding_tools

    def run_tests(self, test_path: str = None) -> List[Dict]:
        """Run project tests."""
        test_commands = [
            "npm test",
            "pytest",
            "python -m pytest",
            "python manage.py test",
            "go test ./...",
            "cargo test",
        ]

        if test_path:
            # Try to run specific test
            for base_cmd in test_commands:
                result = self.run_command(f"{base_cmd} {test_path}")
                if result['exit_code'] != 127:
                    return [{
                        'command': f"{base_cmd} {test_path}",
                        'output': result['stdout'],
                        'success': result['exit_code'] == 0
                    }]

        # Run all tests
        for cmd in test_commands:
            result = self.run_command(cmd)
            if result['exit_code'] != 127:
                return [{
                    'command': cmd,
                    'output': result['stdout'],
                    'success': result['exit_code'] == 0
                }]

        return [{"error": "No test framework detected"}]

    def take_screenshot(self, url: str = "http://localhost:3000") -> str:
        """Take screenshot of running application."""
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
        self.run_command(f"cat > /tmp/screenshot.py << 'EOF'\n{screenshot_script}\nEOF")
        result = self.run_command("python3 /tmp/screenshot.py")

        if result['exit_code'] == 0:
            return result['stdout'].strip()
        return None

    def start_dev_server(self, command: str = None):
        """Start development server in background."""
        if command:
            self.run_command(f"{command} &")
            return f"Started dev server with: {command}"

        start_commands = [
            "npm run dev &",
            "npm start &",
            "python manage.py runserver &",
            "python -m flask run &",
            "go run main.go &",
        ]

        for cmd in start_commands:
            # Check if command exists
            check_cmd = cmd.split()[0]
            check_result = self.run_command(f"which {check_cmd}")
            if check_result['exit_code'] == 0:
                self.run_command(cmd)
                import time
                time.sleep(3)
                return f"Started dev server with: {cmd}"

        return "Could not detect dev server command"

    def lint_code(self, path: str = ".") -> str:
        """Run code linter."""
        lint_commands = [
            f"eslint {path}",
            f"pylint {path}",
            f"flake8 {path}",
            f"golangci-lint run {path}",
        ]

        results = []
        for cmd in lint_commands:
            result = self.run_command(cmd)
            if result['exit_code'] != 127:
                results.append(f"=== {cmd} ===\n{result['stdout']}\n")

        return "\n".join(results) if results else "No linters found"

    def process_tool_call(self, tool_name: str, tool_input: Dict):
        """Process tool calls including coding-specific tools."""
        if tool_name == "run_tests":
            test_path = tool_input.get("test_path")
            results = self.run_tests(test_path)
            return str(results)

        elif tool_name == "take_screenshot":
            url = tool_input.get("url", "http://localhost:3000")
            screenshot_b64 = self.take_screenshot(url)
            return screenshot_b64 if screenshot_b64 else "Failed to capture screenshot"

        elif tool_name == "start_dev_server":
            command = tool_input.get("command")
            return self.start_dev_server(command)

        elif tool_name == "lint_code":
            path = tool_input.get("path", ".")
            return self.lint_code(path)

        return super().process_tool_call(tool_name, tool_input)

    def implement_feature(self, feature_spec: str, repo_url: str = None,
                         existing_workspace: str = None) -> Dict:
        """
        Implement a feature based on specifications.

        Args:
            feature_spec: Feature specification and requirements
            repo_url: Repository URL
            existing_workspace: Path to existing workspace

        Returns:
            Implementation results
        """
        self.setup_sandbox(repo_url=repo_url, existing_workspace=existing_workspace)

        task = f"""Please implement the following feature:

{feature_spec}

Follow this workflow:
1. Explore the codebase to understand the current structure
2. Identify the files that need to be modified or created
3. Implement the feature following best practices
4. Run tests to verify the implementation
5. If there are UI changes, start the dev server and take screenshots
6. Fix any issues found during testing

Provide a summary of changes made and verification results."""

        return self.run_agent(task)

    def review_code(self, repo_url: str = None, existing_workspace: str = None,
                   focus_areas: List[str] = None) -> Dict:
        """
        Perform code review.

        Args:
            repo_url: Repository URL
            existing_workspace: Path to existing workspace
            focus_areas: Specific areas to focus on (optional)

        Returns:
            Review results
        """
        self.setup_sandbox(repo_url=repo_url, existing_workspace=existing_workspace)

        focus = "\n".join(f"- {area}" for area in focus_areas) if focus_areas else "all aspects"

        task = f"""Please perform a comprehensive code review focusing on:
{focus}

Review for:
1. Code quality and maintainability
2. Bugs and potential issues
3. Security vulnerabilities
4. Performance concerns
5. Best practices adherence
6. Test coverage
7. Documentation

Provide specific, actionable feedback with file names and line numbers where applicable."""

        return self.run_agent(task)
