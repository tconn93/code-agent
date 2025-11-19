# Configuration Guide - Multi-Provider Support

This guide explains how to configure the AI Agent Pipeline with support for multiple AI providers including Anthropic Claude, Google Gemini, xAI Grok, and Groq.

## Quick Start

1. **Initialize default configuration**:
   ```bash
   python main.py init
   ```
   This creates `config.json` in the current directory with placeholders for all providers.

2. **Edit the configuration file**:
   ```bash
   nano config.json  # or your preferred editor
   ```

3. **Set your API keys**:
   Add API keys for the providers you want to use. You don't need all of them - only the ones you plan to use.

## Supported AI Providers

### 1. Anthropic Claude
- **Models**: `claude-sonnet-4-20250514`, `claude-opus-4-20250514`, `claude-3-5-sonnet-20241022`, `claude-3-haiku-20240307`
- **Get API Key**: [console.anthropic.com](https://console.anthropic.com/)
- **Best for**: Complex reasoning, code quality, architecture design
- **Provider ID**: `anthropic`

### 2. Google Gemini
- **Models**: `gemini-2.0-flash-exp`, `gemini-1.5-pro`, `gemini-1.5-flash`
- **Get API Key**: [aistudio.google.com](https://aistudio.google.com/app/apikey)
- **Best for**: Multimodal tasks, fast responses, cost efficiency
- **Provider ID**: `gemini`

### 3. xAI Grok
- **Models**: `grok-beta`, `grok-vision-beta`
- **Get API Key**: [console.x.ai](https://console.x.ai/)
- **Best for**: Real-time information, creative tasks
- **Provider ID**: `grok`

### 4. Groq
- **Models**: `llama-3.3-70b-versatile`, `mixtral-8x7b-32768`, `gemma2-9b-it`
- **Get API Key**: [console.groq.com](https://console.groq.com/)
- **Best for**: Ultra-fast inference, high throughput
- **Provider ID**: `groq`

## Configuration Methods

The system supports three configuration methods (in priority order):

1. **Config file** (highest priority): Explicitly specified via `--config` flag
2. **Default config.json**: Located in the current directory
3. **Environment variables** (lowest priority): Loaded from shell environment

### Method 1: Configuration File (Recommended)

Create a `config.json` file with your API keys and model preferences:

```json
{
  "anthropic_api_key": "sk-ant-xxxxx",
  "gemini_api_key": "AIzaSyxxxxx",
  "grok_api_key": "xai-xxxxx",
  "groq_api_key": "gsk_xxxxx",

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
    "architect": "anthropic:claude-opus-4-20250514",
    "coding": "anthropic:claude-sonnet-4-20250514",
    "testing": "groq:llama-3.3-70b-versatile",
    "deployment": "gemini:gemini-2.0-flash-exp",
    "monitoring": "groq:llama-3.3-70b-versatile"
  }
}
```

**Model Configuration Format**: `"provider:model"` or just `"model"` (defaults to Anthropic)

### Method 2: Environment Variables

Set environment variables in your shell:

```bash
# API Keys (set only the ones you need)
export ANTHROPIC_API_KEY="sk-ant-xxxxx"
export GEMINI_API_KEY="AIzaSyxxxxx"
export GROK_API_KEY="xai-xxxxx"
export GROQ_API_KEY="gsk_xxxxx"

# Other settings
export ANTHROPIC_MODEL="claude-sonnet-4-20250514"
export WORKSPACE_PATH="/tmp/agent-workspace"
export MAX_ITERATIONS="20"
```

## Configuration Parameters

### API Keys

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `anthropic_api_key` | string | Conditional | Anthropic API key (required if using Claude models) |
| `gemini_api_key` | string | Conditional | Google AI API key (required if using Gemini models) |
| `grok_api_key` | string | Conditional | xAI API key (required if using Grok models) |
| `groq_api_key` | string | Conditional | Groq API key (required if using Groq models) |

**Note**: You must provide at least one API key for the system to work.

### Model Selection

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `anthropic_model` | string | `claude-sonnet-4-20250514` | Default model (backward compatibility) |
| `agent_models` | object | *see below* | Per-agent provider and model configuration |

### Per-Agent Model Configuration

Configure each agent to use a specific provider and model:

```json
{
  "agent_models": {
    "architect": "provider:model",
    "coding": "provider:model",
    "testing": "provider:model",
    "deployment": "provider:model",
    "monitoring": "provider:model"
  }
}
```

**Examples**:
- `"anthropic:claude-sonnet-4-20250514"` - Use Claude Sonnet
- `"gemini:gemini-2.0-flash-exp"` - Use Gemini Flash
- `"grok:grok-beta"` - Use Grok
- `"groq:llama-3.3-70b-versatile"` - Use Groq with Llama
- `"claude-sonnet-4-20250514"` - Defaults to Anthropic provider

### Available Models by Provider

**Anthropic (Claude)**:
- `claude-sonnet-4-20250514` - Latest Sonnet (balanced, recommended)
- `claude-opus-4-20250514` - Most capable (best for complex tasks)
- `claude-3-5-sonnet-20241022` - Previous Sonnet
- `claude-3-haiku-20240307` - Fastest, most economical

**Google (Gemini)**:
- `gemini-2.0-flash-exp` - Latest experimental Flash (fast & capable)
- `gemini-1.5-pro` - Pro model (high capability)
- `gemini-1.5-flash` - Flash model (fast inference)

**xAI (Grok)**:
- `grok-beta` - Grok base model
- `grok-vision-beta` - Grok with vision capabilities

**Groq** (Ultra-fast inference):
- `llama-3.3-70b-versatile` - Llama 3.3 70B (balanced)
- `mixtral-8x7b-32768` - Mixtral (long context)
- `gemma2-9b-it` - Gemma 2 (efficient)

### Docker & Workspace Settings

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `docker_image` | string | `coding-agent-sandbox` | Docker image name for sandbox containers |
| `workspace_path` | string | `/tmp/agent-workspace` | Host path for shared workspace |

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

## Example Configurations

### 1. Cost-Optimized Configuration

Use cheaper, faster models where appropriate:

```json
{
  "anthropic_api_key": "sk-ant-xxxxx",
  "groq_api_key": "gsk_xxxxx",
  "gemini_api_key": "AIzaSyxxxxx",

  "agent_models": {
    "architect": "anthropic:claude-sonnet-4-20250514",
    "coding": "anthropic:claude-sonnet-4-20250514",
    "testing": "groq:llama-3.3-70b-versatile",
    "deployment": "gemini:gemini-2.0-flash-exp",
    "monitoring": "groq:llama-3.3-70b-versatile"
  },

  "max_iterations": 15,
  "output_truncate_length": 3000
}
```

**Cost Breakdown**:
- Architect & Coding: Claude Sonnet (best quality for critical tasks)
- Testing: Groq Llama (fast, good for test generation)
- Deployment & Monitoring: Gemini/Groq (fast & economical for ops tasks)

### 2. High-Performance Configuration

Use fastest models for maximum throughput:

```json
{
  "groq_api_key": "gsk_xxxxx",
  "gemini_api_key": "AIzaSyxxxxx",

  "agent_models": {
    "architect": "gemini:gemini-1.5-pro",
    "coding": "gemini:gemini-2.0-flash-exp",
    "testing": "groq:llama-3.3-70b-versatile",
    "deployment": "groq:mixtral-8x7b-32768",
    "monitoring": "groq:llama-3.3-70b-versatile"
  }
}
```

**Benefits**: Ultra-fast execution with Groq's optimized inference

### 3. Quality-First Configuration

Use best models regardless of cost:

```json
{
  "anthropic_api_key": "sk-ant-xxxxx",

  "agent_models": {
    "architect": "anthropic:claude-opus-4-20250514",
    "coding": "anthropic:claude-opus-4-20250514",
    "testing": "anthropic:claude-sonnet-4-20250514",
    "deployment": "anthropic:claude-sonnet-4-20250514",
    "monitoring": "anthropic:claude-sonnet-4-20250514"
  },

  "max_iterations": 30,
  "coverage_threshold": 90.0
}
```

**Benefits**: Highest quality outputs across all stages

### 4. Mixed Provider Configuration

Leverage strengths of different providers:

```json
{
  "anthropic_api_key": "sk-ant-xxxxx",
  "gemini_api_key": "AIzaSyxxxxx",
  "grok_api_key": "xai-xxxxx",
  "groq_api_key": "gsk_xxxxx",

  "agent_models": {
    "architect": "anthropic:claude-opus-4-20250514",
    "coding": "anthropic:claude-sonnet-4-20250514",
    "testing": "groq:llama-3.3-70b-versatile",
    "deployment": "gemini:gemini-2.0-flash-exp",
    "monitoring": "grok:grok-beta"
  }
}
```

**Strategy**:
- Architect: Claude Opus (best reasoning for design decisions)
- Coding: Claude Sonnet (excellent code generation)
- Testing: Groq Llama (fast test generation)
- Deployment: Gemini Flash (quick DevOps automation)
- Monitoring: Grok (real-time monitoring insights)

### 5. Gemini-Only Configuration

Use only Google's models:

```json
{
  "gemini_api_key": "AIzaSyxxxxx",

  "agent_models": {
    "architect": "gemini:gemini-1.5-pro",
    "coding": "gemini:gemini-1.5-pro",
    "testing": "gemini:gemini-2.0-flash-exp",
    "deployment": "gemini:gemini-2.0-flash-exp",
    "monitoring": "gemini:gemini-2.0-flash-exp"
  }
}
```

## Working with Repositories

### Existing Repository

```bash
python main.py run \
  --requirements "Add authentication" \
  --repo-url https://github.com/username/my-project
```

### New Project

Omit `--repo-url` to start from scratch:

```bash
python main.py run --requirements "Build a REST API"
```

## Programmatic Usage

```python
from config import Settings
from pipelines import PipelineOrchestrator

# Load from file
settings = Settings.from_file("./config.json")

# Or create manually with multiple providers
settings = Settings(
    anthropic_api_key="sk-ant-xxxxx",
    gemini_api_key="AIzaSyxxxxx",
    groq_api_key="gsk_xxxxx",
    agent_models={
        "architect": "anthropic:claude-opus-4-20250514",
        "coding": "anthropic:claude-sonnet-4-20250514",
        "testing": "groq:llama-3.3-70b-versatile",
        "deployment": "gemini:gemini-2.0-flash-exp",
        "monitoring": "groq:llama-3.3-70b-versatile"
    }
)

# Create orchestrator
orchestrator = PipelineOrchestrator(
    api_key=settings.anthropic_api_key,  # Legacy parameter
    workspace_path=settings.workspace_path,
    settings=settings
)

# Run pipeline
result = orchestrator.run_full_pipeline(
    requirements="Your requirements",
    output_dir="./output"
)

# Each agent will use its configured provider and model
```

## Troubleshooting

### API Key Not Found

```
Error: No API key found for provider 'gemini'
```

**Solution**: Add the required API key to your config:
```json
{
  "gemini_api_key": "AIzaSyxxxxx"
}
```

Or set environment variable:
```bash
export GEMINI_API_KEY="AIzaSyxxxxx"
```

### Provider Not Supported

```
Error: Unknown provider: xyz
```

**Solution**: Use a valid provider name: `anthropic`, `gemini`, `grok`, or `groq`

### Model Not Available

Check the provider's documentation for available models and ensure you have access.

### Missing Dependencies

```
Error: No module named 'google.generativeai'
```

**Solution**: Install all dependencies:
```bash
pip install -r requirements.txt
```

## Security Considerations

1. **API Key Protection**:
   ```bash
   echo "config.json" >> .gitignore
   chmod 600 config.json
   ```

2. **Environment Variables**: Use secure secret management for production:
   - AWS: AWS Secrets Manager
   - GCP: Secret Manager
   - Azure: Key Vault

3. **Provider Quotas**: Monitor API usage across all providers to avoid unexpected charges.

4. **Rate Limiting**: Different providers have different rate limits. Configure accordingly.

## Provider Comparison

| Feature | Anthropic | Gemini | Grok | Groq |
|---------|-----------|--------|------|------|
| Tool Calling | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes |
| Speed | Medium | Fast | Medium | Ultra-Fast |
| Cost | Medium-High | Low | Medium | Low |
| Context Length | 200K | 1M-2M | 128K | 32K-128K |
| Best Use Case | Reasoning | Multimodal | Creative | Speed |

## Next Steps

- See [CLAUDE.md](./CLAUDE.md) for architecture and development guide
- See [DEPLOYMENT.md](./DEPLOYMENT.md) for production deployment
- See [examples/example_usage.py](./examples/example_usage.py) for code examples
- Check provider documentation for model-specific features and limitations
