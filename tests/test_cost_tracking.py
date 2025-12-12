"""
Unit tests for cost tracking system.
"""
import pytest
from services.cost_tracking import (
    calculate_cost,
    update_job_cost,
    get_project_cost,
    check_budget_limit,
    enforce_budget_limit
)
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from services.api.database import Base
from services.api import models
from decimal import Decimal

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_costs.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(autouse=True)
def setup_database():
    """Create tables before each test and drop after."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db():
    """Get database session."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


class TestCostCalculation:
    """Test cost calculation functions."""

    def test_calculate_cost_anthropic_sonnet(self):
        """Test cost calculation for Anthropic Claude Sonnet."""
        cost = calculate_cost(
            provider="anthropic",
            model="claude-sonnet-4-20250514",
            input_tokens=1_000_000,  # 1M tokens
            output_tokens=1_000_000   # 1M tokens
        )

        # Expected: (1M * $3/1M) + (1M * $15/1M) = $18
        assert cost == 18.0

    def test_calculate_cost_openai_gpt5(self):
        """Test cost calculation for OpenAI GPT-5.1."""
        cost = calculate_cost(
            provider="openai",
            model="gpt-5.1",
            input_tokens=500_000,  # 0.5M tokens
            output_tokens=500_000   # 0.5M tokens
        )

        # Expected: (0.5M * $10/1M) + (0.5M * $30/1M) = $20
        assert cost == 20.0

    def test_calculate_cost_google_flash(self):
        """Test cost calculation for Google Gemini Flash."""
        cost = calculate_cost(
            provider="google",
            model="gemini-2.5-flash",
            input_tokens=10_000_000,  # 10M tokens
            output_tokens=5_000_000    # 5M tokens
        )

        # Expected: (10M * $0.075/1M) + (5M * $0.30/1M) = $0.75 + $1.50 = $2.25
        assert cost == 2.25

    def test_calculate_cost_groq_llama(self):
        """Test cost calculation for Groq Llama."""
        cost = calculate_cost(
            provider="groq",
            model="llama-3.3-70b-versatile",
            input_tokens=1_000_000,
            output_tokens=1_000_000
        )

        # Expected: (1M * $0.59/1M) + (1M * $0.79/1M) = $1.38
        assert cost == 1.38

    def test_calculate_cost_xai_grok(self):
        """Test cost calculation for xAI Grok."""
        cost = calculate_cost(
            provider="xai",
            model="grok-4-1-fast-reasoning",
            input_tokens=2_000_000,
            output_tokens=1_000_000
        )

        # Expected: (2M * $5/1M) + (1M * $15/1M) = $25
        assert cost == 25.0

    def test_calculate_cost_unknown_provider(self):
        """Test cost calculation for unknown provider (uses default)."""
        cost = calculate_cost(
            provider="unknown_provider",
            model="some_model",
            input_tokens=1_000_000,
            output_tokens=1_000_000
        )

        # Expected: default pricing (1M * $1/1M) + (1M * $3/1M) = $4
        assert cost == 4.0

    def test_calculate_cost_unknown_model(self):
        """Test cost calculation for unknown model (uses default for provider)."""
        cost = calculate_cost(
            provider="anthropic",
            model="unknown_model",
            input_tokens=1_000_000,
            output_tokens=1_000_000
        )

        # Expected: default Anthropic pricing (1M * $3/1M) + (1M * $15/1M) = $18
        assert cost == 18.0

    def test_calculate_cost_small_numbers(self):
        """Test cost calculation with small token counts."""
        cost = calculate_cost(
            provider="anthropic",
            model="claude-sonnet-4-20250514",
            input_tokens=1_000,    # 0.001M tokens
            output_tokens=2_000     # 0.002M tokens
        )

        # Expected: (0.001M * $3/1M) + (0.002M * $15/1M) = $0.003 + $0.03 = $0.033
        assert cost == 0.033


class TestJobCostTracking:
    """Test job cost tracking."""

    def test_update_job_cost(self, db):
        """Test updating job cost based on token usage."""
        # Create a project and job
        project = models.Project(name="Test Project")
        db.add(project)
        db.commit()

        job = models.Job(
            project_id=project.id,
            type="implement_feature",
            payload={"task": "Test"},
            status="completed",
            tokens_used_input=1_000_000,
            tokens_used_output=500_000
        )
        db.add(job)
        db.commit()

        # Update cost
        update_job_cost(job, provider="anthropic", model="claude-sonnet-4-20250514")

        # Expected: (1M * $3/1M) + (0.5M * $15/1M) = $10.50
        assert float(job.actual_cost) == 10.5


class TestProjectCostReporting:
    """Test project-level cost reporting."""

    def test_get_project_cost(self, db):
        """Test getting total cost for a project."""
        # Create project
        project = models.Project(name="Test Project")
        db.add(project)
        db.commit()

        # Create jobs with costs
        job1 = models.Job(
            project_id=project.id,
            type="implement_feature",
            payload={},
            status="completed",
            actual_cost=Decimal("10.50")
        )
        job2 = models.Job(
            project_id=project.id,
            type="review_code",
            payload={},
            status="completed",
            actual_cost=Decimal("5.25")
        )
        job3 = models.Job(
            project_id=project.id,
            type="create_tests",
            payload={},
            status="failed",
            actual_cost=Decimal("2.00")
        )
        db.add_all([job1, job2, job3])
        db.commit()

        # Get project cost
        cost_info = get_project_cost(project.id, db)

        assert cost_info["project_id"] == project.id
        assert cost_info["total_cost"] == 17.75  # 10.50 + 5.25 + 2.00
        assert cost_info["total_jobs"] == 3
        assert cost_info["completed_jobs"] == 2
        assert cost_info["failed_jobs"] == 1
        assert cost_info["average_cost_per_job"] == round(17.75 / 3, 2)


class TestBudgetEnforcement:
    """Test budget enforcement."""

    def test_check_budget_limit_ok(self, db):
        """Test budget check when under limit."""
        # Create project with budget
        project = models.Project(
            name="Test Project",
            budget_allocated=Decimal("100.00")
        )
        db.add(project)
        db.commit()

        # Add jobs with total cost of $50
        for i in range(5):
            job = models.Job(
                project_id=project.id,
                type="test",
                payload={},
                actual_cost=Decimal("10.00")
            )
            db.add(job)
        db.commit()

        # Check budget
        status = check_budget_limit(project.id, db)

        assert status["status"] == "ok"  # 50% used, status should be "ok"
        assert status["budget_allocated"] == 100.0
        assert status["actual_cost"] == 50.0
        assert status["remaining_budget"] == 50.0
        assert status["percentage_used"] == 50.0

    def test_check_budget_limit_warning(self, db):
        """Test budget check when in warning zone (80%)."""
        project = models.Project(
            name="Test Project",
            budget_allocated=Decimal("100.00")
        )
        db.add(project)
        db.commit()

        # Add jobs with total cost of $85
        job = models.Job(
            project_id=project.id,
            type="test",
            payload={},
            actual_cost=Decimal("85.00")
        )
        db.add(job)
        db.commit()

        # Check budget
        status = check_budget_limit(project.id, db)

        assert status["status"] == "warning"  # 85% used
        assert status["percentage_used"] == 85.0

    def test_check_budget_limit_critical(self, db):
        """Test budget check when in critical zone (95%)."""
        project = models.Project(
            name="Test Project",
            budget_allocated=Decimal("100.00")
        )
        db.add(project)
        db.commit()

        job = models.Job(
            project_id=project.id,
            type="test",
            payload={},
            actual_cost=Decimal("96.00")
        )
        db.add(job)
        db.commit()

        status = check_budget_limit(project.id, db)

        assert status["status"] == "critical"  # 96% used
        assert status["percentage_used"] == 96.0

    def test_check_budget_limit_exceeded(self, db):
        """Test budget check when exceeded."""
        project = models.Project(
            name="Test Project",
            budget_allocated=Decimal("100.00")
        )
        db.add(project)
        db.commit()

        job = models.Job(
            project_id=project.id,
            type="test",
            payload={},
            actual_cost=Decimal("105.00")
        )
        db.add(job)
        db.commit()

        status = check_budget_limit(project.id, db)

        assert status["status"] == "exceeded"  # 105% used
        assert status["percentage_used"] == 105.0
        assert status["remaining_budget"] == -5.0

    def test_enforce_budget_limit_allows(self, db):
        """Test that enforce_budget_limit allows jobs when under budget."""
        project = models.Project(
            name="Test Project",
            budget_allocated=Decimal("100.00")
        )
        db.add(project)
        db.commit()

        # Add job with $50 cost
        job = models.Job(
            project_id=project.id,
            type="test",
            payload={},
            actual_cost=Decimal("50.00")
        )
        db.add(job)
        db.commit()

        # Should allow new jobs
        assert enforce_budget_limit(project.id, db) is True

    def test_enforce_budget_limit_blocks(self, db):
        """Test that enforce_budget_limit blocks jobs when budget exceeded."""
        project = models.Project(
            name="Test Project",
            budget_allocated=Decimal("100.00")
        )
        db.add(project)
        db.commit()

        # Add job that exceeds budget
        job = models.Job(
            project_id=project.id,
            type="test",
            payload={},
            actual_cost=Decimal("105.00")
        )
        db.add(job)
        db.commit()

        # Should block new jobs
        assert enforce_budget_limit(project.id, db) is False

    def test_enforce_budget_no_budget_set(self, db):
        """Test that projects without budget are not blocked."""
        project = models.Project(
            name="Test Project",
            budget_allocated=None  # No budget set
        )
        db.add(project)
        db.commit()

        # Should allow jobs (no budget limit)
        assert enforce_budget_limit(project.id, db) is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
