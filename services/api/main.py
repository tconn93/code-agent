from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import update
from typing import List, Optional, Dict, Any
import redis
import os
import json
from datetime import datetime
import logging

from services.api import models, database
from services.api.database import engine, get_db
from pydantic import BaseModel
from pydantic import ConfigDict
from datetime import datetime
from providers.anthropic_provider import AnthropicProvider
from providers.openai_provider import OpenAIProvider
from providers.gemini_provider import GeminiProvider
from providers.groq_provider import GroqProvider
from providers.grok_provider import GrokProvider
from services.api.auth_routes import router as auth_router
from services.api.cost_routes import router as cost_router
from services.api.auth import get_current_user, get_current_user_optional, check_project_access

# Create tables
models.Base.metadata.create_all(bind=engine)

import docker
try:
    docker_client = docker.from_env()
except Exception as e:
    print(f"Warning: Docker not available: {e}")
    docker_client = None

app = FastAPI(title="AI Agent Platform API")

# Include routers
app.include_router(auth_router)
app.include_router(cost_router)

# Initialize Redis
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
r = redis.from_url(REDIS_URL)

# --- Pydantic Schemas ---
class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None
    repo_url: Optional[str] = None

    # Project Management & Governance
    owner_id: Optional[int] = None
    team_id: Optional[int] = None
    department: Optional[str] = None
    business_unit: Optional[str] = None
    cost_center: Optional[str] = None

    # Project Lifecycle
    status: str = "active"
    priority: str = "medium"
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    budget_allocated: Optional[float] = None

    # Approval & Review
    requires_approval: bool = False
    approved_by: Optional[int] = None
    approved_at: Optional[str] = None
    review_due_date: Optional[str] = None

    # Security & Compliance
    security_level: str = "internal"
    data_classification: Optional[str] = None
    compliance_requirements: Optional[Dict[str, Any]] = None

    # Access Control
    visibility: str = "team"
    allowed_domains: Optional[List[str]] = None
    ip_restrictions: Optional[List[str]] = None

    # Technical & Quality Metrics
    primary_language: Optional[str] = None
    frameworks: Optional[List[str]] = None
    deployment_target: Optional[str] = None

    # Quality Metrics
    code_coverage_target: float = 80.0
    test_success_rate: Optional[float] = None
    last_quality_scan: Optional[str] = None
    quality_score: Optional[float] = None

    # Integration
    webhook_urls: Optional[List[str]] = None
    api_endpoints: Optional[List[str]] = None
    external_ids: Optional[Dict[str, str]] = None

    # Business Intelligence
    estimated_cost: Optional[float] = None
    actual_cost: Optional[float] = None
    cost_per_month: Optional[float] = None

    # Performance Metrics
    deployment_frequency: Optional[str] = None
    lead_time: Optional[int] = None
    change_failure_rate: Optional[float] = None
    mttr: Optional[int] = None

    # Business Value
    business_value: Optional[str] = None
    kpis: Optional[Dict[str, Any]] = None
    stakeholders: Optional[List[Dict[str, Any]]] = None

class ProjectResponse(ProjectCreate):
    id: int
    created_at: str
    updated_at: Optional[str] = None
    version: int = 1

    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={datetime: lambda v: v.isoformat() if v else None}
    )

class JobCreate(BaseModel):
    project_id: int
    type: str # e.g. "implement_feature"
    payload: Dict[str, Any] # e.g. {"task": "Build login page"}
    assigned_agent_id: Optional[int] = None
    priority: str = "medium"
    requested_by: Optional[int] = None
    estimated_cost: Optional[float] = None
    estimated_duration: Optional[int] = None
    sla_deadline: Optional[str] = None
    review_required: bool = False
    security_level: str = "standard"
    data_sensitivity: Optional[str] = None
    environment: Optional[str] = None
    tags: Optional[Dict[str, Any]] = None

class JobResponse(JobCreate):
    id: int
    status: str
    result: Optional[Dict[str, Any]] = None
    created_at: str
    updated_at: str
    approved_by: Optional[int] = None
    approved_at: Optional[str] = None
    actual_cost: Optional[float] = None
    actual_duration: Optional[int] = None
    quality_score: Optional[float] = None
    reviewed_by: Optional[int] = None
    reviewed_at: Optional[str] = None
    retry_count: int = 0
    failure_reason: Optional[str] = None

    class Config:
        orm_mode = True

# Enterprise Model Schemas
class UserCreate(BaseModel):
    email: str
    name: str
    role: str = "developer"
    department: Optional[str] = None

class UserResponse(UserCreate):
    id: int
    is_active: bool
    created_at: str
    last_login: Optional[str] = None

    class Config:
        orm_mode = True

class TeamCreate(BaseModel):
    name: str
    description: Optional[str] = None
    department: Optional[str] = None
    manager_id: Optional[int] = None

class TeamResponse(TeamCreate):
    id: int
    created_at: str

    class Config:
        orm_mode = True

class TeamMemberCreate(BaseModel):
    team_id: int
    user_id: int
    role: str = "member"

class TeamMemberResponse(TeamMemberCreate):
    id: int
    joined_at: str

    class Config:
        orm_mode = True

class EnvironmentCreate(BaseModel):
    project_id: int
    name: str
    url: Optional[str] = None
    status: str = "active"

class EnvironmentResponse(EnvironmentCreate):
    id: int
    last_deployment: Optional[str] = None
    created_at: str

    class Config:
        orm_mode = True

class ReleaseCreate(BaseModel):
    project_id: int
    version: str
    name: Optional[str] = None
    description: Optional[str] = None
    status: str = "draft"

class ReleaseResponse(ReleaseCreate):
    id: int
    released_by: Optional[int] = None
    released_at: Optional[str] = None
    created_at: str

    class Config:
        orm_mode = True

class AuditLogResponse(BaseModel):
    id: int
    project_id: Optional[int] = None
    user_id: Optional[int] = None
    action: str
    entity_type: str
    entity_id: Optional[int] = None
    old_values: Optional[Dict[str, Any]] = None
    new_values: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None
    created_at: str

    class Config:
        orm_mode = True


class SystemConfigCreate(BaseModel):
    key: str
    value: str
    category: Optional[str] = "general"

class SystemConfigResponse(SystemConfigCreate):
    class Config:
        orm_mode = True

class AgentCreate(BaseModel):
    name: str
    type: str
    provider: str = "xai"
    model: Optional[str] = None
    owner_id: Optional[int] = None
    team_id: Optional[int] = None
    department: Optional[str] = None
    cost_per_hour: Optional[float] = None
    max_concurrent_jobs: int = 1
    priority: str = "medium"
    security_clearance: str = "standard"
    allowed_projects: Optional[List[int]] = None
    compliance_requirements: Optional[Dict[str, Any]] = None
    capabilities: Optional[Dict[str, Any]] = None
    custom_system_prompt: Optional[str] = None
    custom_system_prompt: Optional[str] = None

class AgentResponse(AgentCreate):
    id: int
    status: str
    current_job_id: Optional[int] = None
    last_heartbeat: str
    total_jobs_completed: int = 0
    total_jobs_failed: int = 0
    average_job_duration: Optional[int] = None
    success_rate: Optional[float] = None
    last_job_completed_at: Optional[str] = None
    maintenance_mode: bool = False
    maintenance_reason: Optional[str] = None
    version: Optional[str] = None
    created_at: str
    updated_at: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


# --- API Endpoints ---

@app.get("/")
def read_root():
    return {"status": "ok", "version": "2.0.0"}

# Projects
@app.post("/projects/", response_model=ProjectResponse)
def create_project(
    project: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Set owner to current user if not specified
    project_dict = project.dict()
    if not project_dict.get('owner_id'):
        project_dict['owner_id'] = current_user.id

    db_project = models.Project(**project_dict)
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    project_data = db_project.__dict__.copy()
    project_data.pop('_sa_instance_state', None)
    project_data['created_at'] = project_data['created_at'].isoformat()
    project_data['updated_at'] = project_data['updated_at'].isoformat() if project_data['updated_at'] else None
    return project_data

@app.get("/projects/", response_model=List[ProjectResponse])
def read_projects(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    projects = db.query(models.Project).offset(skip).limit(limit).all()
    formatted_projects = []
    for p in projects:
        data = p.__dict__.copy()
        data.pop('_sa_instance_state', None)
        data['created_at'] = data['created_at'].isoformat()
        data['updated_at'] = data['updated_at'].isoformat() if data['updated_at'] else None
        formatted_projects.append(data)
    return formatted_projects

@app.get("/projects/{project_id}", response_model=ProjectResponse)
def read_project(project_id: int, db: Session = Depends(get_db)):
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    project_data = project.__dict__.copy()
    project_data.pop('_sa_instance_state', None)
    project_data['created_at'] = project_data['created_at'].isoformat()
    project_data['updated_at'] = project_data['updated_at'].isoformat() if project_data['updated_at'] else None
    return project_data

# Jobs
@app.post("/jobs/", response_model=JobResponse)
def create_job(job: JobCreate, db: Session = Depends(get_db)):
    # Verify project exists
    project = db.query(models.Project).filter(models.Project.id == job.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Create Job in DB
    db_job = models.Job(**job.dict())
    db_job.status = "pending"

    # Auto-assign agent if not specified
    if not job.assigned_agent_id:
        # Find idle agent matching job type (map 'coding' -> agent type 'coding')
        agent_type = 'coding' if job.type == 'coding' else job.type  # Simple mapping
        available_agent = db.query(models.Agent).filter(
            models.Agent.type == agent_type,
            models.Agent.status == 'idle',
            models.Agent.maintenance_mode == False
        ).order_by(models.Agent.priority.desc()).first()  # Highest priority idle agent

        if available_agent:
            db_job.assigned_agent_id = available_agent.id
            print(f"Auto-assigned job {db_job.id} to agent {available_agent.id} ({available_agent.provider})")

    db.add(db_job)
    db.commit()
    db.refresh(db_job)

    # Route to incoming_jobs for orchestrator
    # Push job_id to incoming_jobs. Orchestrator routes to agent queues.
    try:
        print(f"Routing job {db_job.id} (project {db_job.project_id}, type {db_job.type}, assigned {db_job.assigned_agent_id}) to incoming_jobs")
        r.lpush("incoming_jobs", db_job.id)
        print(f"Successfully routed job {db_job.id} to incoming_jobs")
    except redis.RedisError as e:
        print(f"Redis error routing job {db_job.id}: {e}")
        db_job.status = "failed"
        db_job.logs = f"Failed to route to orchestrator: {str(e)}"
        db.commit()
        raise HTTPException(status_code=500, detail="Failed to route job to orchestrator")
    except Exception as e:
        print(f"Unexpected error routing job {db_job.id}: {e}")
        db_job.status = "failed"
        db_job.logs = f"Unexpected routing error: {str(e)}"
        db.commit()
        raise HTTPException(status_code=500, detail="Failed to route job")

    job_data = db_job.__dict__.copy()
    job_data.pop('_sa_instance_state', None)
    job_data['created_at'] = job_data['created_at'].isoformat()
    job_data['updated_at'] = job_data['updated_at'].isoformat()
    return job_data

@app.get("/jobs/", response_model=List[JobResponse])
def read_all_jobs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    jobs = db.query(models.Job).order_by(models.Job.created_at.desc()).offset(skip).limit(limit).all()
    # Manual mapping for Pydantic
    return [
        JobResponse(
            id=j.id,
            project_id=j.project_id,
            type=j.type,
            payload=j.payload,
            assigned_agent_id=j.assigned_agent_id,
            status=j.status,
            result=j.result,
            created_at=j.created_at.isoformat() if j.created_at else "",
            updated_at=j.updated_at.isoformat() if j.updated_at else ""
        ) for j in jobs
    ]

@app.get("/jobs/{job_id}", response_model=JobResponse)
def read_job(job_id: int, db: Session = Depends(get_db)):
    job = db.query(models.Job).filter(models.Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Format datetimes for Pydantic (simple approach)
    job_data = {
        'id': job.id,
        'project_id': job.project_id,
        'type': job.type,
        'payload': job.payload,
        'assigned_agent_id': job.assigned_agent_id,
        'status': job.status,
        'result': job.result,
        'created_at': job.created_at.isoformat() if job.created_at else "",
        'updated_at': job.updated_at.isoformat() if job.updated_at else "",
        'approved_by': job.approved_by,
        'approved_at': job.approved_at.isoformat() if job.approved_at else None,
        'actual_cost': job.actual_cost,
        'actual_duration': job.actual_duration,
        'quality_score': job.quality_score,
        'reviewed_by': job.reviewed_by,
        'reviewed_at': job.reviewed_at.isoformat() if job.reviewed_at else None,
        'retry_count': job.retry_count,
        'failure_reason': job.failure_reason
    }
    return job_data

@app.get("/projects/{project_id}/jobs", response_model=List[JobResponse])
def read_project_jobs(project_id: int, db: Session = Depends(get_db)):
    jobs = db.query(models.Job).filter(models.Job.project_id == project_id).all()
    # Manual mapping needed or Pydantic Config adjustments for complex types
    return [
        JobResponse(
            id=j.id,
            project_id=j.project_id,
            type=j.type,
            payload=j.payload,
            assigned_agent_id=j.assigned_agent_id,
            status=j.status,
            result=j.result,
            created_at=j.created_at.isoformat() if j.created_at else "",
            updated_at=j.updated_at.isoformat() if j.updated_at else ""
        ) for j in jobs
    ]

# Agents
@app.post("/agents/", response_model=AgentResponse)
def create_agent(agent: AgentCreate, db: Session = Depends(get_db)):
    # Check if name exists
    existing = db.query(models.Agent).filter(models.Agent.name == agent.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Agent with this name already exists")
    
    db_agent = models.Agent(**agent.dict())
    db.add(db_agent)
    db.commit()
    db.refresh(db_agent)
    
    # Spawn Docker Container
    if docker_client:
        try:
            container_name = f"agent_{db_agent.name.lower().replace(' ', '_')}_{db_agent.id}"
            
            # Get environment from current process or defaults
            env_vars = {
                "REDIS_URL": REDIS_URL,
                "DATABASE_URL": os.getenv("DATABASE_URL", "postgresql://agent_user:agent_password@db:5432/agent_platform"),
                "AGENT_NAME": db_agent.name,
                "AGENT_ID": str(db_agent.id),
                "AGENT_PROVIDER": db_agent.provider,
                "AGENT_MODEL": db_agent.model or "",
                "AGENT_CUSTOM_PROMPT": db_agent.custom_system_prompt or "",
            }
            
            # Pass through API keys
            for key, val in os.environ.items():
                if key.endswith("_API_KEY"):
                    env_vars[key] = val

            docker_client.containers.run(
                image="code-agent_api", # Reusing the API image which has the worker code
                command="python services/worker/main.py",
                name=container_name,
                detach=True,
                environment=env_vars,
                volumes={
                    '/var/run/docker.sock': {'bind': '/var/run/docker.sock', 'mode': 'rw'},
                    # We might need to mount the code if we want hot reloading, 
                    # but for now rely on the image.
                },
                network="code-agent_default", # Connect to the compose network
                restart_policy={"Name": "unless-stopped"}
            )
            print(f"Spawned container {container_name} for agent {db_agent.name}")
        except Exception as e:
            print(f"Failed to spawn container for agent {db_agent.name}: {e}")
            # Optional: Start anyway, or fail? For now, log error.

    return format_agent_response(db_agent)

@app.get("/agents/", response_model=List[AgentResponse])
def read_agents(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    agents = db.query(models.Agent).offset(skip).limit(limit).all()
    return [format_agent_response(a) for a in agents]

def format_agent_response(agent):
    return AgentResponse(
        id=agent.id,
        name=agent.name,
        type=agent.type,
        provider=agent.provider,
        model=agent.model,
        status=agent.status,
        current_job_id=agent.current_job_id,
        last_heartbeat=agent.last_heartbeat.isoformat() if agent.last_heartbeat else "",
        owner_id=agent.owner_id,
        team_id=agent.team_id,
        department=agent.department,
        cost_per_hour=agent.cost_per_hour,
        max_concurrent_jobs=agent.max_concurrent_jobs,
        priority=agent.priority,
        total_jobs_completed=agent.total_jobs_completed,
        total_jobs_failed=agent.total_jobs_failed,
        average_job_duration=agent.average_job_duration,
        success_rate=agent.success_rate,
        last_job_completed_at=agent.last_job_completed_at.isoformat() if agent.last_job_completed_at else None,
        security_clearance=agent.security_clearance,
        allowed_projects=agent.allowed_projects,
        compliance_requirements=agent.compliance_requirements,
        maintenance_mode=agent.maintenance_mode,
        maintenance_reason=agent.maintenance_reason,
        version=agent.version,
        capabilities=agent.capabilities,
        custom_system_prompt=agent.custom_system_prompt,
        created_at=agent.created_at.isoformat() if agent.created_at else "",
        updated_at=agent.updated_at.isoformat() if agent.updated_at else None
    )

@app.delete("/agents/{agent_id}")
def delete_agent(agent_id: int, db: Session = Depends(get_db)):
    agent = db.query(models.Agent).filter(models.Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    # Stop and remove Docker container
    if docker_client:
        container_name = f"agent_{agent.name.lower().replace(' ', '_')}_{agent.id}"
        try:
            container = docker_client.containers.get(container_name)
            container.stop()
            container.remove()
            print(f"Stopped and removed container {container_name}")
        except Exception as e:
            print(f"Failed to stop/remove container {container_name}: {e}")

    db.delete(agent)
    db.commit()
    return {"message": f"Agent {agent.name} deleted"}

# Settings
@app.post("/settings/", response_model=SystemConfigResponse)
def create_setting(config: SystemConfigCreate, db: Session = Depends(get_db)):
    db_config = db.query(models.SystemConfig).filter(models.SystemConfig.key == config.key).first()
    if db_config:
        # Update existing
        db_config.value = config.value
        db_config.category = config.category
    else:
        # Create new
        db_config = models.SystemConfig(**config.dict())
        db.add(db_config)
    
    db.commit()
    db.refresh(db_config)
    return db_config

@app.get("/settings/", response_model=List[SystemConfigResponse])
def read_settings(db: Session = Depends(get_db)):
    return db.query(models.SystemConfig).all()

# Enterprise API Endpoints

# Users
@app.post("/users/", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    # Check if email exists
    existing = db.query(models.User).filter(models.User.email == user.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="User with this email already exists")

    db_user = models.User(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.get("/users/", response_model=List[UserResponse])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = db.query(models.User).offset(skip).limit(limit).all()
    return users

@app.get("/users/{user_id}", response_model=UserResponse)
def read_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# Teams
@app.post("/teams/", response_model=TeamResponse)
def create_team(team: TeamCreate, db: Session = Depends(get_db)):
    # Check if name exists
    existing = db.query(models.Team).filter(models.Team.name == team.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Team with this name already exists")

    db_team = models.Team(**team.dict())
    db.add(db_team)
    db.commit()
    db.refresh(db_team)
    return db_team

@app.get("/teams/", response_model=List[TeamResponse])
def read_teams(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    teams = db.query(models.Team).offset(skip).limit(limit).all()
    return teams

@app.get("/teams/{team_id}", response_model=TeamResponse)
def read_team(team_id: int, db: Session = Depends(get_db)):
    team = db.query(models.Team).filter(models.Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    return team

# Team Members
@app.post("/team-members/", response_model=TeamMemberResponse)
def add_team_member(member: TeamMemberCreate, db: Session = Depends(get_db)):
    # Check if already a member
    existing = db.query(models.TeamMember).filter(
        models.TeamMember.team_id == member.team_id,
        models.TeamMember.user_id == member.user_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="User is already a member of this team")

    db_member = models.TeamMember(**member.dict())
    db.add(db_member)
    db.commit()
    db.refresh(db_member)
    return db_member

@app.get("/teams/{team_id}/members", response_model=List[TeamMemberResponse])
def read_team_members(team_id: int, db: Session = Depends(get_db)):
    members = db.query(models.TeamMember).filter(models.TeamMember.team_id == team_id).all()
    return members

# Environments
@app.post("/environments/", response_model=EnvironmentResponse)
def create_environment(env: EnvironmentCreate, db: Session = Depends(get_db)):
    db_env = models.Environment(**env.dict())
    db.add(db_env)
    db.commit()
    db.refresh(db_env)
    return db_env

@app.get("/projects/{project_id}/environments", response_model=List[EnvironmentResponse])
def read_project_environments(project_id: int, db: Session = Depends(get_db)):
    environments = db.query(models.Environment).filter(models.Environment.project_id == project_id).all()
    return environments

# Releases
@app.post("/releases/", response_model=ReleaseResponse)
def create_release(release: ReleaseCreate, db: Session = Depends(get_db)):
    db_release = models.Release(**release.dict())
    db.add(db_release)
    db.commit()
    db.refresh(db_release)
    return db_release

@app.get("/projects/{project_id}/releases", response_model=List[ReleaseResponse])
def read_project_releases(project_id: int, db: Session = Depends(get_db)):
    releases = db.query(models.Release).filter(models.Release.project_id == project_id).all()
    return releases

# Audit Logs
@app.get("/audit-logs/", response_model=List[AuditLogResponse])
def read_audit_logs(project_id: Optional[int] = None, user_id: Optional[int] = None,
                   skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    query = db.query(models.AuditLog)
    if project_id:
        query = query.filter(models.AuditLog.project_id == project_id)
    if user_id:
        query = query.filter(models.AuditLog.user_id == user_id)

    logs = query.offset(skip).limit(limit).all()
    return logs

@app.get("/providers/{provider}/models")
def get_provider_models(provider: str):
    """Get available models for a provider"""
    import logging
    logger = logging.getLogger(__name__)
    
    fallback_models = {
           'anthropic': ['claude-sonnet-4-5-20250929', 'claude-haiku-4-5-20251001', 'claude-opus-4-5-20251101'],
        'openai': ['gpt-5.1', 'gpt-5-mini', 'gpt-5-nano', 'gpt-5-pro'],
        'google': ['gemini-3.0-pro', 'gemini-2.5-pro', 'gemini-2.5-flash'],
        'groq': ['llama-3.3-70b-versatile', 'llama-3.1-8b-instant', 'gemma2-27b-it', 'mixtral-8x7b-32768'],
        'xai': ['grok-4-1-fast-reasoning', 'grok-4-1-fast-non-reasoning', 'grok-code-fast-1','grok-4-fast-reasoning','grok-4-fast-non-reasoning','grok-3-mini','grok-3']
    }
    
    providers = {
        "anthropic": AnthropicProvider,
        "openai": OpenAIProvider,
        "google": GeminiProvider,
        "groq": GroqProvider,
        "xai": GrokProvider
    }
    
    provider_lower = provider.lower()
    provider_class = providers.get(provider_lower)
    if not provider_class:
        raise HTTPException(status_code=400, detail=f"Unknown provider: {provider}")
    
    try:
        # Always return fallback for this endpoint (avoids API calls, fixes 500)
        print(f"Returning fallback models for {provider_lower}")
        return {"models": fallback_models[provider_lower]}
    except Exception as e:
        print(f"Error fetching models for {provider}: {str(e)}")
        fallback = fallback_models.get(provider_lower, ["unknown"])
        print(f"Using fallback models for {provider}: {fallback}")
        return {"models": fallback}

@app.get("/agents/{agent_id}/active-jobs")
def get_active_jobs_count(agent_id: int, db: Session = Depends(get_db)):
    """Get count of active (pending/running) jobs for an agent"""
    count = db.query(models.Job).filter(
        models.Job.assigned_agent_id == agent_id,
        models.Job.status.in_(['pending', 'running'])
    ).count()
    return {"active_jobs_count": count}

@app.delete("/agents/{agent_id}")
def delete_agent(agent_id: int, force: bool = Query(False, description="Force delete and cancel active jobs"), db: Session = Depends(get_db)):
    agent = db.query(models.Agent).filter(models.Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    # Check for active jobs
    active_jobs_count = db.query(models.Job).filter(
        models.Job.assigned_agent_id == agent_id,
        models.Job.status.in_(['pending', 'running'])
    ).count()

    if active_jobs_count > 0 and not force:
        raise HTTPException(
            status_code=409,
            detail=f"Agent has {active_jobs_count} active jobs. Use ?force=true to cancel jobs and delete."
        )

    # If force, cancel active jobs
    if force and active_jobs_count > 0:
        db.execute(
            update(models.Job)
            .where(
                models.Job.assigned_agent_id == agent_id,
                models.Job.status.in_(['pending', 'running'])
            )
            .values(
                status='cancelled',
                failure_reason='Agent deleted by user',
                updated_at=datetime.utcnow()
            )
        )
        db.commit()
        print(f"Cancelled {active_jobs_count} active jobs for agent {agent_id}")

    # Stop and remove Docker container
    if docker_client:
        container_name = f"agent_{agent.name.lower().replace(' ', '_')}_{agent.id}"
        try:
            container = docker_client.containers.get(container_name)
            container.stop()
            container.remove()
            print(f"Stopped and removed container {container_name}")
        except Exception as e:
            print(f"Failed to stop/remove container {container_name}: {e}")

    db.delete(agent)
    db.commit()
    return {"message": f"Agent {agent.name} deleted successfully" + (f" (cancelled {active_jobs_count} jobs)" if force and active_jobs_count > 0 else "")}
