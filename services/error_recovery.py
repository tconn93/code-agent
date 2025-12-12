"""
Error recovery system for handling job failures, retries, and dead letter queue.
"""
import redis
import time
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session
import logging

logger = logging.getLogger(__name__)


class CircuitBreaker:
    """
    Circuit breaker pattern for AI provider API calls.

    States:
    - CLOSED: Normal operation, requests pass through
    - OPEN: Failure threshold exceeded, requests fail immediately
    - HALF_OPEN: Testing if service has recovered
    """

    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        """
        Initialize circuit breaker.

        Args:
            failure_threshold: Number of failures before opening circuit
            timeout: Seconds to wait before trying again (HALF_OPEN state)
        """
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN

    def call(self, func, *args, **kwargs):
        """
        Execute function with circuit breaker protection.

        Args:
            func: Function to execute
            *args, **kwargs: Arguments to pass to function

        Returns:
            Result of function call

        Raises:
            Exception: If circuit is OPEN or function fails
        """
        if self.state == "OPEN":
            # Check if timeout has passed
            if self.last_failure_time and \
               (datetime.now() - self.last_failure_time).total_seconds() > self.timeout:
                self.state = "HALF_OPEN"
                logger.info("Circuit breaker entering HALF_OPEN state")
            else:
                raise Exception("Circuit breaker is OPEN - service unavailable")

        try:
            result = func(*args, **kwargs)

            # Success - reset circuit breaker
            if self.state == "HALF_OPEN":
                self.state = "CLOSED"
                self.failure_count = 0
                logger.info("Circuit breaker reset to CLOSED state")

            return result

        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = datetime.now()

            if self.failure_count >= self.failure_threshold:
                self.state = "OPEN"
                logger.error(f"Circuit breaker opened after {self.failure_count} failures")

            raise e

    def reset(self):
        """Manually reset circuit breaker."""
        self.state = "CLOSED"
        self.failure_count = 0
        self.last_failure_time = None


class RetryManager:
    """Manages retry logic with exponential backoff."""

    @staticmethod
    def should_retry(job, max_retries: int = 3) -> bool:
        """
        Determine if job should be retried.

        Args:
            job: Job database model
            max_retries: Maximum number of retries allowed

        Returns:
            True if job should be retried
        """
        return job.retry_count < max_retries

    @staticmethod
    def calculate_next_retry(retry_count: int, base_delay: int = 60) -> datetime:
        """
        Calculate next retry time using exponential backoff.

        Args:
            retry_count: Current retry attempt number
            base_delay: Base delay in seconds (default 60s)

        Returns:
            DateTime for next retry
        """
        # Exponential backoff: base_delay * (2 ^ retry_count)
        # retry_count 0: 60s
        # retry_count 1: 120s (2 min)
        # retry_count 2: 240s (4 min)
        # retry_count 3: 480s (8 min)
        delay_seconds = base_delay * (2 ** retry_count)
        return datetime.utcnow() + timedelta(seconds=delay_seconds)

    @staticmethod
    def schedule_retry(job, db: Session, redis_client: redis.Redis, error_message: str):
        """
        Schedule job for retry.

        Args:
            job: Job database model
            db: Database session
            redis_client: Redis client
            error_message: Error message from failed attempt
        """
        from services.api import models

        job.retry_count += 1
        job.last_error = error_message
        job.next_retry_at = RetryManager.calculate_next_retry(job.retry_count)
        job.status = "retrying"
        job.updated_at = datetime.utcnow()

        db.commit()

        logger.info(
            f"Job {job.id} scheduled for retry #{job.retry_count} at {job.next_retry_at}"
        )

        # Push to retry queue with delay
        # Note: This requires a separate worker to process retries at scheduled time
        retry_data = {
            "job_id": job.id,
            "retry_at": job.next_retry_at.isoformat(),
            "retry_count": job.retry_count
        }

        import json
        redis_client.lpush("retry_queue", json.dumps(retry_data))


class DeadLetterQueue:
    """Manages dead letter queue for permanently failed jobs."""

    @staticmethod
    def move_to_dlq(job, db: Session, redis_client: redis.Redis, reason: str):
        """
        Move job to dead letter queue.

        Args:
            job: Job database model
            db: Database session
            redis_client: Redis client
            reason: Reason for permanent failure
        """
        from services.api import models

        job.status = "dead_letter"
        job.failure_reason = reason
        job.updated_at = datetime.utcnow()
        job.completed_at = datetime.utcnow()

        db.commit()

        logger.error(f"Job {job.id} moved to dead letter queue: {reason}")

        # Push to DLQ for manual review
        import json
        dlq_data = {
            "job_id": job.id,
            "project_id": job.project_id,
            "type": job.type,
            "failure_reason": reason,
            "retry_count": job.retry_count,
            "moved_at": datetime.utcnow().isoformat()
        }

        redis_client.lpush("dead_letter_queue", json.dumps(dlq_data))

        # Optional: Send notification/alert about DLQ job
        # This could trigger emails, Slack messages, etc.

    @staticmethod
    def get_dlq_jobs(redis_client: redis.Redis, limit: int = 100):
        """
        Retrieve jobs from dead letter queue.

        Args:
            redis_client: Redis client
            limit: Maximum number of jobs to retrieve

        Returns:
            List of dead letter queue jobs
        """
        import json

        jobs = []
        for _ in range(limit):
            job_data = redis_client.rpop("dead_letter_queue")
            if not job_data:
                break
            jobs.append(json.loads(job_data))

        return jobs

    @staticmethod
    def retry_dlq_job(job_id: int, db: Session, redis_client: redis.Redis):
        """
        Retry a job from the dead letter queue.

        Args:
            job_id: Job ID to retry
            db: Database session
            redis_client: Redis client
        """
        from services.api import models

        job = db.query(models.Job).filter(models.Job.id == job_id).first()
        if not job or job.status != "dead_letter":
            raise ValueError(f"Job {job_id} not found in dead letter queue")

        # Reset job for retry
        job.status = "pending"
        job.retry_count = 0
        job.failure_reason = None
        job.last_error = None
        job.next_retry_at = None
        job.updated_at = datetime.utcnow()

        db.commit()

        # Push back to incoming queue
        redis_client.lpush("incoming_jobs", job_id)

        logger.info(f"Job {job_id} restored from dead letter queue")


def handle_job_failure(
    job,
    db: Session,
    redis_client: redis.Redis,
    error_message: str,
    max_retries: int = 3
):
    """
    Handle job failure with retry or DLQ logic.

    Args:
        job: Job database model
        db: Database session
        redis_client: Redis client
        error_message: Error message from failure
        max_retries: Maximum retry attempts
    """
    logger.warning(f"Job {job.id} failed: {error_message}")

    if RetryManager.should_retry(job, max_retries):
        RetryManager.schedule_retry(job, db, redis_client, error_message)
    else:
        reason = f"Max retries ({max_retries}) exceeded. Last error: {error_message}"
        DeadLetterQueue.move_to_dlq(job, db, redis_client, reason)


class RetryWorker:
    """Worker that processes retry queue at scheduled times."""

    def __init__(self, redis_client: redis.Redis, db_session_factory):
        self.redis_client = redis_client
        self.db_session_factory = db_session_factory

    def process_retry_queue(self):
        """
        Process jobs in retry queue that are ready to be retried.
        """
        import json
        from services.api import models

        while True:
            # Get all jobs from retry queue
            retry_data = self.redis_client.rpop("retry_queue")
            if not retry_data:
                time.sleep(5)  # Wait before checking again
                continue

            retry_info = json.loads(retry_data)
            retry_at = datetime.fromisoformat(retry_info["retry_at"])

            # Check if it's time to retry
            if datetime.utcnow() < retry_at:
                # Not yet time, push back to queue
                self.redis_client.lpush("retry_queue", retry_data)
                time.sleep(5)
                continue

            # Time to retry - push to incoming queue
            job_id = retry_info["job_id"]

            db = self.db_session_factory()
            try:
                job = db.query(models.Job).filter(models.Job.id == job_id).first()
                if job and job.status == "retrying":
                    job.status = "pending"
                    job.updated_at = datetime.utcnow()
                    db.commit()

                    self.redis_client.lpush("incoming_jobs", job_id)
                    logger.info(f"Job {job_id} retry #{retry_info['retry_count']} queued")
            finally:
                db.close()
