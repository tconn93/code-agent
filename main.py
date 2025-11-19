"""
Main entry point for the AI Agent Pipeline.
"""
import argparse
import sys
from pathlib import Path

from config import load_config, create_default_config
from pipelines import PipelineOrchestrator


def main():
    parser = argparse.ArgumentParser(
        description="AI Agent Pipeline for Software Development"
    )

    subparsers = parser.add_subparsers(dest='command', help='Command to execute')

    # Init config command
    init_parser = subparsers.add_parser('init', help='Initialize configuration')
    init_parser.add_argument(
        '--output',
        default='./config.json',
        help='Output path for config file'
    )

    # Run full pipeline
    full_parser = subparsers.add_parser('run', help='Run full development pipeline')
    full_parser.add_argument(
        '--requirements',
        required=True,
        help='Project requirements (file path or string)'
    )
    full_parser.add_argument(
        '--repo-url',
        help='Git repository URL (optional)'
    )
    full_parser.add_argument(
        '--output-dir',
        default='./pipeline_output',
        help='Output directory for results'
    )
    full_parser.add_argument(
        '--config',
        help='Path to configuration file'
    )

    # Run partial pipeline
    partial_parser = subparsers.add_parser('run-stages', help='Run specific pipeline stages')
    partial_parser.add_argument(
        '--stages',
        required=True,
        nargs='+',
        choices=['architecture', 'coding', 'testing', 'deployment', 'monitoring'],
        help='Stages to run'
    )
    partial_parser.add_argument(
        '--tasks',
        required=True,
        help='JSON file with task descriptions for each stage'
    )
    partial_parser.add_argument(
        '--repo-url',
        help='Git repository URL'
    )
    partial_parser.add_argument(
        '--output-dir',
        default='./pipeline_output',
        help='Output directory for results'
    )
    partial_parser.add_argument(
        '--config',
        help='Path to configuration file'
    )

    # Code review pipeline
    review_parser = subparsers.add_parser('review', help='Run code review pipeline')
    review_parser.add_argument(
        '--repo-url',
        required=True,
        help='Git repository URL to review'
    )
    review_parser.add_argument(
        '--focus',
        nargs='+',
        help='Specific areas to focus on'
    )
    review_parser.add_argument(
        '--output-dir',
        default='./review_output',
        help='Output directory for results'
    )
    review_parser.add_argument(
        '--config',
        help='Path to configuration file'
    )

    args = parser.parse_args()

    if args.command == 'init':
        create_default_config(args.output)
        return

    if not args.command:
        parser.print_help()
        return

    # Load configuration
    try:
        config = load_config(getattr(args, 'config', None))
    except ValueError as e:
        print(f"Error loading configuration: {e}")
        print("\nRun 'python main.py init' to create a default configuration file.")
        sys.exit(1)

    # Create orchestrator
    orchestrator = PipelineOrchestrator(
        api_key=config.anthropic_api_key,
        workspace_path=config.workspace_path
    )

    try:
        if args.command == 'run':
            # Load requirements
            requirements_path = Path(args.requirements)
            if requirements_path.exists():
                requirements = requirements_path.read_text()
            else:
                requirements = args.requirements

            print(f"\nRunning full pipeline with requirements:\n{requirements}\n")

            result = orchestrator.run_full_pipeline(
                requirements=requirements,
                repo_url=args.repo_url,
                output_dir=args.output_dir
            )

            print(f"\n✓ Pipeline completed: {result['status']}")
            print(f"✓ Stages completed: {', '.join(result['stages_completed'])}")
            print(f"✓ Results saved to: {args.output_dir}")

        elif args.command == 'run-stages':
            import json

            # Load task descriptions
            with open(args.tasks, 'r') as f:
                task_descriptions = json.load(f)

            print(f"\nRunning stages: {', '.join(args.stages)}\n")

            result = orchestrator.run_partial_pipeline(
                stages=args.stages,
                task_descriptions=task_descriptions,
                repo_url=args.repo_url,
                output_dir=args.output_dir
            )

            print(f"\n✓ Pipeline completed: {result['status']}")
            print(f"✓ Stages completed: {', '.join(result['stages_completed'])}")
            print(f"✓ Results saved to: {args.output_dir}")

        elif args.command == 'review':
            print(f"\nRunning code review for: {args.repo_url}\n")

            result = orchestrator.run_code_review_pipeline(
                repo_url=args.repo_url,
                focus_areas=args.focus,
                output_dir=args.output_dir
            )

            print(f"\n✓ Review completed: {result['status']}")
            print(f"✓ Results saved to: {args.output_dir}")

    except Exception as e:
        print(f"\n✗ Pipeline failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
