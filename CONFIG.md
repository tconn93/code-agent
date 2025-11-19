# Configuration Guide

This guide explains how to configure the AI Agent Pipeline, including setting up API keys, customizing models, and managing project repositories.

## 🆕 Multi-Provider Support

The AI Agent Pipeline now supports **multiple AI providers**! You can configure each agent to use different providers and models:

- **Anthropic Claude** - Best for complex reasoning and code quality
- **Google Gemini** - Fast, capable, cost-effective
- **xAI Grok** - Real-time information and creative tasks
- **Groq** - Ultra-fast inference with open models

**For comprehensive multi-provider documentation, see [CONFIG_MULTI_PROVIDER.md](./CONFIG_MULTI_PROVIDER.md)**

This page covers the basics. For advanced multi-provider setups, model comparisons, and cost optimization strategies, refer to the multi-provider guide.

## Quick Start

1. **Initialize default configuration**:
   ```bash
   python main.py init
   ```
   This creates `config.json` in the current directory.

2. **Edit the configuration file**:
   ```bash
   nano config.json  # or your preferred editor
   ```

3. **Set your API key**:
   Replace `"your-api-key-here"` with your actual Anthropic API key.

## Configuration Methods

The system supports three configuration methods (in priority order):

1. **Config file** (highest priority): Explicitly specified via `--config` flag
2. **Default config.json**: Located in the current directory
3. **Environment variables** (lowest priority): Loaded from shell environment

### Method 1: Configuration File (Recommended)

Create a `config.json` file:

```json
{
  "anthropic_api_key": "sk-ant-xxxxx",
  "anthropic_model": "claude-sonnet-4-20250514",
  "docker_image": "coding-agent-sandbox",
  "workspace_path": "/tmp/agent-workspace",
  "max_iterations": 20,
  "output_truncate_length": 5000,
  "default_output_dir": "./pipeline_output",
  "save_intermediate_results": true,
  "health_check_timeout": 10,
  "log_analysis_lines": 100,
  "coverage_threshold": 80.0,
  "run_security_scans": true,
  "default_deployment_platform": "docker",
  "deployment_environments": ["dev", "staging", "production"],
  "agent_models": {
    "architect": "claude-sonnet-4-20250514",
    "coding": "claude-sonnet-4-20250514",
    "testing": "claude-sonnet-4-20250514",
    "deployment": "claude-sonnet-4-20250514",
    "monitoring": "claude-sonnet-4-20250514"
  }
}
```

Use it with:
```bash
python main.py run --config ./config.json --requirements "Build a REST API"
```

### Method 2: Environment Variables

Set environment variables in your shell:

```bash
export ANTHROPIC_API_KEY="sk-ant-xxxxx"
export ANTHROPIC_MODEL="claude-sonnet-4-20250514"
export WORKSPACE_PATH="/tmp/agent-workspace"
export MAX_ITERATIONS="20"
export OUTPUT_TRUNCATE_LENGTH="5000"
export DEFAULT_OUTPUT_DIR="./pipeline_output"
export SAVE_INTERMEDIATE_RESULTS="true"
export HEALTH_CHECK_TIMEOUT="10"
export LOG_ANALYSIS_LINES="100"
export COVERAGE_THRESHOLD="80.0"
export RUN_SECURITY_SCANS="true"
export DEFAULT_DEPLOYMENT_PLATFORM="docker"
```

Then run without `--config`:
```bash
python main.py run --requirements "Build a REST API"
```

## Configuration Parameters

### API Settings

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `anthropic_api_key` | string | *required* | Your Anthropic API key (get it from console.anthropic.com) |
| `anthropic_model` | string | `claude-sonnet-4-20250514` | Default Claude model for all agents |
| `agent_models` | object | *see below* | Per-agent model configuration (optional) |

**Available Models**:
- `claude-sonnet-4-20250514` - Latest Sonnet (recommended, balanced performance)
- `claude-opus-4-20250514` - Most capable (slower, more expensive)
- `claude-3-5-sonnet-20241022` - Previous Sonnet version
- `claude-3-opus-20240229` - Previous Opus version
- `claude-3-haiku-20240307` - Fastest, most economical

### Per-Agent Model Configuration

You can assign different models to different agents for cost optimization:

```json
{
  "anthropic_model": "claude-sonnet-4-20250514",
  "agent_models": {
    "architect": "claude-opus-4-20250514",    // Use most capable for design
    "coding": "claude-sonnet-4-20250514",     // Balanced for implementation
    "testing": "claude-3-haiku-20240307",     // Fast for test generation
    "deployment": "claude-3-haiku-20240307",  // Fast for DevOps tasks
    "monitoring": "claude-3-haiku-20240307"   // Fast for monitoring
  }
}
```

### Docker & Workspace Settings

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `docker_image` | string | `coding-agent-sandbox` | Docker image name for sandbox containers |
| `workspace_path` | string | `/tmp/agent-workspace` | Host path for shared workspace |

**Note**: The workspace is mounted to `/workspace` inside containers. Change `workspace_path` to use a different host directory:

```json
{
  "workspace_path": "/home/user/projects/agent-workspace"
}
```

### Agent Behavior Settings

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `max_iterations` | integer | `20` | Maximum conversation turns per agent |
| `output_truncate_length` | integer | `5000` | Maximum characters in tool output |
| `default_output_dir` | string | `./pipeline_output` | Default directory for pipeline results |
| `save_intermediate_results` | boolean | `true` | Save state after each pipeline stage |

### Testing Settings

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `coverage_threshold` | float | `80.0` | Minimum code coverage percentage |
| `run_security_scans` | boolean | `true` | Enable security scanning in QA |

### Monitoring Settings

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `health_check_timeout` | integer | `10` | Timeout for health checks (seconds) |
| `log_analysis_lines` | integer | `100` | Number of log lines to analyze |

### Deployment Settings

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `default_deployment_platform` | string | `docker` | Default deployment platform |
| `deployment_environments` | array | `["dev", "staging", "production"]` | Available deployment environments |

## Specifying Project Repositories

You can work with existing repositories or create new projects.

### Working with Existing Repositories

Specify a Git repository URL using the `--repo-url` flag:

```bash
# Full pipeline on existing repo
python main.py run \
  --requirements "Add user authentication" \
  --repo-url https://github.com/username/my-project

# Code review of existing repo
python main.py review \
  --repo-url https://github.com/username/my-project \
  --focus security performance
```

**Supported Git URLs**:
- HTTPS: `https://github.com/username/repo.git`
- SSH: `git@github.com:username/repo.git`
- GitLab: `https://gitlab.com/username/repo.git`
- Private repos: Use SSH keys or tokens

### Creating New Projects

Omit `--repo-url` to start a new project from scratch:

```bash
python main.py run --requirements "Build a REST API for task management"
```

The pipeline will:
1. Create project structure in the workspace
2. Generate architecture documentation
3. Implement code from scratch
4. Create tests and deployment configs

### Using Different Repositories per Stage

For partial pipelines, you can work on different repos:

```bash
# Create tasks.json
cat > tasks.json << 'EOF'
{
  "coding": "Implement authentication feature",
  "testing": "Create comprehensive test suite"
}
EOF

# Run stages
python main.py run-stages \
  --stages coding testing \
  --tasks tasks.json \
  --repo-url https://github.com/username/my-project
```

## Workspace Management

The workspace is where agents read/write code and artifacts.

### Workspace Structure

```
/tmp/agent-workspace/           (host path, configurable)
├── repo/                       (cloned repository or new project)
│   ├── src/                   (source code)
│   ├── tests/                 (test files)
│   ├── docs/                  (documentation)
│   └── ...
├── docs/                       (architecture docs from Architect)
│   └── architecture/
│       ├── system-design.md
│       ├── adr-001-*.md
│       └── dependencies.json
└── pipeline_state.json         (pipeline execution state)
```

### Changing Workspace Location

Edit `config.json`:

```json
{
  "workspace_path": "/home/myuser/code-workspace"
}
```

Or set environment variable:

```bash
export WORKSPACE_PATH="/home/myuser/code-workspace"
```

### Persisting Workspace Between Runs

By default, the workspace persists on the host filesystem. To clean it:

```bash
rm -rf /tmp/agent-workspace/*  # or your custom path
```

To preserve workspace for inspection:

```bash
# Run pipeline
python main.py run --requirements "..." --output-dir ./output1

# Workspace is preserved at /tmp/agent-workspace
ls -la /tmp/agent-workspace/repo

# Copy artifacts before next run
cp -r /tmp/agent-workspace/repo ./my-backup
```

## Output Directory Structure

Pipeline results are saved to the output directory (default: `./pipeline_output`):

```
pipeline_output/
├── pipeline_state.json         (execution state, results, errors)
├── architecture/               (architecture artifacts)
│   └── ...
├── code/                       (generated code)
│   └── ...
└── logs/                       (agent conversation logs)
    └── ...
```

Change output location:

```bash
python main.py run --requirements "..." --output-dir ./my-output
```

## Example Configurations

### Cost-Optimized Configuration

Use cheaper models where possible:

```json
{
  "anthropic_api_key": "sk-ant-xxxxx",
  "anthropic_model": "claude-3-haiku-20240307",
  "agent_models": {
    "architect": "claude-sonnet-4-20250514",
    "coding": "claude-3-5-sonnet-20241022",
    "testing": "claude-3-haiku-20240307",
    "deployment": "claude-3-haiku-20240307",
    "monitoring": "claude-3-haiku-20240307"
  },
  "max_iterations": 15,
  "output_truncate_length": 3000
}
```

### High-Quality Configuration

Use best models for all stages:

```json
{
  "anthropic_api_key": "sk-ant-xxxxx",
  "anthropic_model": "claude-opus-4-20250514",
  "max_iterations": 30,
  "output_truncate_length": 8000,
  "coverage_threshold": 90.0
}
```

### Development Configuration

Fast iterations for testing:

```json
{
  "anthropic_api_key": "sk-ant-xxxxx",
  "anthropic_model": "claude-3-haiku-20240307",
  "workspace_path": "./dev-workspace",
  "max_iterations": 10,
  "save_intermediate_results": false
}
```

## Programmatic Configuration

Use the Settings class in Python code:

```python
from config import Settings
from pipelines import PipelineOrchestrator

# Load from file
settings = Settings.from_file("./config.json")

# Load from environment
settings = Settings.from_env()

# Create manually
settings = Settings(
    anthropic_api_key="sk-ant-xxxxx",
    anthropic_model="claude-sonnet-4-20250514",
    workspace_path="/tmp/workspace",
    max_iterations=20
)

# Create orchestrator
orchestrator = PipelineOrchestrator(
    api_key=settings.anthropic_api_key,
    workspace_path=settings.workspace_path
)

# Run pipeline
result = orchestrator.run_full_pipeline(
    requirements="Build a REST API",
    repo_url="https://github.com/username/repo",
    output_dir="./output"
)
```

## Troubleshooting

### API Key Not Found

```
Error: ANTHROPIC_API_KEY environment variable is required
```

**Solution**: Set API key in `config.json` or environment:
```bash
export ANTHROPIC_API_KEY="sk-ant-xxxxx"
# or
python main.py init  # then edit config.json
```

### Docker Connection Failed

```
Error: Cannot connect to Docker daemon
```

**Solution**: Ensure Docker is running:
```bash
sudo systemctl start docker  # Linux
# or start Docker Desktop (Mac/Windows)
```

### Workspace Permission Denied

```
Error: Permission denied: '/tmp/agent-workspace'
```

**Solution**: Create workspace directory with correct permissions:
```bash
sudo mkdir -p /tmp/agent-workspace
sudo chown $USER:$USER /tmp/agent-workspace
```

### Model Not Found

```
Error: model 'xyz' not found
```

**Solution**: Use a valid model name from the supported list above.

## Security Considerations

1. **API Key Protection**: Never commit `config.json` with real API keys to version control
   ```bash
   echo "config.json" >> .gitignore
   ```

2. **Workspace Isolation**: Use separate workspaces for untrusted repositories
   ```json
   {
     "workspace_path": "/tmp/untrusted-workspace"
   }
   ```

3. **Docker Security**: The sandbox container has network access. Review code before running on sensitive systems.

4. **Output Sanitization**: Review pipeline outputs before sharing, as they may contain sensitive information.

## Next Steps

- See [CLAUDE.md](./CLAUDE.md) for architecture and development guide
- See [DEPLOYMENT.md](./DEPLOYMENT.md) for production deployment
- See [examples/example_usage.py](./examples/example_usage.py) for code examples
