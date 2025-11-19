"""
Architect Agent for system design and architecture review.
"""
from typing import Dict, List
from agents.base_agent import BaseAgent


class ArchitectAgent(BaseAgent):
    """
    Agent responsible for:
    - Creating system architecture designs
    - Reviewing architectural decisions
    - Creating technical specifications
    - Identifying design patterns and best practices
    - Planning component structure
    """

    @property
    def agent_name(self) -> str:
        return "ArchitectAgent"

    @property
    def agent_role(self) -> str:
        return "System Architecture & Design"

    def get_system_prompt(self) -> str:
        return """You are an expert Software Architect agent specializing in system design and architecture review.

Your responsibilities:
1. ARCHITECTURE DESIGN:
   - Design scalable, maintainable system architectures
   - Define component boundaries and interactions
   - Choose appropriate design patterns
   - Plan data models and database schemas
   - Define API contracts and interfaces

2. ARCHITECTURE REVIEW:
   - Evaluate existing codebases for architectural issues
   - Identify code smells, anti-patterns, and technical debt
   - Suggest refactoring strategies
   - Ensure SOLID principles and best practices
   - Review security architecture

3. TECHNICAL SPECIFICATIONS:
   - Create detailed technical specifications
   - Define file structure and module organization
   - Document architectural decisions (ADRs)
   - Plan integration points and dependencies

4. PLANNING:
   - Break down requirements into components
   - Identify required technologies and libraries
   - Plan development phases
   - Estimate complexity and risks

Output Format:
- Provide clear, actionable architecture documents
- Use diagrams and structured formats where helpful
- Document rationale for architectural decisions
- Identify potential issues and risks
- Create detailed technical specifications for implementation

You have access to read files, explore the codebase, and create architecture documents.
Be thorough, methodical, and consider scalability, maintainability, and security."""

    def get_tool_definitions(self) -> List[Dict]:
        """Return tools for architecture work."""
        base_tools = self.get_base_tools()

        # Add architecture-specific tools
        architecture_tools = [
            {
                "name": "create_architecture_doc",
                "description": "Create or update an architecture document",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "doc_name": {
                            "type": "string",
                            "description": "Name of the architecture document (e.g., 'system_design.md')"
                        },
                        "content": {
                            "type": "string",
                            "description": "Content of the architecture document"
                        }
                    },
                    "required": ["doc_name", "content"]
                }
            },
            {
                "name": "analyze_dependencies",
                "description": "Analyze project dependencies and their relationships",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "Path to analyze (default: root)"
                        }
                    }
                }
            }
        ]

        return base_tools + architecture_tools

    def process_tool_call(self, tool_name: str, tool_input: Dict):
        """Process tool calls including architecture-specific tools."""
        if tool_name == "create_architecture_doc":
            doc_path = f"/workspace/repo/docs/architecture/{tool_input['doc_name']}"
            # Ensure directory exists
            self.run_command("mkdir -p /workspace/repo/docs/architecture")
            success = self.write_file(doc_path, tool_input['content'])
            return f"Architecture document created at {doc_path}" if success else "Error creating document"

        elif tool_name == "analyze_dependencies":
            path = tool_input.get("path", ".")
            # Check for various dependency files
            dep_files = [
                "package.json",
                "requirements.txt",
                "go.mod",
                "Cargo.toml",
                "pom.xml",
                "build.gradle"
            ]

            results = []
            for dep_file in dep_files:
                file_result = self.run_command(f"cat {path}/{dep_file}")
                if file_result['exit_code'] == 0:
                    results.append(f"=== {dep_file} ===\n{file_result['stdout']}\n")

            return "\n".join(results) if results else "No dependency files found"

        # Fall back to base tools
        return super().process_tool_call(tool_name, tool_input)

    def review_architecture(self, repo_url: str = None, existing_workspace: str = None) -> Dict:
        """
        Perform architecture review of a codebase.

        Args:
            repo_url: Repository URL to review
            existing_workspace: Path to existing workspace

        Returns:
            Review results and recommendations
        """
        self.setup_sandbox(repo_url=repo_url, existing_workspace=existing_workspace)

        task = """Please perform a comprehensive architecture review of this codebase:

1. Explore the project structure and identify main components
2. Analyze the architecture and design patterns used
3. Identify strengths and potential issues
4. Review for:
   - Code organization and modularity
   - Separation of concerns
   - Design patterns usage
   - Scalability concerns
   - Security considerations
   - Technical debt
5. Create an architecture review document with findings and recommendations

Be thorough and provide actionable insights."""

        return self.run_agent(task)

    def design_system(self, requirements: str, existing_workspace: str = None) -> Dict:
        """
        Design a new system based on requirements.

        Args:
            requirements: System requirements and specifications
            existing_workspace: Path to workspace for creating design docs

        Returns:
            Design results and architecture documents
        """
        self.setup_sandbox(existing_workspace=existing_workspace)

        task = f"""Please design a system architecture based on these requirements:

{requirements}

Create comprehensive architecture documentation including:
1. System overview and high-level design
2. Component architecture and interactions
3. Data model and database schema
4. API design and contracts
5. Technology stack recommendations
6. File and module structure
7. Security considerations
8. Scalability and performance considerations
9. Implementation plan and phases

Create detailed architecture documents that can guide the implementation."""

        return self.run_agent(task)
