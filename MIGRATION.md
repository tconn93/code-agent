# Migration Guide - Multi-Provider Support

This guide helps you migrate from single-provider (Anthropic-only) configurations to the new multi-provider system.

## Overview

The AI Agent Pipeline now supports multiple AI providers:
- **Anthropic Claude** (existing)
- **Google Gemini** (new)
- **xAI Grok** (new)
- **Groq** (new)

## Backward Compatibility

**Good news**: Your existing configurations will continue to work! The system is backward compatible.

### Existing Config (Still Works)

```json
{
  "anthropic_api_key": "sk-ant-xxxxx",
  "anthropic_model": "claude-sonnet-4-20250514",
  "agent_models": {
    "architect": "claude-opus-4-20250514",
    "coding": "claude-sonnet-4-20250514"
  }
}
```

This will continue to work as before, using only Anthropic models.

## Migration Steps

### Step 1: Update Dependencies

Install the new provider dependencies:

```bash
pip install --upgrade -r requirements.txt
```

This installs:
- `google-generativeai` - For Gemini
- `openai` - For Grok (uses OpenAI-compatible API)
- `groq` - For Groq

### Step 2: Update Configuration Format

Change your `agent_models` to use the new `provider:model` format:

**Before (old format)**:
```json
{
  "agent_models": {
    "architect": "claude-opus-4-20250514",
    "coding": "claude-sonnet-4-20250514"
  }
}
```

**After (new format)**:
```json
{
  "agent_models": {
    "architect": "anthropic:claude-opus-4-20250514",
    "coding": "anthropic:claude-sonnet-4-20250514"
  }
}
```

**Note**: The old format still works! Models without a provider prefix default to Anthropic.

### Step 3: Add New Provider API Keys (Optional)

If you want to use additional providers, add their API keys:

```json
{
  "anthropic_api_key": "sk-ant-xxxxx",
  "gemini_api_key": "AIzaSyxxxxx",
  "grok_api_key": "xai-xxxxx",
  "groq_api_key": "gsk_xxxxx"
}
```

You only need to add keys for providers you plan to use.

### Step 4: Configure Mixed Providers (Optional)

Now you can use different providers for different agents:

```json
{
  "anthropic_api_key": "sk-ant-xxxxx",
  "groq_api_key": "gsk_xxxxx",
  "gemini_api_key": "AIzaSyxxxxx",

  "agent_models": {
    "architect": "anthropic:claude-opus-4-20250514",
    "coding": "anthropic:claude-sonnet-4-20250514",
    "testing": "groq:llama-3.3-70b-versatile",
    "deployment": "gemini:gemini-2.0-flash-exp",
    "monitoring": "groq:llama-3.3-70b-versatile"
  }
}
```

## Common Migration Scenarios

### Scenario 1: Stay with Anthropic Only

**No changes needed!** Your existing config works as-is.

### Scenario 2: Add Groq for Speed

Keep Anthropic for critical tasks, add Groq for fast operations:

```json
{
  "anthropic_api_key": "sk-ant-xxxxx",
  "groq_api_key": "gsk_xxxxx",

  "agent_models": {
    "architect": "anthropic:claude-opus-4-20250514",
    "coding": "anthropic:claude-sonnet-4-20250514",
    "testing": "groq:llama-3.3-70b-versatile",
    "deployment": "groq:llama-3.3-70b-versatile",
    "monitoring": "groq:llama-3.3-70b-versatile"
  }
}
```

**Benefits**:
- Keep Claude for architecture and coding (best quality)
- Use Groq for testing, deployment, monitoring (ultra-fast)

### Scenario 3: Cost Optimization

Mix providers to reduce costs:

```json
{
  "anthropic_api_key": "sk-ant-xxxxx",
  "gemini_api_key": "AIzaSyxxxxx",
  "groq_api_key": "gsk_xxxxx",

  "agent_models": {
    "architect": "anthropic:claude-sonnet-4-20250514",
    "coding": "anthropic:claude-sonnet-4-20250514",
    "testing": "groq:llama-3.3-70b-versatile",
    "deployment": "gemini:gemini-2.0-flash-exp",
    "monitoring": "gemini:gemini-2.0-flash-exp"
  }
}
```

**Cost savings**: Gemini and Groq are typically cheaper than Claude for operations.

### Scenario 4: Switch to Gemini

Use only Gemini:

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

## Environment Variable Migration

### Before

```bash
export ANTHROPIC_API_KEY="sk-ant-xxxxx"
export ANTHROPIC_MODEL="claude-sonnet-4-20250514"
```

### After

```bash
# Add new provider keys
export ANTHROPIC_API_KEY="sk-ant-xxxxx"
export GEMINI_API_KEY="AIzaSyxxxxx"
export GROK_API_KEY="xai-xxxxx"
export GROQ_API_KEY="gsk_xxxxx"

# ANTHROPIC_MODEL still works for backward compatibility
export ANTHROPIC_MODEL="claude-sonnet-4-20250514"
```

## Programmatic Usage Migration

### Before

```python
from config import Settings
from pipelines import PipelineOrchestrator

settings = Settings.from_env()
orchestrator = PipelineOrchestrator(
    api_key=settings.anthropic_api_key,
    workspace_path=settings.workspace_path
)
```

### After (Backward Compatible)

```python
from config import Settings
from pipelines import PipelineOrchestrator

settings = Settings.from_env()
orchestrator = PipelineOrchestrator(
    api_key=settings.anthropic_api_key,  # Still works
    workspace_path=settings.workspace_path,
    settings=settings  # Now required for multi-provider support
)
```

### After (Full Multi-Provider)

```python
from config import Settings
from pipelines import PipelineOrchestrator

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

orchestrator = PipelineOrchestrator(
    api_key=settings.anthropic_api_key,
    workspace_path=settings.workspace_path,
    settings=settings
)
```

## Testing Your Migration

1. **Test with existing config**:
   ```bash
   python main.py run --requirements "Hello World" --output-dir ./test-output
   ```

2. **Verify agents are using correct providers**:
   Check the console output. You should see:
   ```
   [ORCHESTRATOR] Created architect agent with anthropic:claude-opus-4-20250514
   [ORCHESTRATOR] Created coding agent with groq:llama-3.3-70b-versatile
   ```

3. **Check pipeline output**:
   ```bash
   cat ./test-output/pipeline_state.json
   ```

## Rollback

If you need to rollback:

1. **Uninstall new dependencies** (optional):
   ```bash
   pip uninstall google-generativeai groq
   ```

2. **Use old config format**:
   ```json
   {
     "anthropic_api_key": "sk-ant-xxxxx",
     "agent_models": {
       "architect": "claude-opus-4-20250514"
     }
   }
   ```

The system will automatically default to Anthropic provider.

## FAQ

**Q: Do I need to update my config?**
A: No, old configs still work. But you should add provider prefixes for clarity.

**Q: Can I mix old and new format?**
A: Yes! `"claude-sonnet-4-20250514"` and `"anthropic:claude-sonnet-4-20250514"` are equivalent.

**Q: What if I only have Anthropic API key?**
A: Everything works as before. The multi-provider system is opt-in.

**Q: Will this break my existing pipelines?**
A: No! The changes are backward compatible.

**Q: Do I need all four provider API keys?**
A: No, only provide keys for providers you want to use.

**Q: Can I use only Gemini/Grok/Groq without Anthropic?**
A: Yes! Just provide that provider's API key and configure all agents to use it.

## Getting Help

- **Configuration Guide**: [CONFIG_MULTI_PROVIDER.md](./CONFIG_MULTI_PROVIDER.md)
- **Basic Setup**: [CONFIG.md](./CONFIG.md)
- **Development Guide**: [CLAUDE.md](./CLAUDE.md)

## Summary

- ✅ Existing configs work without changes
- ✅ Add provider prefixes for clarity: `provider:model`
- ✅ Install new dependencies: `pip install -r requirements.txt`
- ✅ Add API keys only for providers you use
- ✅ Test your migration before production deployment
