"""
Deployment Agent for automating deployment processes.
"""
from typing import Dict, List
from agents.base_agent import BaseAgent


class DeploymentAgent(BaseAgent):
    """
    Agent responsible for:
    - Creating deployment configurations
    - Building and packaging applications
    - Deploying to various environments
    - Managing CI/CD pipelines
    - Infrastructure as Code
    """

    def __init__(self, api_key: str = None, provider: str = None, model: str = None,
                 docker_image: str = "coding-agent-sandbox",
                 max_iterations: int = 20, output_truncate_length: int = 5000):
        """
        Initialize DeploymentAgent.
        """
        super().__init__(api_key, provider, model, docker_image, max_iterations, output_truncate_length)

    @property
    def agent_name(self) -> str:
        return "DeploymentAgent"

    @property
    def agent_role(self) -> str:
        return "Deployment & DevOps"

    def get_system_prompt(self) -> str:
        return f"""You are an expert DevOps Engineer agent specializing in deployment automation.

Your responsibilities:
1. DEPLOYMENT CONFIGURATION:
   - Create Dockerfile and docker-compose configurations
   - Set up Kubernetes manifests and Helm charts
   - Configure CI/CD pipelines (GitHub Actions, GitLab CI, Jenkins)
   - Manage environment variables and secrets
   - Create deployment scripts

2. BUILD & PACKAGE:
   - Build Docker images
   - Create application bundles
   - Optimize build processes
   - Manage dependencies
   - Version artifacts

3. DEPLOYMENT EXECUTION:
   - Deploy to development, staging, production environments
   - Perform rolling updates
   - Handle database migrations
   - Manage configuration changes
   - Execute smoke tests post-deployment

4. INFRASTRUCTURE AS CODE:
   - Create Terraform configurations
   - Write CloudFormation templates
   - Set up infrastructure provisioning
   - Manage cloud resources (AWS, GCP, Azure)

5. CI/CD PIPELINE:
   - Design automated pipelines
   - Set up automated testing in pipelines
   - Configure deployment gates
   - Implement rollback strategies
   - Set up artifact storage

Best Practices:
- Use infrastructure as code
- Implement blue-green or canary deployments
- Automate everything
- Use environment-specific configurations
- Secure secrets and credentials
- Implement health checks
- Enable easy rollbacks
- Log all deployment activities
- Use container orchestration
- Implement monitoring and alerting

You have access to read/write files, run commands, and manage deployments.
Be careful with production deployments and always verify changes."""

    def get_tool_definitions(self) -> List[Dict]:
        """Return tools for deployment work."""
        base_tools = self.get_base_tools()

        deployment_tools = [
            {
                "name": "build_docker_image",
                "description": "Build a Docker image",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "tag": {
                            "type": "string",
                            "description": "Image tag (e.g., 'myapp:v1.0.0')"
                        },
                        "dockerfile_path": {
                            "type": "string",
                            "description": "Path to Dockerfile (default: ./Dockerfile)"
                        },
                        "build_args": {
                            "type": "string",
                            "description": "Build arguments as JSON object"
                        }
                    },
                    "required": ["tag"]
                }
            },
            {
                "name": "run_build",
                "description": "Run application build process",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "build_command": {
                            "type": "string",
                            "description": "Custom build command (will auto-detect if not provided)"
                        }
                    }
                }
            },
            {
                "name": "deploy_to_environment",
                "description": "Deploy application to an environment",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "environment": {
                            "type": "string",
                            "description": "Target environment (dev, staging, production)"
                        },
                        "deployment_method": {
                            "type": "string",
                            "description": "Deployment method (docker-compose, kubernetes, script)"
                        }
                    },
                    "required": ["environment"]
                }
            },
            {
                "name": "run_migrations",
                "description": "Run database migrations",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "direction": {
                            "type": "string",
                            "description": "Migration direction (up, down, status)"
                        }
                    }
                }
            },
            {
                "name": "health_check",
                "description": "Perform health check on deployed service",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "endpoint": {
                            "type": "string",
                            "description": "Health check endpoint URL"
                        }
                    },
                    "required": ["endpoint"]
                }
            }
        ]

        return base_tools + deployment_tools

    def build_docker_image(self, tag: str, dockerfile_path: str = "./Dockerfile",
                          build_args: str = None) -> str:
        """Build Docker image."""
        cmd = f"docker build -t {tag}"

        if build_args:
            for arg in build_args.split():
                cmd += f" --build-arg {arg}"

        cmd += f" -f {dockerfile_path} ."

        result = self.run_command(cmd)
        return f"Build command: {cmd}\nExit code: {result['exit_code']}\n\n{result['stdout']}"

    def run_build(self, build_command: str = None) -> str:
        """Run application build."""
        if build_command:
            result = self.run_command(build_command)
            return f"Exit code: {result['exit_code']}\n{result['stdout']}"

        # Auto-detect build command
        build_commands = [
            "npm run build",
            "npm run compile",
            "python setup.py build",
            "go build",
            "cargo build --release",
            "mvn package",
            "gradle build",
        ]

        for cmd in build_commands:
            check = self.run_command(f"which {cmd.split()[0]}")
            if check['exit_code'] == 0:
                result = self.run_command(cmd)
                return f"Build command: {cmd}\nExit code: {result['exit_code']}\n\n{result['stdout']}"

        return "No build command detected"

    def deploy_to_environment(self, environment: str,
                             deployment_method: str = "docker-compose") -> str:
        """Deploy to environment."""
        if deployment_method == "docker-compose":
            compose_file = f"docker-compose.{environment}.yml"
            # Check if compose file exists
            check = self.run_command(f"test -f {compose_file}")
            if check['exit_code'] == 0:
                result = self.run_command(f"docker-compose -f {compose_file} up -d")
                return f"Deployment to {environment}\n{result['stdout']}"
            else:
                result = self.run_command("docker-compose up -d")
                return f"Deployment to {environment} (default compose)\n{result['stdout']}"

        elif deployment_method == "kubernetes":
            result = self.run_command(f"kubectl apply -f k8s/{environment}/")
            return f"Kubernetes deployment to {environment}\n{result['stdout']}"

        elif deployment_method == "script":
            script = f"scripts/deploy-{environment}.sh"
            check = self.run_command(f"test -f {script}")
            if check['exit_code'] == 0:
                result = self.run_command(f"bash {script}")
                return f"Script deployment to {environment}\n{result['stdout']}"

        return f"Unknown deployment method: {deployment_method}"

    def run_migrations(self, direction: str = "up") -> str:
        """Run database migrations."""
        migration_commands = [
            f"npm run migrate:{direction}",
            f"python manage.py migrate",
            f"alembic upgrade head" if direction == "up" else "alembic downgrade -1",
            f"goose {direction}",
        ]

        for cmd in migration_commands:
            check = self.run_command(f"which {cmd.split()[0]}")
            if check['exit_code'] == 0:
                result = self.run_command(cmd)
                return f"Migration command: {cmd}\n{result['stdout']}"

        return "No migration tool detected"

    def health_check(self, endpoint: str) -> str:
        """Perform health check."""
        result = self.run_command(f"curl -f {endpoint}")
        if result['exit_code'] == 0:
            return f"Health check PASSED for {endpoint}\n{result['stdout']}"
        else:
            return f"Health check FAILED for {endpoint}\n{result['stdout']}"

    def process_tool_call(self, tool_name: str, tool_input: Dict):
        """Process deployment-specific tool calls."""
        if tool_name == "build_docker_image":
            return self.build_docker_image(
                tag=tool_input["tag"],
                dockerfile_path=tool_input.get("dockerfile_path", "./Dockerfile"),
                build_args=tool_input.get("build_args")
            )

        elif tool_name == "run_build":
            return self.run_build(tool_input.get("build_command"))

        elif tool_name == "deploy_to_environment":
            return self.deploy_to_environment(
                environment=tool_input["environment"],
                deployment_method=tool_input.get("deployment_method", "docker-compose")
            )

        elif tool_name == "run_migrations":
            return self.run_migrations(tool_input.get("direction", "up"))

        elif tool_name == "health_check":
            return self.health_check(tool_input["endpoint"])

        return super().process_tool_call(tool_name, tool_input)

    def setup_deployment(self, platform: str, repo_url: str = None,
                        existing_workspace: str = None) -> Dict:
        """
        Set up deployment infrastructure.

        Args:
            platform: Target platform (docker, kubernetes, aws, etc.)
            repo_url: Repository URL
            existing_workspace: Path to existing workspace

        Returns:
            Setup results
        """
        self.setup_sandbox(repo_url=repo_url, existing_workspace=existing_workspace)

        task = f"""Set up deployment infrastructure for {platform}:

1. Analyze the application to understand deployment requirements
2. Create appropriate deployment configurations:
   - Dockerfile (if needed)
   - docker-compose.yml for local/dev
   - Kubernetes manifests (if applicable)
   - CI/CD pipeline configuration
3. Create deployment scripts for different environments
4. Set up environment variable templates
5. Create deployment documentation
6. Test the deployment process

Provide deployment configurations and documentation."""

        return self.run_agent(task)

    def execute_deployment(self, environment: str, repo_url: str = None,
                          existing_workspace: str = None) -> Dict:
        """
        Execute deployment to an environment.

        Args:
            environment: Target environment (dev, staging, production)
            repo_url: Repository URL
            existing_workspace: Path to existing workspace

        Returns:
            Deployment results
        """
        self.setup_sandbox(repo_url=repo_url, existing_workspace=existing_workspace)

        task = f"""Deploy the application to {environment}:

1. Run the build process
2. Run all tests to ensure code is ready
3. Run database migrations (if needed)
4. Deploy the application
5. Perform health checks
6. Verify the deployment
7. Document the deployment

Provide deployment status and verification results."""

        return self.run_agent(task)
