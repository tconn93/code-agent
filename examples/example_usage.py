"""
Example usage of the AI Agent Pipeline.
"""
from config import Settings
from pipelines import PipelineOrchestrator
from agents import ArchitectAgent, CodingAgent, TestingAgent


def example_full_pipeline():
    """Example: Run full development pipeline."""
    print("=== Example: Full Development Pipeline ===\n")

    # Load configuration
    settings = Settings.from_env()

    # Create orchestrator
    orchestrator = PipelineOrchestrator(
        api_key=settings.anthropic_api_key,
        workspace_path=settings.workspace_path
    )

    # Define requirements
    requirements = """
    Create a simple REST API for a task management system with the following features:

    1. User authentication (JWT)
    2. CRUD operations for tasks
    3. Task categories and tags
    4. Due dates and priorities
    5. Search and filter functionality

    Technical requirements:
    - Use Python with FastAPI
    - PostgreSQL database
    - Docker containerization
    - Comprehensive tests
    - API documentation
    """

    # Run full pipeline
    result = orchestrator.run_full_pipeline(
        requirements=requirements,
        output_dir="./example_output/full_pipeline"
    )

    print(f"\nPipeline Status: {result['status']}")
    print(f"Stages Completed: {', '.join(result['stages_completed'])}")


def example_partial_pipeline():
    """Example: Run specific stages."""
    print("=== Example: Partial Pipeline (Coding + Testing) ===\n")

    settings = Settings.from_env()
    orchestrator = PipelineOrchestrator(
        api_key=settings.anthropic_api_key,
        workspace_path=settings.workspace_path
    )

    # Define tasks for each stage
    tasks = {
        "coding": """
        Implement a user authentication module with:
        - Login endpoint
        - Registration endpoint
        - JWT token generation
        - Password hashing
        """,
        "testing": """
        Create comprehensive tests for the authentication module:
        - Unit tests for password hashing
        - Integration tests for login/registration
        - Security tests for JWT tokens
        """
    }

    result = orchestrator.run_partial_pipeline(
        stages=["coding", "testing"],
        task_descriptions=tasks,
        output_dir="./example_output/partial_pipeline"
    )

    print(f"\nPipeline Status: {result['status']}")


def example_code_review():
    """Example: Run code review pipeline."""
    print("=== Example: Code Review Pipeline ===\n")

    settings = Settings.from_env()
    orchestrator = PipelineOrchestrator(
        api_key=settings.anthropic_api_key,
        workspace_path=settings.workspace_path
    )

    result = orchestrator.run_code_review_pipeline(
        repo_url="https://github.com/yourusername/your-repo.git",
        focus_areas=["security", "performance", "test coverage"],
        output_dir="./example_output/code_review"
    )

    print(f"\nReview Status: {result['status']}")


def example_individual_agent():
    """Example: Use individual agents directly."""
    print("=== Example: Individual Agent Usage ===\n")

    settings = Settings.from_env()

    # Use Architect Agent
    with ArchitectAgent(settings.anthropic_api_key) as architect:
        architect.setup_sandbox()

        result = architect.design_system(
            requirements="""
            Design a microservices architecture for an e-commerce platform
            with services for: users, products, orders, payments, and inventory.
            """
        )

        print(f"Architecture Design Status: {result['status']}")

    # Use Coding Agent
    with CodingAgent(settings.anthropic_api_key) as coder:
        coder.setup_sandbox(repo_url="https://github.com/yourusername/repo.git")

        result = coder.implement_feature(
            feature_spec="Add dark mode toggle to the application"
        )

        print(f"Implementation Status: {result['status']}")

    # Use Testing Agent
    with TestingAgent(settings.anthropic_api_key) as tester:
        tester.setup_sandbox(repo_url="https://github.com/yourusername/repo.git")

        result = tester.run_qa_suite()

        print(f"QA Status: {result['status']}")


if __name__ == "__main__":
    # Run examples (uncomment the one you want to run)

    # example_full_pipeline()
    # example_partial_pipeline()
    # example_code_review()
    example_individual_agent()
