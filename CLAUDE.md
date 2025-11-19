# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **multi-agent software development pipeline** that uses Claude's API to autonomously complete end-to-end software development workflows. The system coordinates five specialized agents (Architect, Coding, Testing, Deployment, Monitoring) through a pipeline orchestrator, with each agent operating in isolated Docker sandboxes.

## Architecture

### High-Level System Design

The system follows a **multi-agent pipeline architecture**:

```
Requirements → Architect → Coding → Testing → Deployment → Monitoring
                  ↓          ↓         ↓          ↓            ↓
              Design Docs  Code    Tests      Deploy      Health Checks
```

Each stage is handled by a specialized agent that can run independently or as part of the full pipeline.

### Core Components

**BaseAgent** (`agents/base_agent.py`): Abstract base class providing:
- Docker sandbox management
- Claude API interaction loop
- Common tools (read_file, write_file, list_directory, run_command)
- Context manager support for resource cleanup
- Configurable iteration limits and output truncation

**Specialized Agents** (all inherit from `BaseAgent`):

1. **ArchitectAgent** (`agents/architect_agent.py`):
   - System architecture design and review
   - Creates technical specifications and ADRs
   - Analyzes dependencies and design patterns
   - Additional tools: `create_architecture_doc`, `analyze_dependencies`

2. **CodingAgent** (`agents/coding_agent.py`):
   - Feature implementation and code review
   - Bug fixing and refactoring
   - UI verification via screenshots
   - Additional tools: `run_tests`, `take_screenshot`, `start_dev_server`, `lint_code`

3. **TestingAgent** (`agents/testing_agent.py`):
   - Test creation (unit, integration, e2e)
   - Coverage analysis and QA
   - Security scanning and linting
   - Additional tools: `run_tests`, `run_coverage`, `run_linter`, `run_security_scan`, `run_performance_test`

4. **DeploymentAgent** (`agents/deployment_agent.py`):
   - Deployment configuration creation
   - Build and packaging
   - Environment deployment (dev/staging/prod)
   - Additional tools: `build_docker_image`, `run_build`, `deploy_to_environment`, `run_migrations`, `health_check`

5. **MonitoringAgent** (`agents/monitoring_agent.py`):
   - Monitoring setup and configuration
   - Health checks and log analysis
   - Performance monitoring and alerting
   - Additional tools: `check_health`, `check_logs`, `check_resources`, `check_process`, `analyze_metrics`, `test_alert`

**PipelineOrchestrator** (`pipelines/orchestrator.py`):
- Coordinates workflow across all agents
- Manages pipeline state and results
- Provides three execution modes:
  - `run_full_pipeline()`: Complete development workflow
  - `run_partial_pipeline()`: Specific stages only
  - `run_code_review_pipeline()`: Architecture + Code + QA review
- Saves intermediate results and state to disk
- Implements shared workspace across agents

**Configuration System** (`config/settings.py`):
- Centralized settings management
- Supports environment variables, JSON files, or programmatic config
- Priority: config file → ./config.json → environment variables
- Settings include API keys, Docker config, agent parameters, and defaults
- **Multi-provider support**: Use Anthropic, Gemini, Grok, or Groq models
- Per-agent provider and model configuration for cost optimization
- See [CONFIG.md](./CONFIG.md) and [CONFIG_MULTI_PROVIDER.md](./CONFIG_MULTI_PROVIDER.md) for comprehensive configuration guides

**Provider System** (`providers/`):
- Abstract base provider interface for multi-AI-provider support
- Provider implementations: Anthropic, Gemini, Grok, Groq
- Standardized message format across all providers
- Automatic provider selection based on agent configuration

### Docker Sandbox

**Image**: `coding-agent-sandbox` (defined in `Dockerfile`)
- Ubuntu 22.04 base
- Git, Python 3, Node.js/npm, Chromium, curl
- Playwright pre-installed for screenshots
- Workspace mounted at `/workspace` from configurable host path

**Isolation**: Each agent instance runs in a disposable container (`remove=True`). Agents can share a workspace by mounting the same host directory, enabling artifact passing between pipeline stages.

## Development Commands

### Setup and Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt

# Build the Docker sandbox image
docker build -t coding-agent-sandbox .

# Create default configuration
python main.py init
# Edit config.json and add your Anthropic API key
# See CONFIG.md for detailed configuration options
```

### Running the Pipeline

**Full pipeline**:
```bash
export ANTHROPIC_API_KEY="your-key"
python main.py run --requirements "Build a REST API for task management"
```

**Specific stages**:
```bash
# Create tasks.json with stage-specific task descriptions
python main.py run-stages --stages coding testing --tasks tasks.json
```

**Code review**:
```bash
python main.py review --repo-url https://github.com/user/repo --focus security performance
```

**Programmatic usage**:
```python
from config import Settings
from pipelines import PipelineOrchestrator

settings = Settings.from_env()
orchestrator = PipelineOrchestrator(
    api_key=settings.anthropic_api_key,
    workspace_path=settings.workspace_path
)

result = orchestrator.run_full_pipeline(
    requirements="Your requirements here",
    output_dir="./output"
)
```

**Individual agents**:
```python
from agents import CodingAgent

with CodingAgent(api_key) as agent:
    agent.setup_sandbox(repo_url="https://github.com/user/repo")
    result = agent.implement_feature("Add dark mode toggle")
```

### Testing

```bash
# Test Docker connectivity
python -c "import docker; print(docker.from_env().ping())"

# Test sandbox
docker run --rm coding-agent-sandbox echo "Sandbox OK"

# Run example usage
python examples/example_usage.py
```

## Key Implementation Details

### Agent Communication Pattern

Agents don't communicate directly. They share context through:
1. **Shared workspace**: Files written by one agent are available to the next
2. **Pipeline state**: `pipeline_state.json` tracks progress and results
3. **Architecture docs**: Architect creates specs that Coding agent reads
4. **Code artifacts**: Coding agent creates code that Testing agent validates

### Tool Execution Flow

1. Agent receives task description
2. Agent constructs system prompt with role and responsibilities
3. Claude API called with tools and messages
4. For each `tool_use` response:
   - Agent executes tool via `process_tool_call()`
   - Result returned to Claude as `tool_result`
5. Loop continues until `end_turn` or max iterations
6. Results and conversation history returned

### Configuration Priority

1. Explicit config file path passed to `load_config()`
2. `./config.json` in current directory
3. Environment variables (`ANTHROPIC_API_KEY`, etc.)

### Workspace Management

- Default: `/tmp/agent-workspace` on host
- Mounted to `/workspace` in containers
- Working directory: `/workspace/repo` (if repo cloned)
- Persists across agent invocations in same pipeline
- Cleaned up manually or via container removal

### State Persistence

Pipeline state saved to `{output_dir}/pipeline_state.json` after each stage:
```json
{
  "status": "running",
  "current_stage": "testing",
  "stages_completed": ["architecture", "coding"],
  "results": { ... },
  "errors": [],
  "started_at": "2025-11-19T12:00:00",
  "completed_at": null
}
```

### Error Handling

- Agents wrapped in context managers for cleanup
- Pipeline catches exceptions and marks status as "failed"
- Errors appended to `pipeline_state.errors`
- State saved even on failure for debugging

## Important Constraints

- **Container Lifecycle**: Containers are ephemeral. Extract artifacts before cleanup.
- **Output Truncation**: Tool results limited to 5000 characters (configurable via `Settings.output_truncate_length`)
- **Iteration Limits**: Default 20 iterations per agent (configurable via `Settings.max_iterations`)
- **API Costs**: Full pipeline can consume significant API tokens; monitor usage
- **Docker Socket**: Requires access to Docker socket (`/var/run/docker.sock`) for container management
- **Model Selection**: Defaults to `claude-sonnet-4-20250514`; update via config for different models
- **Workspace Isolation**: Agents see shared workspace but have separate conversation histories

## Project Structure

```
code-agent/
├── agents/                    # Specialized AI agents
│   ├── base_agent.py         # Abstract base class
│   ├── architect_agent.py    # Architecture & design
│   ├── coding_agent.py       # Implementation & review
│   ├── testing_agent.py      # Testing & QA
│   ├── deployment_agent.py   # Deployment & DevOps
│   └── monitoring_agent.py   # Monitoring & observability
├── providers/                 # AI provider abstractions
│   ├── base_provider.py      # Abstract provider interface
│   ├── anthropic_provider.py # Anthropic/Claude provider
│   ├── gemini_provider.py    # Google Gemini provider
│   ├── grok_provider.py      # xAI Grok provider
│   └── groq_provider.py      # Groq provider
├── pipelines/                 # Orchestration
│   └── orchestrator.py       # Pipeline coordinator
├── config/                    # Configuration management
│   └── settings.py           # Settings and config loading
├── examples/                  # Usage examples
│   └── example_usage.py      # Example scripts
├── Dockerfile                 # Sandbox container definition
├── main.py                   # CLI entry point
├── requirements.txt          # Python dependencies
├── CLAUDE.md                 # This file
├── CONFIG.md                 # Basic configuration guide
├── CONFIG_MULTI_PROVIDER.md  # Multi-provider setup guide
└── DEPLOYMENT.md             # Deployment guide

Legacy: agents/coding_agent_legacy.py (original single-agent implementation)
```

## Common Workflows

**New Feature Development**:
1. Architect designs the feature architecture
2. Coding agent implements according to spec
3. Testing agent creates and runs tests
4. Deployment agent packages and deploys
5. Monitoring agent sets up health checks

**Code Review**:
1. Architect reviews architecture
2. Coding agent reviews code quality
3. Testing agent runs QA suite
4. Results aggregated in review output

**Bug Fix**:
1. Use Coding agent directly with bug description
2. Agent diagnoses, fixes, and runs tests
3. Use Deployment agent to deploy fix

**Performance Optimization**:
1. Monitoring agent analyzes current performance
2. Coding agent implements optimizations
3. Testing agent runs performance benchmarks
4. Monitoring agent verifies improvements

## Deployment

See `DEPLOYMENT.md` for comprehensive deployment strategies including:
- Local development setup
- Docker and Docker Compose deployment
- Kubernetes deployment
- Cloud deployment (AWS, GCP, Azure)
- CI/CD integration
- Monitoring and observability
- Security considerations
- Scaling strategies
