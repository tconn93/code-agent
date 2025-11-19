# AI Agent Software Development Pipeline

A comprehensive multi-agent system for autonomous software development, powered by Claude AI. This system orchestrates specialized AI agents through a complete development pipeline from architecture design to deployment and monitoring.

## 🚀 Overview

This project provides a production-ready pipeline of AI agents that can:

- **Design** system architecture and technical specifications
- **Implement** features and fix bugs
- **Test** code comprehensively with unit, integration, and e2e tests
- **Deploy** applications to various environments
- **Monitor** system health and performance

Each agent operates in an isolated Docker sandbox, ensuring safe execution while maintaining the ability to share artifacts through a common workspace.

## 🏗️ Architecture

```
Requirements → Architect → Coding → Testing → Deployment → Monitoring
                  ↓          ↓         ↓          ↓            ↓
              Design Docs  Code    Tests      Deploy      Health Checks
```

### Specialized Agents

1. **ArchitectAgent**: System design, architecture review, technical specifications
2. **CodingAgent**: Feature implementation, code review, bug fixes
3. **TestingAgent**: Test creation, QA, coverage analysis, security scans
4. **DeploymentAgent**: Build, package, deploy to environments, CI/CD
5. **MonitoringAgent**: Health checks, log analysis, performance monitoring

### Pipeline Orchestrator

Coordinates agent workflows with three execution modes:
- **Full Pipeline**: Complete development workflow from requirements to monitoring
- **Partial Pipeline**: Run specific stages (e.g., just coding + testing)
- **Code Review**: Architecture review + code review + QA

## 📋 Prerequisites

- **Python 3.8+**
- **Docker Engine 20.10+**
- **Anthropic API Key** ([Get one here](https://console.anthropic.com/))
- **Git**

### System Requirements
- **Minimum**: 4 CPU cores, 8GB RAM, 50GB storage
- **Recommended**: 8 CPU cores, 16GB RAM, 100GB SSD

## 🚀 Quick Start

### 1. Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd code-agent

# Install Python dependencies
pip install -r requirements.txt

# Build the Docker sandbox image
docker build -t coding-agent-sandbox .
```

### 2. Configuration

```bash
# Create default configuration
python main.py init

# Edit config.json and add your Anthropic API key
# OR set environment variable
export ANTHROPIC_API_KEY="your-api-key-here"
```

### 3. Run Your First Pipeline

```bash
# Run full development pipeline
python main.py run --requirements "Create a REST API for a todo app with user authentication"

# Results will be saved to ./pipeline_output/
```

## 💡 Usage Examples

### Full Pipeline

```bash
python main.py run --requirements "Build a microservice for user authentication with JWT tokens"
```

### Specific Stages

```bash
# Create tasks.json
echo '{
  "coding": "Implement JWT authentication middleware",
  "testing": "Create unit and integration tests for auth"
}' > tasks.json

python main.py run-stages --stages coding testing --tasks tasks.json
```

### Code Review

```bash
python main.py review --repo-url https://github.com/user/repo \
  --focus security performance "test coverage"
```

### Programmatic Usage

```python
from config import Settings
from pipelines import PipelineOrchestrator

# Initialize
settings = Settings.from_env()
orchestrator = PipelineOrchestrator(
    api_key=settings.anthropic_api_key,
    workspace_path=settings.workspace_path
)

# Run full pipeline
result = orchestrator.run_full_pipeline(
    requirements="Your project requirements here",
    output_dir="./output"
)

print(f"Status: {result['status']}")
print(f"Completed stages: {result['stages_completed']}")
```

### Individual Agent Usage

```python
from agents import CodingAgent, TestingAgent

# Use Coding Agent
with CodingAgent(api_key) as coder:
    coder.setup_sandbox(repo_url="https://github.com/user/repo")
    result = coder.implement_feature(
        feature_spec="Add dark mode toggle to the UI"
    )

# Use Testing Agent
with TestingAgent(api_key) as tester:
    tester.setup_sandbox(repo_url="https://github.com/user/repo")
    result = tester.run_qa_suite()
```

## 📁 Project Structure

```
code-agent/
├── agents/                    # Specialized AI agents
│   ├── base_agent.py         # Abstract base class
│   ├── architect_agent.py    # Architecture & design
│   ├── coding_agent.py       # Implementation & review
│   ├── testing_agent.py      # Testing & QA
│   ├── deployment_agent.py   # Deployment & DevOps
│   └── monitoring_agent.py   # Monitoring & observability
├── pipelines/                 # Orchestration
│   └── orchestrator.py       # Pipeline coordinator
├── config/                    # Configuration management
│   └── settings.py           # Settings and config loading
├── examples/                  # Usage examples
│   └── example_usage.py      # Example scripts
├── Dockerfile                 # Sandbox container definition
├── main.py                   # CLI entry point
├── requirements.txt          # Python dependencies
├── README.md                 # This file
├── CLAUDE.md                 # Development guide
└── DEPLOYMENT.md             # Deployment strategies
```

## ⚙️ Configuration

Configuration can be provided via:

1. **JSON file** (highest priority):
```json
{
  "anthropic_api_key": "your-key",
  "anthropic_model": "claude-sonnet-4-20250514",
  "workspace_path": "/tmp/agent-workspace",
  "max_iterations": 20
}
```

2. **Environment variables**:
```bash
export ANTHROPIC_API_KEY="your-key"
export ANTHROPIC_MODEL="claude-sonnet-4-20250514"
export WORKSPACE_PATH="/tmp/agent-workspace"
export MAX_ITERATIONS="20"
```

3. **Programmatic**:
```python
from config import Settings

settings = Settings(
    anthropic_api_key="your-key",
    anthropic_model="claude-sonnet-4-20250514"
)
```

## 🚢 Deployment

This system can be deployed in multiple ways:

### Local Development
```bash
python main.py run --requirements "..."
```

### Docker
```bash
docker build -t ai-agent-pipeline .
docker run -v /var/run/docker.sock:/var/run/docker.sock \
  -e ANTHROPIC_API_KEY="your-key" \
  ai-agent-pipeline run --requirements "..."
```

### Docker Compose
```bash
docker-compose up -d
```

### Kubernetes
```bash
kubectl apply -f k8s/
```

For comprehensive deployment strategies including cloud deployments (AWS, GCP, Azure), CI/CD integration, and scaling, see **[DEPLOYMENT.md](DEPLOYMENT.md)**.

## 🔧 Advanced Features

### Shared Workspace

Agents share a workspace to pass artifacts:
```python
orchestrator = PipelineOrchestrator(
    api_key=api_key,
    workspace_path="/shared/workspace"  # Same path for all agents
)
```

### Pipeline State Tracking

Monitor pipeline progress:
```python
result = orchestrator.run_full_pipeline(requirements="...")

print(result["status"])           # "completed", "failed", "running"
print(result["current_stage"])    # Current stage or None
print(result["stages_completed"]) # List of completed stages
print(result["results"])          # Results from each stage
```

### Custom Agent Tools

Extend agents with custom tools:
```python
class CustomCodingAgent(CodingAgent):
    def get_tool_definitions(self):
        base_tools = super().get_tool_definitions()
        custom_tools = [
            {
                "name": "my_custom_tool",
                "description": "Does something custom",
                "input_schema": {...}
            }
        ]
        return base_tools + custom_tools

    def process_tool_call(self, tool_name, tool_input):
        if tool_name == "my_custom_tool":
            return self.my_custom_implementation(tool_input)
        return super().process_tool_call(tool_name, tool_input)
```

## 🔒 Security Considerations

- **API Keys**: Never commit API keys. Use environment variables or secrets management.
- **Sandbox Isolation**: Each agent runs in an isolated Docker container with limited privileges.
- **Code Review**: All agent-generated code should be reviewed before production deployment.
- **Resource Limits**: Configure Docker resource limits to prevent resource exhaustion.
- **Network Isolation**: Use Docker networks to isolate sandboxes.

## 📊 Monitoring & Observability

Track pipeline performance:
- Pipeline execution time per stage
- Agent success/failure rates
- API token usage and costs
- Resource usage (CPU, memory, disk)

Logs are structured and can be aggregated with ELK stack, CloudWatch, or similar tools.

## 🤝 Contributing

This is a personal project, but suggestions and feedback are welcome!

## 📝 License

See [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Powered by [Claude AI](https://www.anthropic.com/claude) from Anthropic
- Built with Docker for sandboxed execution
- Uses Playwright for UI verification

## 📚 Documentation

- **[CLAUDE.md](CLAUDE.md)**: Developer guide for working with this codebase
- **[DEPLOYMENT.md](DEPLOYMENT.md)**: Comprehensive deployment strategies and guides
- **[examples/](examples/)**: Example usage scripts

## 🐛 Troubleshooting

### Docker Permission Denied
```bash
sudo usermod -aG docker $USER
# Log out and back in
```

### API Rate Limits
- Monitor usage in Anthropic Console
- Adjust `max_iterations` in config to reduce token usage
- Implement retry logic with exponential backoff

### Container Cleanup
```bash
# Remove stopped containers
docker container prune

# Remove all agent containers
docker ps -a | grep coding-agent-sandbox | awk '{print $1}' | xargs docker rm
```

## 📞 Support

For issues or questions:
1. Check the [CLAUDE.md](CLAUDE.md) for implementation details
2. Review [DEPLOYMENT.md](DEPLOYMENT.md) for deployment issues
3. Check Docker and Python logs for errors
4. Verify Anthropic API key and quota

---

**Built with ❤️ using Claude AI**
