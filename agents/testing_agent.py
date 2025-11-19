"""
Testing Agent for test creation, execution, and quality assurance.
"""
from typing import Dict, List
from agents.base_agent import BaseAgent


class TestingAgent(BaseAgent):
    """
    Agent responsible for:
    - Writing comprehensive tests (unit, integration, e2e)
    - Running test suites
    - Analyzing test coverage
    - Performance testing
    - Security testing
    """

    @property
    def agent_name(self) -> str:
        return "TestingAgent"

    @property
    def agent_role(self) -> str:
        return "Testing & Quality Assurance"

    def get_system_prompt(self) -> str:
        return """You are an expert QA Engineer agent specializing in comprehensive testing.

Your responsibilities:
1. TEST CREATION:
   - Write unit tests for individual functions/methods
   - Create integration tests for component interactions
   - Develop end-to-end tests for user workflows
   - Write edge case and error handling tests
   - Create performance and load tests
   - Implement security tests

2. TEST EXECUTION:
   - Run test suites and analyze results
   - Debug failing tests
   - Identify flaky tests
   - Generate test reports
   - Track test coverage

3. TEST STRATEGY:
   - Design comprehensive test plans
   - Identify critical test scenarios
   - Determine appropriate test types (unit, integration, e2e)
   - Plan test data and fixtures
   - Define acceptance criteria

4. QUALITY ASSURANCE:
   - Verify functionality meets requirements
   - Check for regressions
   - Validate error messages and edge cases
   - Test accessibility
   - Verify security measures

5. COVERAGE ANALYSIS:
   - Measure code coverage
   - Identify untested code paths
   - Suggest tests for uncovered areas
   - Track coverage trends

Testing Best Practices:
- Write tests that are independent and isolated
- Use descriptive test names that explain what is being tested
- Follow AAA pattern: Arrange, Act, Assert
- Test one thing per test
- Use appropriate assertions
- Mock external dependencies
- Keep tests fast and deterministic
- Test both happy paths and error cases

You have access to read/write files, run commands, and execute tests.
Be thorough and ensure comprehensive test coverage."""

    def get_tool_definitions(self) -> List[Dict]:
        """Return tools for testing work."""
        base_tools = self.get_base_tools()

        testing_tools = [
            {
                "name": "run_tests",
                "description": "Run tests with various options",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "test_path": {
                            "type": "string",
                            "description": "Specific test file/directory to run"
                        },
                        "pattern": {
                            "type": "string",
                            "description": "Test name pattern to match"
                        },
                        "verbose": {
                            "type": "boolean",
                            "description": "Enable verbose output"
                        }
                    }
                }
            },
            {
                "name": "run_coverage",
                "description": "Run tests with coverage analysis",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "output_format": {
                            "type": "string",
                            "description": "Coverage report format (html, xml, json, text)"
                        }
                    }
                }
            },
            {
                "name": "run_linter",
                "description": "Run code linters and static analysis",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "Path to lint"
                        }
                    }
                }
            },
            {
                "name": "run_security_scan",
                "description": "Run security vulnerability scan",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "scan_type": {
                            "type": "string",
                            "description": "Type of scan (dependencies, code, all)"
                        }
                    }
                }
            },
            {
                "name": "run_performance_test",
                "description": "Run performance benchmarks",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "test_path": {
                            "type": "string",
                            "description": "Path to performance tests"
                        }
                    }
                }
            }
        ]

        return base_tools + testing_tools

    def run_tests(self, test_path: str = None, pattern: str = None,
                  verbose: bool = False) -> str:
        """Run tests with options."""
        test_frameworks = [
            ("npm test", "-- "),
            ("pytest", " "),
            ("python -m pytest", " "),
            ("go test", " "),
            ("cargo test", " "),
        ]

        for base_cmd, separator in test_frameworks:
            # Build command with options
            cmd_parts = [base_cmd]

            if test_path:
                cmd_parts.append(test_path)

            if pattern:
                if "pytest" in base_cmd:
                    cmd_parts.append(f"-k {pattern}")
                elif "npm" in base_cmd:
                    cmd_parts.append(f"{separator}--grep {pattern}")

            if verbose:
                if "pytest" in base_cmd:
                    cmd_parts.append("-v")
                elif "npm" in base_cmd:
                    cmd_parts.append(f"{separator}--verbose")

            cmd = " ".join(cmd_parts)
            result = self.run_command(cmd)

            if result['exit_code'] != 127:  # Command found
                return f"Command: {cmd}\nExit Code: {result['exit_code']}\n\n{result['stdout']}"

        return "No test framework detected"

    def run_coverage(self, output_format: str = "text") -> str:
        """Run tests with coverage analysis."""
        coverage_commands = [
            f"pytest --cov --cov-report={output_format}",
            f"python -m pytest --cov --cov-report={output_format}",
            "npm test -- --coverage",
            "go test -cover ./...",
        ]

        for cmd in coverage_commands:
            result = self.run_command(cmd)
            if result['exit_code'] != 127:
                return f"Command: {cmd}\n\n{result['stdout']}"

        return "No coverage tool detected"

    def run_linter(self, path: str = ".") -> str:
        """Run code linters."""
        linters = [
            f"eslint {path}",
            f"pylint {path}",
            f"flake8 {path}",
            f"black --check {path}",
            f"golangci-lint run {path}",
            f"cargo clippy",
        ]

        results = []
        for cmd in linters:
            result = self.run_command(cmd)
            if result['exit_code'] != 127:
                results.append(f"=== {cmd} ===\nExit Code: {result['exit_code']}\n{result['stdout']}\n")

        return "\n".join(results) if results else "No linters found"

    def run_security_scan(self, scan_type: str = "all") -> str:
        """Run security scans."""
        scans = []

        if scan_type in ["dependencies", "all"]:
            scans.extend([
                "npm audit",
                "pip-audit",
                "safety check",
                "cargo audit",
            ])

        if scan_type in ["code", "all"]:
            scans.extend([
                "bandit -r .",
                "semgrep --config=auto .",
            ])

        results = []
        for cmd in scans:
            result = self.run_command(cmd)
            if result['exit_code'] != 127:
                results.append(f"=== {cmd} ===\nExit Code: {result['exit_code']}\n{result['stdout']}\n")

        return "\n".join(results) if results else "No security tools found"

    def run_performance_test(self, test_path: str = None) -> str:
        """Run performance tests."""
        perf_commands = [
            f"pytest --benchmark {test_path or ''}",
            f"npm run benchmark",
            f"go test -bench=. {test_path or './...'}",
        ]

        for cmd in perf_commands:
            result = self.run_command(cmd)
            if result['exit_code'] != 127:
                return f"Command: {cmd}\n\n{result['stdout']}"

        return "No performance testing framework detected"

    def process_tool_call(self, tool_name: str, tool_input: Dict):
        """Process testing-specific tool calls."""
        if tool_name == "run_tests":
            return self.run_tests(
                test_path=tool_input.get("test_path"),
                pattern=tool_input.get("pattern"),
                verbose=tool_input.get("verbose", False)
            )

        elif tool_name == "run_coverage":
            return self.run_coverage(tool_input.get("output_format", "text"))

        elif tool_name == "run_linter":
            return self.run_linter(tool_input.get("path", "."))

        elif tool_name == "run_security_scan":
            return self.run_security_scan(tool_input.get("scan_type", "all"))

        elif tool_name == "run_performance_test":
            return self.run_performance_test(tool_input.get("test_path"))

        return super().process_tool_call(tool_name, tool_input)

    def create_tests(self, spec: str, repo_url: str = None,
                    existing_workspace: str = None) -> Dict:
        """
        Create comprehensive tests based on specification.

        Args:
            spec: Testing requirements and specifications
            repo_url: Repository URL
            existing_workspace: Path to existing workspace

        Returns:
            Test creation results
        """
        self.setup_sandbox(repo_url=repo_url, existing_workspace=existing_workspace)

        task = f"""Create comprehensive tests based on these requirements:

{spec}

Please:
1. Analyze the codebase to understand what needs testing
2. Identify critical test scenarios
3. Write unit tests for individual components
4. Write integration tests for component interactions
5. Create end-to-end tests for key workflows
6. Include edge cases and error handling tests
7. Run the tests to verify they work
8. Generate a coverage report

Provide a summary of tests created and coverage achieved."""

        return self.run_agent(task)

    def run_qa_suite(self, repo_url: str = None, existing_workspace: str = None) -> Dict:
        """
        Run comprehensive QA suite.

        Args:
            repo_url: Repository URL
            existing_workspace: Path to existing workspace

        Returns:
            QA results
        """
        self.setup_sandbox(repo_url=repo_url, existing_workspace=existing_workspace)

        task = """Run a comprehensive QA suite:

1. Run all tests and report results
2. Generate coverage report and identify gaps
3. Run linters and static analysis
4. Perform security vulnerability scan
5. Check for performance regressions
6. Review test quality and suggest improvements

Provide a detailed QA report with:
- Test results summary
- Coverage metrics
- Security issues found
- Performance metrics
- Recommendations for improvement"""

        return self.run_agent(task)
