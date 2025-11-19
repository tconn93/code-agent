"""
Configuration management for the AI agent pipeline.
"""
import os
import json
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict


@dataclass
class Settings:
    """Application settings."""

    # API Keys for different providers
    anthropic_api_key: str = None
    gemini_api_key: str = None
    grok_api_key: str = None
    groq_api_key: str = None
    openai_api_key: str = None

    # Default model (backward compatibility)
    anthropic_model: str = "claude-sonnet-4-20250514"

    # Docker settings
    docker_image: str = "coding-agent-sandbox"
    workspace_path: str = "/tmp/agent-workspace"

    # Agent settings
    max_iterations: int = 20
    output_truncate_length: int = 5000
    agent_models: Dict[str, str] = None  # Per-agent model configuration (format: "provider:model")

    # Pipeline settings
    default_output_dir: str = "./pipeline_output"
    save_intermediate_results: bool = True

    # Monitoring settings
    health_check_timeout: int = 10
    log_analysis_lines: int = 100

    # Testing settings
    coverage_threshold: float = 80.0
    run_security_scans: bool = True

    # Deployment settings
    default_deployment_platform: str = "docker"
    deployment_environments: list = None

    def __post_init__(self):
        if self.deployment_environments is None:
            self.deployment_environments = ["dev", "staging", "production"]

        # Initialize agent_models with defaults if not provided
        if self.agent_models is None:
            self.agent_models = {
                "architect": f"anthropic:{self.anthropic_model}",
                "coding": f"anthropic:{self.anthropic_model}",
                "testing": f"anthropic:{self.anthropic_model}",
                "deployment": f"anthropic:{self.anthropic_model}",
                "monitoring": f"anthropic:{self.anthropic_model}"
            }

        # Ensure at least one API key is provided
        if not any([self.anthropic_api_key, self.gemini_api_key, self.grok_api_key, self.groq_api_key, self.openai_api_key]):
            # Only raise error if we're not initializing from file (allow defaults for config creation)
            pass

    def get_model_for_agent(self, agent_type: str) -> str:
        """
        Get the model configuration for a specific agent type.
        Returns format: "provider:model"
        """
        return self.agent_models.get(agent_type, f"anthropic:{self.anthropic_model}")

    def parse_model_config(self, model_config: str) -> tuple:
        """
        Parse model configuration string.

        Args:
            model_config: String in format "provider:model" or just "model"

        Returns:
            Tuple of (provider, model)
        """
        if ":" in model_config:
            provider, model = model_config.split(":", 1)
            return provider.lower(), model
        else:
            # Default to anthropic if no provider specified
            return "anthropic", model_config

    def get_api_key_for_provider(self, provider: str) -> Optional[str]:
        """Get API key for a specific provider."""
        provider_key_map = {
            "anthropic": self.anthropic_api_key,
            "gemini": self.gemini_api_key,
            "grok": self.grok_api_key,
            "groq": self.groq_api_key,
            "openai": self.openai_api_key
        }
        return provider_key_map.get(provider.lower())

    @classmethod
    def from_dict(cls, config: Dict[str, Any]) -> 'Settings':
        """Create Settings from dictionary."""
        return cls(**{k: v for k, v in config.items() if k in cls.__annotations__})

    @classmethod
    def from_file(cls, config_path: str) -> 'Settings':
        """Load settings from JSON file."""
        with open(config_path, 'r') as f:
            config = json.load(f)
        return cls.from_dict(config)

    @classmethod
    def from_env(cls) -> 'Settings':
        """Load settings from environment variables."""
        # Check if at least one API key is provided
        anthropic_key = os.getenv('ANTHROPIC_API_KEY')
        gemini_key = os.getenv('GEMINI_API_KEY')
        grok_key = os.getenv('GROK_API_KEY')
        groq_key = os.getenv('GROQ_API_KEY')
        openai_key = os.getenv('OPENAI_API_KEY')

        if not any([anthropic_key, gemini_key, grok_key, groq_key, openai_key]):
            raise ValueError("At least one API key is required (ANTHROPIC_API_KEY, GEMINI_API_KEY, GROK_API_KEY, GROQ_API_KEY, or OPENAI_API_KEY)")

        return cls(
            anthropic_api_key=anthropic_key,
            gemini_api_key=gemini_key,
            grok_api_key=grok_key,
            groq_api_key=groq_key,
            openai_api_key=openai_key,
            anthropic_model=os.getenv('ANTHROPIC_MODEL', 'claude-sonnet-4-20250514'),
            docker_image=os.getenv('DOCKER_IMAGE', 'coding-agent-sandbox'),
            workspace_path=os.getenv('WORKSPACE_PATH', '/tmp/agent-workspace'),
            max_iterations=int(os.getenv('MAX_ITERATIONS', '20')),
            output_truncate_length=int(os.getenv('OUTPUT_TRUNCATE_LENGTH', '5000')),
            default_output_dir=os.getenv('DEFAULT_OUTPUT_DIR', './pipeline_output'),
            save_intermediate_results=os.getenv('SAVE_INTERMEDIATE_RESULTS', 'true').lower() == 'true',
            health_check_timeout=int(os.getenv('HEALTH_CHECK_TIMEOUT', '10')),
            log_analysis_lines=int(os.getenv('LOG_ANALYSIS_LINES', '100')),
            coverage_threshold=float(os.getenv('COVERAGE_THRESHOLD', '80.0')),
            run_security_scans=os.getenv('RUN_SECURITY_SCANS', 'true').lower() == 'true',
            default_deployment_platform=os.getenv('DEFAULT_DEPLOYMENT_PLATFORM', 'docker'),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert settings to dictionary."""
        return asdict(self)

    def save(self, config_path: str):
        """Save settings to JSON file."""
        Path(config_path).parent.mkdir(parents=True, exist_ok=True)
        with open(config_path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)


def load_config(config_path: Optional[str] = None) -> Settings:
    """
    Load configuration from file or environment.

    Priority:
    1. Config file (if path provided)
    2. ./config.json (if exists)
    3. Environment variables
    """
    # Try config file path if provided
    if config_path and Path(config_path).exists():
        return Settings.from_file(config_path)

    # Try default config.json
    default_config = Path("./config.json")
    if default_config.exists():
        return Settings.from_file(str(default_config))

    # Fall back to environment variables
    return Settings.from_env()


def create_default_config(output_path: str = "./config.json"):
    """Create a default configuration file."""
    default_settings = Settings(
        anthropic_api_key="your-anthropic-api-key-here",
        gemini_api_key="your-gemini-api-key-here-optional",
        grok_api_key="your-grok-api-key-here-optional",
        groq_api_key="your-groq-api-key-here-optional",
        openai_api_key="your-openai-api-key-here-optional",
        anthropic_model="claude-sonnet-4-20250514",
        docker_image="coding-agent-sandbox",
        workspace_path="/tmp/agent-workspace",
        max_iterations=20,
        output_truncate_length=5000,
        default_output_dir="./pipeline_output",
        save_intermediate_results=True,
        health_check_timeout=10,
        log_analysis_lines=100,
        coverage_threshold=80.0,
        run_security_scans=True,
        default_deployment_platform="docker"
    )

    default_settings.save(output_path)
    print(f"Default configuration created at: {output_path}")
    print("\nPlease update the API keys in the config file:")
    print("  - anthropic_api_key: Required if using Claude models")
    print("  - gemini_api_key: Required if using Gemini models")
    print("  - grok_api_key: Required if using Grok models")
    print("  - groq_api_key: Required if using Groq models")
    print("  - openai_api_key: Required if using OpenAI GPT models")
    print("\nYou only need to provide keys for the providers you plan to use.")
