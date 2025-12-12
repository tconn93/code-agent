"""
Unit tests for error recovery system.
"""
import pytest
import time
from datetime import datetime, timedelta
from services.error_recovery import (
    RetryManager,
    CircuitBreaker,
    handle_job_failure
)
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from services.api.database import Base
from services.api import models
import redis
from unittest.mock import MagicMock

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_error_recovery.db"
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


@pytest.fixture
def mock_redis():
    """Mock Redis client."""
    return MagicMock(spec=redis.Redis)


class TestRetryManager:
    """Test retry management."""

    def test_should_retry_first_attempt(self, db):
        """Test that first failure should retry."""
        project = models.Project(name="Test")
        db.add(project)
        db.commit()

        job = models.Job(
            project_id=project.id,
            type="test",
            payload={},
            retry_count=0,
            max_retries=3
        )
        db.add(job)
        db.commit()

        assert RetryManager.should_retry(job, max_retries=3) is True

    def test_should_retry_within_limit(self, db):
        """Test that retries within limit should continue."""
        project = models.Project(name="Test")
        db.add(project)
        db.commit()

        job = models.Job(
            project_id=project.id,
            type="test",
            payload={},
            retry_count=2,  # 2 retries so far
            max_retries=3
        )
        db.add(job)
        db.commit()

        assert RetryManager.should_retry(job, max_retries=3) is True

    def test_should_not_retry_at_limit(self, db):
        """Test that retries at limit should stop."""
        project = models.Project(name="Test")
        db.add(project)
        db.commit()

        job = models.Job(
            project_id=project.id,
            type="test",
            payload={},
            retry_count=3,  # Already at max
            max_retries=3
        )
        db.add(job)
        db.commit()

        assert RetryManager.should_retry(job, max_retries=3) is False

    def test_calculate_next_retry_exponential(self):
        """Test exponential backoff calculation."""
        # First retry: 60s
        retry_at = RetryManager.calculate_next_retry(retry_count=0, base_delay=60)
        expected = datetime.utcnow() + timedelta(seconds=60)
        assert abs((retry_at - expected).total_seconds()) < 1  # Within 1 second

        # Second retry: 120s
        retry_at = RetryManager.calculate_next_retry(retry_count=1, base_delay=60)
        expected = datetime.utcnow() + timedelta(seconds=120)
        assert abs((retry_at - expected).total_seconds()) < 1

        # Third retry: 240s
        retry_at = RetryManager.calculate_next_retry(retry_count=2, base_delay=60)
        expected = datetime.utcnow() + timedelta(seconds=240)
        assert abs((retry_at - expected).total_seconds()) < 1

    def test_schedule_retry(self, db, mock_redis):
        """Test scheduling a retry."""
        project = models.Project(name="Test")
        db.add(project)
        db.commit()

        job = models.Job(
            project_id=project.id,
            type="test",
            payload={},
            retry_count=0,
            status="failed"
        )
        db.add(job)
        db.commit()

        RetryManager.schedule_retry(job, db, mock_redis, "Test error")

        # Check job was updated
        db.refresh(job)
        assert job.retry_count == 1
        assert job.status == "retrying"
        assert job.last_error == "Test error"
        assert job.next_retry_at is not None

        # Check Redis was called
        mock_redis.lpush.assert_called_once()


class TestCircuitBreaker:
    """Test circuit breaker pattern."""

    def test_circuit_closed_initially(self):
        """Test circuit breaker starts in CLOSED state."""
        cb = CircuitBreaker(failure_threshold=5, timeout=60)
        assert cb.state == "CLOSED"
        assert cb.failure_count == 0

    def test_circuit_stays_closed_on_success(self):
        """Test circuit stays closed when calls succeed."""
        cb = CircuitBreaker(failure_threshold=5, timeout=60)

        # Successful call
        def success_func():
            return "success"

        result = cb.call(success_func)
        assert result == "success"
        assert cb.state == "CLOSED"
        assert cb.failure_count == 0

    def test_circuit_opens_after_threshold(self):
        """Test circuit opens after failure threshold."""
        cb = CircuitBreaker(failure_threshold=3, timeout=60)

        def failing_func():
            raise Exception("Test failure")

        # First 2 failures
        for i in range(2):
            with pytest.raises(Exception):
                cb.call(failing_func)
            assert cb.state == "CLOSED"

        # Third failure should open circuit
        with pytest.raises(Exception):
            cb.call(failing_func)
        assert cb.state == "OPEN"
        assert cb.failure_count == 3

    def test_circuit_open_blocks_calls(self):
        """Test that OPEN circuit blocks calls."""
        cb = CircuitBreaker(failure_threshold=2, timeout=60)

        def failing_func():
            raise Exception("Test failure")

        # Fail enough times to open circuit
        for i in range(2):
            with pytest.raises(Exception):
                cb.call(failing_func)

        assert cb.state == "OPEN"

        # Next call should be blocked by circuit breaker
        with pytest.raises(Exception) as exc_info:
            cb.call(failing_func)
        assert "Circuit breaker is OPEN" in str(exc_info.value)

    def test_circuit_half_open_after_timeout(self):
        """Test circuit enters HALF_OPEN after timeout."""
        cb = CircuitBreaker(failure_threshold=2, timeout=1)  # 1 second timeout

        def failing_func():
            raise Exception("Test failure")

        # Open the circuit
        for i in range(2):
            with pytest.raises(Exception):
                cb.call(failing_func)

        assert cb.state == "OPEN"

        # Wait for timeout
        time.sleep(1.1)

        # Next call should enter HALF_OPEN state
        def success_func():
            return "success"

        result = cb.call(success_func)
        assert result == "success"
        assert cb.state == "CLOSED"  # Success in HALF_OPEN should close circuit

    def test_circuit_reset(self):
        """Test manual circuit reset."""
        cb = CircuitBreaker(failure_threshold=2, timeout=60)

        def failing_func():
            raise Exception("Test failure")

        # Open the circuit
        for i in range(2):
            with pytest.raises(Exception):
                cb.call(failing_func)

        assert cb.state == "OPEN"

        # Manual reset
        cb.reset()
        assert cb.state == "CLOSED"
        assert cb.failure_count == 0


class TestHandleJobFailure:
    """Test job failure handling."""

    def test_handle_failure_schedules_retry(self, db, mock_redis):
        """Test that job failure schedules retry within limit."""
        project = models.Project(name="Test")
        db.add(project)
        db.commit()

        job = models.Job(
            project_id=project.id,
            type="test",
            payload={},
            retry_count=0,
            max_retries=3,
            status="running"
        )
        db.add(job)
        db.commit()

        handle_job_failure(job, db, mock_redis, "Test error", max_retries=3)

        db.refresh(job)
        assert job.status == "retrying"
        assert job.retry_count == 1
        assert job.last_error == "Test error"
        mock_redis.lpush.assert_called()  # Should push to retry queue

    def test_handle_failure_moves_to_dlq(self, db, mock_redis):
        """Test that job failure moves to DLQ after max retries."""
        project = models.Project(name="Test")
        db.add(project)
        db.commit()

        job = models.Job(
            project_id=project.id,
            type="test",
            payload={},
            retry_count=3,  # Already at max
            max_retries=3,
            status="running"
        )
        db.add(job)
        db.commit()

        handle_job_failure(job, db, mock_redis, "Final error", max_retries=3)

        db.refresh(job)
        assert job.status == "dead_letter"
        assert "Max retries (3) exceeded" in job.failure_reason
        # Should push to DLQ
        calls = [call for call in mock_redis.lpush.call_args_list if "dead_letter_queue" in str(call)]
        assert len(calls) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
