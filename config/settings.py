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

    # Anthropic API
    anthropic_api_key: str
    anthropic_model: str = "claude-sonnet-4-20250514"

    # Docker settings
    docker_image: str = "coding-agent-sandbox"
    workspace_path: str = "/tmp/agent-workspace"

    # Agent settings
    max_iterations: int = 20
    output_truncate_length: int = 5000

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
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is required")

        return cls(
            anthropic_api_key=api_key,
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
        anthropic_api_key="your-api-key-here",
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
    print("Please update the anthropic_api_key in the config file.")
