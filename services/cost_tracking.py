"""
Cost tracking and budget enforcement system.
"""
from typing import Dict, Optional
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


# Provider pricing (USD per 1M tokens)
# Prices as of 2025 - update these regularly
PROVIDER_PRICING = {
    "anthropic": {
        "claude-sonnet-4-20250514": {"input": 3.00, "output": 15.00},
        "claude-sonnet-4-5-20250929": {"input": 3.00, "output": 15.00},
        "claude-haiku-4-5-20251001": {"input": 0.25, "output": 1.25},
        "claude-opus-4-5-20251101": {"input": 15.00, "output": 75.00},
        # Default for unknown models
        "default": {"input": 3.00, "output": 15.00}
    },
    "openai": {
        "gpt-5.1": {"input": 10.00, "output": 30.00},
        "gpt-5-mini": {"input": 0.15, "output": 0.60},
        "gpt-5-nano": {"input": 0.10, "output": 0.40},
        "gpt-5-pro": {"input": 15.00, "output": 60.00},
        "gpt-4o": {"input": 5.00, "output": 15.00},
        "default": {"input": 5.00, "output": 15.00}
    },
    "google": {
        "gemini-3.0-pro": {"input": 7.00, "output": 21.00},
        "gemini-2.5-pro": {"input": 1.25, "output": 5.00},
        "gemini-2.5-flash": {"input": 0.075, "output": 0.30},
        "gemini-2.0-flash": {"input": 0.05, "output": 0.20},
        "default": {"input": 1.00, "output": 3.00}
    },
    "groq": {
        "llama-3.3-70b-versatile": {"input": 0.59, "output": 0.79},
        "llama-3.1-8b-instant": {"input": 0.05, "output": 0.08},
        "gemma2-27b-it": {"input": 0.20, "output": 0.20},
        "mixtral-8x7b-32768": {"input": 0.27, "output": 0.27},
        "default": {"input": 0.20, "output": 0.20}
    },
    "xai": {
        "grok-4-1-fast-reasoning": {"input": 5.00, "output": 15.00},
        "grok-4-1-fast-non-reasoning": {"input": 1.00, "output": 5.00},
        "grok-code-fast-1": {"input": 2.00, "output": 10.00},
        "grok-4-fast-reasoning": {"input": 5.00, "output": 15.00},
        "grok-4-fast-non-reasoning": {"input": 1.00, "output": 5.00},
        "grok-3-mini": {"input": 0.50, "output": 2.00},
        "grok-3": {"input": 3.00, "output": 10.00},
        "default": {"input": 2.00, "output": 8.00}
    }
}


def calculate_cost(
    provider: str,
    model: str,
    input_tokens: int,
    output_tokens: int
) -> float:
    """
    Calculate cost based on token usage and provider pricing.

    Args:
        provider: AI provider name (anthropic, openai, google, groq, xai)
        model: Model name
        input_tokens: Number of input tokens
        output_tokens: Number of output tokens

    Returns:
        Cost in USD
    """
    provider = provider.lower()

    # Get pricing for provider
    if provider not in PROVIDER_PRICING:
        logger.warning(f"Unknown provider '{provider}', using default pricing")
        pricing = {"input": 1.00, "output": 3.00}
    else:
        provider_prices = PROVIDER_PRICING[provider]
        pricing = provider_prices.get(model, provider_prices.get("default", {"input": 1.00, "output": 3.00}))

    # Calculate cost (pricing is per 1M tokens)
    input_cost = (input_tokens / 1_000_000) * pricing["input"]
    output_cost = (output_tokens / 1_000_000) * pricing["output"]
    total_cost = input_cost + output_cost

    logger.debug(
        f"Cost calculation: provider={provider}, model={model}, "
        f"input={input_tokens} tokens (${input_cost:.4f}), "
        f"output={output_tokens} tokens (${output_cost:.4f}), "
        f"total=${total_cost:.4f}"
    )

    return round(total_cost, 4)


def update_job_cost(job, provider: str, model: str):
    """
    Update job cost based on token usage.

    Args:
        job: Job database model
        provider: AI provider name
        model: Model name
    """
    if not job.tokens_used_input or not job.tokens_used_output:
        logger.warning(f"Job {job.id} missing token usage data")
        return

    cost = calculate_cost(
        provider=provider,
        model=model,
        input_tokens=job.tokens_used_input,
        output_tokens=job.tokens_used_output
    )

    job.actual_cost = cost


def get_project_cost(project_id: int, db: Session, period_days: Optional[int] = None) -> Dict:
    """
    Get total cost for a project.

    Args:
        project_id: Project ID
        db: Database session
        period_days: Optional number of days to look back (None = all time)

    Returns:
        Dictionary with cost breakdown
    """
    from services.api.models import Job

    query = db.query(Job).filter(Job.project_id == project_id)

    # Filter by time period if specified
    if period_days:
        cutoff_date = datetime.utcnow() - timedelta(days=period_days)
        query = query.filter(Job.created_at >= cutoff_date)

    jobs = query.all()

    total_cost = sum(job.actual_cost or 0 for job in jobs)
    total_jobs = len(jobs)
    completed_jobs = sum(1 for job in jobs if job.status == "completed")
    failed_jobs = sum(1 for job in jobs if job.status in ["failed", "dead_letter"])

    return {
        "project_id": project_id,
        "total_cost": round(total_cost, 2),
        "total_jobs": total_jobs,
        "completed_jobs": completed_jobs,
        "failed_jobs": failed_jobs,
        "average_cost_per_job": round(total_cost / total_jobs, 2) if total_jobs > 0 else 0,
        "period_days": period_days or "all_time"
    }


def get_team_cost(team_id: int, db: Session, period_days: Optional[int] = None) -> Dict:
    """
    Get total cost for a team.

    Args:
        team_id: Team ID
        db: Database session
        period_days: Optional number of days to look back

    Returns:
        Dictionary with cost breakdown
    """
    from services.api.models import Job, Project

    # Get all projects for team
    projects = db.query(Project).filter(Project.team_id == team_id).all()
    project_ids = [p.id for p in projects]

    if not project_ids:
        return {
            "team_id": team_id,
            "total_cost": 0,
            "total_jobs": 0,
            "projects": []
        }

    query = db.query(Job).filter(Job.project_id.in_(project_ids))

    if period_days:
        cutoff_date = datetime.utcnow() - timedelta(days=period_days)
        query = query.filter(Job.created_at >= cutoff_date)

    jobs = query.all()

    total_cost = sum(job.actual_cost or 0 for job in jobs)

    # Get cost per project
    project_costs = []
    for project in projects:
        project_cost = get_project_cost(project.id, db, period_days)
        if project_cost["total_cost"] > 0:
            project_costs.append({
                "project_id": project.id,
                "project_name": project.name,
                "cost": project_cost["total_cost"]
            })

    return {
        "team_id": team_id,
        "total_cost": round(total_cost, 2),
        "total_jobs": len(jobs),
        "projects": sorted(project_costs, key=lambda x: x["cost"], reverse=True),
        "period_days": period_days or "all_time"
    }


def check_budget_limit(project_id: int, db: Session) -> Dict:
    """
    Check if project is approaching or exceeding budget limit.

    Args:
        project_id: Project ID
        db: Database session

    Returns:
        Dictionary with budget status
    """
    from services.api.models import Project

    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise ValueError(f"Project {project_id} not found")

    # Get project cost
    cost_info = get_project_cost(project_id, db)
    actual_cost = cost_info["total_cost"]

    # Check against allocated budget
    budget_allocated = float(project.budget_allocated or 0)

    if budget_allocated == 0:
        return {
            "project_id": project_id,
            "has_budget": False,
            "status": "no_budget_set"
        }

    percentage_used = (actual_cost / budget_allocated) * 100
    remaining_budget = budget_allocated - actual_cost

    # Determine status
    if percentage_used >= 100:
        status = "exceeded"
    elif percentage_used >= 95:
        status = "critical"  # 95%+
    elif percentage_used >= 80:
        status = "warning"   # 80%+
    else:
        status = "ok"

    return {
        "project_id": project_id,
        "has_budget": True,
        "budget_allocated": budget_allocated,
        "actual_cost": actual_cost,
        "remaining_budget": round(remaining_budget, 2),
        "percentage_used": round(percentage_used, 1),
        "status": status
    }


def enforce_budget_limit(project_id: int, db: Session) -> bool:
    """
    Check if new jobs should be allowed based on budget.

    Args:
        project_id: Project ID
        db: Database session

    Returns:
        True if jobs should be allowed, False if budget exceeded
    """
    budget_status = check_budget_limit(project_id, db)

    if not budget_status["has_budget"]:
        return True  # No budget set, allow all jobs

    if budget_status["status"] == "exceeded":
        logger.warning(f"Project {project_id} budget exceeded, blocking new jobs")
        return False

    return True


def get_cost_report(db: Session, period_days: int = 30) -> Dict:
    """
    Generate platform-wide cost report.

    Args:
        db: Database session
        period_days: Number of days to include in report

    Returns:
        Dictionary with platform cost breakdown
    """
    from services.api.models import Job, Project, Team

    cutoff_date = datetime.utcnow() - timedelta(days=period_days)

    # Get all jobs in period
    jobs = db.query(Job).filter(Job.created_at >= cutoff_date).all()

    total_cost = sum(job.actual_cost or 0 for job in jobs)
    total_tokens = sum(job.tokens_used_total or 0 for job in jobs)

    # Cost by project
    projects = db.query(Project).all()
    project_costs = []
    for project in projects:
        cost_info = get_project_cost(project.id, db, period_days)
        if cost_info["total_cost"] > 0:
            project_costs.append({
                "project_id": project.id,
                "project_name": project.name,
                "cost": cost_info["total_cost"],
                "jobs": cost_info["total_jobs"]
            })

    # Cost by team
    teams = db.query(Team).all()
    team_costs = []
    for team in teams:
        cost_info = get_team_cost(team.id, db, period_days)
        if cost_info["total_cost"] > 0:
            team_costs.append({
                "team_id": team.id,
                "team_name": team.name,
                "cost": cost_info["total_cost"]
            })

    return {
        "period_days": period_days,
        "total_cost": round(total_cost, 2),
        "total_jobs": len(jobs),
        "total_tokens": total_tokens,
        "average_cost_per_job": round(total_cost / len(jobs), 2) if len(jobs) > 0 else 0,
        "top_projects": sorted(project_costs, key=lambda x: x["cost"], reverse=True)[:10],
        "top_teams": sorted(team_costs, key=lambda x: x["cost"], reverse=True)[:10]
    }
