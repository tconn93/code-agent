"""
Monitoring, metrics, and health checks for the AI Agent Platform.
"""
from prometheus_client import Counter, Histogram, Gauge, Info, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Response
from typing import Dict, Any
import psutil
import time
import logging
from datetime import datetime
from sqlalchemy.orm import Session
import redis

logger = logging.getLogger(__name__)


# ============================================================================
# Prometheus Metrics
# ============================================================================

# Application info
app_info = Info('agent_platform_app', 'Application information')
app_info.info({
    'version': '2.0.0',
    'name': 'AI Agent Platform'
})

# Job metrics
job_total = Counter(
    'agent_platform_jobs_total',
    'Total number of jobs created',
    ['type', 'project_id']
)

job_completed = Counter(
    'agent_platform_jobs_completed_total',
    'Total number of completed jobs',
    ['type', 'project_id']
)

job_failed = Counter(
    'agent_platform_jobs_failed_total',
    'Total number of failed jobs',
    ['type', 'project_id', 'reason']
)

job_duration = Histogram(
    'agent_platform_job_duration_seconds',
    'Job execution duration in seconds',
    ['type', 'project_id'],
    buckets=[1, 5, 10, 30, 60, 120, 300, 600, 1800, 3600]  # 1s to 1h
)

# Cost metrics
job_cost = Histogram(
    'agent_platform_job_cost_dollars',
    'Job cost in USD',
    ['type', 'project_id', 'provider'],
    buckets=[0.001, 0.01, 0.1, 1, 5, 10, 25, 50, 100]
)

tokens_used = Counter(
    'agent_platform_tokens_used_total',
    'Total tokens used',
    ['provider', 'model', 'token_type']  # token_type: input or output
)

# Agent metrics
active_agents = Gauge(
    'agent_platform_active_agents',
    'Number of active agents',
    ['type', 'provider']
)

agent_jobs = Gauge(
    'agent_platform_agent_jobs',
    'Number of jobs assigned to agent',
    ['agent_id', 'agent_name']
)

# Queue metrics
queue_size = Gauge(
    'agent_platform_queue_size',
    'Number of jobs in queue',
    ['queue_name']
)

# Error metrics
errors_total = Counter(
    'agent_platform_errors_total',
    'Total number of errors',
    ['error_type', 'component']
)

retry_count = Counter(
    'agent_platform_retries_total',
    'Total number of job retries',
    ['job_id']
)

dead_letter_queue_size = Gauge(
    'agent_platform_dlq_size',
    'Number of jobs in dead letter queue'
)

# API metrics
http_requests_total = Counter(
    'agent_platform_http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

http_request_duration = Histogram(
    'agent_platform_http_request_duration_seconds',
    'HTTP request duration',
    ['method', 'endpoint'],
    buckets=[0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1, 2, 5]
)

# System metrics
cpu_usage = Gauge('agent_platform_cpu_usage_percent', 'CPU usage percentage')
memory_usage = Gauge('agent_platform_memory_usage_bytes', 'Memory usage in bytes')
disk_usage = Gauge('agent_platform_disk_usage_percent', 'Disk usage percentage')


# ============================================================================
# Metric Collection Functions
# ============================================================================

def record_job_created(job_type: str, project_id: int):
    """Record job creation."""
    job_total.labels(type=job_type, project_id=str(project_id)).inc()


def record_job_completed(job_type: str, project_id: int, duration_seconds: float):
    """Record job completion."""
    job_completed.labels(type=job_type, project_id=str(project_id)).inc()
    job_duration.labels(type=job_type, project_id=str(project_id)).observe(duration_seconds)


def record_job_failed(job_type: str, project_id: int, reason: str):
    """Record job failure."""
    job_failed.labels(type=job_type, project_id=str(project_id), reason=reason).inc()


def record_job_cost(job_type: str, project_id: int, provider: str, cost: float):
    """Record job cost."""
    job_cost.labels(type=job_type, project_id=str(project_id), provider=provider).observe(cost)


def record_tokens_used(provider: str, model: str, input_tokens: int, output_tokens: int):
    """Record token usage."""
    tokens_used.labels(provider=provider, model=model, token_type='input').inc(input_tokens)
    tokens_used.labels(provider=provider, model=model, token_type='output').inc(output_tokens)


def record_error(error_type: str, component: str):
    """Record error occurrence."""
    errors_total.labels(error_type=error_type, component=component).inc()


def update_queue_metrics(redis_client: redis.Redis):
    """Update queue size metrics from Redis."""
    try:
        # Incoming jobs queue
        incoming_size = redis_client.llen("incoming_jobs")
        queue_size.labels(queue_name="incoming_jobs").set(incoming_size)

        # Retry queue
        retry_size = redis_client.llen("retry_queue")
        queue_size.labels(queue_name="retry_queue").set(retry_size)

        # Dead letter queue
        dlq_size = redis_client.llen("dead_letter_queue")
        dead_letter_queue_size.set(dlq_size)

    except Exception as e:
        logger.error(f"Failed to update queue metrics: {e}")


def update_system_metrics():
    """Update system resource metrics."""
    try:
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_usage.set(cpu_percent)

        # Memory usage
        memory = psutil.virtual_memory()
        memory_usage.set(memory.used)

        # Disk usage
        disk = psutil.disk_usage('/')
        disk_usage.set(disk.percent)

    except Exception as e:
        logger.error(f"Failed to update system metrics: {e}")


def update_agent_metrics(db: Session):
    """Update agent metrics from database."""
    try:
        from services.api.models import Agent, Job

        # Active agents by type and provider
        agents = db.query(Agent).filter(Agent.status == 'idle').all()

        # Reset gauges
        for agent in agents:
            active_agents.labels(type=agent.type, provider=agent.provider).set(1)

            # Jobs per agent
            job_count = db.query(Job).filter(
                Job.assigned_agent_id == agent.id,
                Job.status.in_(['pending', 'running'])
            ).count()

            agent_jobs.labels(agent_id=str(agent.id), agent_name=agent.name).set(job_count)

    except Exception as e:
        logger.error(f"Failed to update agent metrics: {e}")


# ============================================================================
# Health Checks
# ============================================================================

class HealthStatus:
    """Health check status."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


def check_database_health(db: Session) -> Dict[str, Any]:
    """Check database connectivity and performance."""
    start_time = time.time()

    try:
        # Simple query to check connection
        db.execute("SELECT 1")
        duration = time.time() - start_time

        return {
            "status": HealthStatus.HEALTHY,
            "response_time_ms": round(duration * 1000, 2),
            "message": "Database connection OK"
        }

    except Exception as e:
        return {
            "status": HealthStatus.UNHEALTHY,
            "error": str(e),
            "message": "Database connection failed"
        }


def check_redis_health(redis_client: redis.Redis) -> Dict[str, Any]:
    """Check Redis connectivity and performance."""
    start_time = time.time()

    try:
        # Ping Redis
        redis_client.ping()
        duration = time.time() - start_time

        # Check queue sizes
        incoming = redis_client.llen("incoming_jobs")
        dlq = redis_client.llen("dead_letter_queue")

        return {
            "status": HealthStatus.HEALTHY,
            "response_time_ms": round(duration * 1000, 2),
            "queues": {
                "incoming_jobs": incoming,
                "dead_letter_queue": dlq
            },
            "message": "Redis connection OK"
        }

    except Exception as e:
        return {
            "status": HealthStatus.UNHEALTHY,
            "error": str(e),
            "message": "Redis connection failed"
        }


def check_disk_space() -> Dict[str, Any]:
    """Check disk space availability."""
    try:
        disk = psutil.disk_usage('/')

        if disk.percent > 90:
            status = HealthStatus.UNHEALTHY
            message = f"Disk space critical: {disk.percent}%"
        elif disk.percent > 80:
            status = HealthStatus.DEGRADED
            message = f"Disk space warning: {disk.percent}%"
        else:
            status = HealthStatus.HEALTHY
            message = f"Disk space OK: {disk.percent}%"

        return {
            "status": status,
            "percent_used": disk.percent,
            "free_gb": round(disk.free / (1024**3), 2),
            "total_gb": round(disk.total / (1024**3), 2),
            "message": message
        }

    except Exception as e:
        return {
            "status": HealthStatus.UNHEALTHY,
            "error": str(e),
            "message": "Failed to check disk space"
        }


def check_memory() -> Dict[str, Any]:
    """Check memory usage."""
    try:
        memory = psutil.virtual_memory()

        if memory.percent > 90:
            status = HealthStatus.UNHEALTHY
            message = f"Memory critical: {memory.percent}%"
        elif memory.percent > 80:
            status = HealthStatus.DEGRADED
            message = f"Memory warning: {memory.percent}%"
        else:
            status = HealthStatus.HEALTHY
            message = f"Memory OK: {memory.percent}%"

        return {
            "status": status,
            "percent_used": memory.percent,
            "used_gb": round(memory.used / (1024**3), 2),
            "total_gb": round(memory.total / (1024**3), 2),
            "message": message
        }

    except Exception as e:
        return {
            "status": HealthStatus.UNHEALTHY,
            "error": str(e),
            "message": "Failed to check memory"
        }


def comprehensive_health_check(db: Session, redis_client: redis.Redis) -> Dict[str, Any]:
    """
    Perform comprehensive health check of all system components.

    Returns:
        Health status and details
    """
    checks = {
        "database": check_database_health(db),
        "redis": check_redis_health(redis_client),
        "disk": check_disk_space(),
        "memory": check_memory()
    }

    # Determine overall status
    statuses = [check["status"] for check in checks.values()]

    if HealthStatus.UNHEALTHY in statuses:
        overall_status = HealthStatus.UNHEALTHY
    elif HealthStatus.DEGRADED in statuses:
        overall_status = HealthStatus.DEGRADED
    else:
        overall_status = HealthStatus.HEALTHY

    return {
        "status": overall_status,
        "timestamp": datetime.utcnow().isoformat(),
        "checks": checks,
        "version": "2.0.0"
    }


# ============================================================================
# Monitoring Endpoints
# ============================================================================

def metrics_endpoint() -> Response:
    """Prometheus metrics endpoint."""
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


def health_endpoint(db: Session, redis_client: redis.Redis) -> Dict[str, Any]:
    """Health check endpoint."""
    return comprehensive_health_check(db, redis_client)


def readiness_endpoint(db: Session, redis_client: redis.Redis) -> Dict[str, Any]:
    """
    Readiness check for Kubernetes.

    Returns 200 if ready to serve traffic, 503 otherwise.
    """
    health = comprehensive_health_check(db, redis_client)

    # Ready if not unhealthy
    is_ready = health["status"] != HealthStatus.UNHEALTHY

    return {
        "ready": is_ready,
        "status": health["status"],
        "timestamp": health["timestamp"]
    }


def liveness_endpoint() -> Dict[str, Any]:
    """
    Liveness check for Kubernetes.

    Returns 200 if application is alive, 503 if it should be restarted.
    """
    # Simple check - if we can respond, we're alive
    return {
        "alive": True,
        "timestamp": datetime.utcnow().isoformat()
    }
