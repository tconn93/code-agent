"""
Cost tracking and reporting endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from services.api.database import get_db
from services.api.auth import get_current_user, require_admin
from services.api import models
from services.cost_tracking import (
    get_project_cost,
    get_team_cost,
    check_budget_limit,
    get_cost_report
)

router = APIRouter(prefix="/costs", tags=["costs"])


@router.get("/projects/{project_id}")
def get_project_cost_endpoint(
    project_id: int,
    period_days: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Get cost breakdown for a project."""
    # Check access to project
    from services.api.auth import check_project_access
    check_project_access(project_id, current_user, db, "read")

    return get_project_cost(project_id, db, period_days)


@router.get("/projects/{project_id}/budget")
def get_project_budget_status(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Check budget status for a project."""
    from services.api.auth import check_project_access
    check_project_access(project_id, current_user, db, "read")

    return check_budget_limit(project_id, db)


@router.get("/teams/{team_id}")
def get_team_cost_endpoint(
    team_id: int,
    period_days: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Get cost breakdown for a team."""
    # Check if user is part of team or is admin
    if current_user.role != "admin":
        team_member = db.query(models.TeamMember).filter(
            models.TeamMember.team_id == team_id,
            models.TeamMember.user_id == current_user.id
        ).first()

        if not team_member:
            raise HTTPException(status_code=403, detail="Access denied")

    return get_team_cost(team_id, db, period_days)


@router.get("/report")
def get_platform_cost_report(
    period_days: int = 30,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin)
):
    """Get platform-wide cost report (admin only)."""
    return get_cost_report(db, period_days)


@router.get("/jobs/{job_id}")
def get_job_cost(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Get cost details for a specific job."""
    job = db.query(models.Job).filter(models.Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Check access to project
    from services.api.auth import check_project_access
    check_project_access(job.project_id, current_user, db, "read")

    return {
        "job_id": job.id,
        "project_id": job.project_id,
        "type": job.type,
        "status": job.status,
        "tokens_used_input": job.tokens_used_input,
        "tokens_used_output": job.tokens_used_output,
        "tokens_used_total": job.tokens_used_total,
        "actual_cost": job.actual_cost,
        "estimated_cost": job.estimated_cost,
        "duration": job.actual_duration,
        "created_at": job.created_at.isoformat() if job.created_at else None,
        "completed_at": job.completed_at.isoformat() if job.completed_at else None
    }
