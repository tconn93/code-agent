from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, JSON, Text, Boolean, Numeric
from sqlalchemy.orm import relationship
from datetime import datetime
from services.api.database import Base

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(Text, nullable=True)
    repo_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Project Management & Governance
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=True)
    department = Column(String, nullable=True)
    business_unit = Column(String, nullable=True)
    cost_center = Column(String, nullable=True)

    # Project Lifecycle
    status = Column(String, default="active")  # active, paused, completed, archived
    priority = Column(String, default="medium")  # low, medium, high, critical
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    budget_allocated = Column(Numeric(10,2), nullable=True)

    # Approval & Review
    requires_approval = Column(Boolean, default=False)
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    review_due_date = Column(DateTime, nullable=True)

    # Security & Compliance
    security_level = Column(String, default="internal")  # public, internal, confidential, restricted
    data_classification = Column(String, nullable=True)  # PII, PHI, financial, etc.
    compliance_requirements = Column(JSON, nullable=True)  # GDPR, SOX, HIPAA, etc.

    # Access Control
    visibility = Column(String, default="team")  # public, team, private
    allowed_domains = Column(JSON, nullable=True)  # Email domains that can access
    ip_restrictions = Column(JSON, nullable=True)  # IP ranges for access

    # Audit Trail
    updated_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    version = Column(Integer, default=1)

    # Technical & Quality Metrics
    primary_language = Column(String, nullable=True)
    frameworks = Column(JSON, nullable=True)
    deployment_target = Column(String, nullable=True)

    # Quality Metrics
    code_coverage_target = Column(Numeric(5,2), default=80.0)
    test_success_rate = Column(Numeric(5,2), nullable=True)
    last_quality_scan = Column(DateTime, nullable=True)
    quality_score = Column(Numeric(5,2), nullable=True)

    # Integration
    webhook_urls = Column(JSON, nullable=True)
    api_endpoints = Column(JSON, nullable=True)
    external_ids = Column(JSON, nullable=True)

    # Business Intelligence
    estimated_cost = Column(Numeric(10,2), nullable=True)
    actual_cost = Column(Numeric(10,2), nullable=True)
    cost_per_month = Column(Numeric(10,2), nullable=True)

    # Performance Metrics
    deployment_frequency = Column(String, nullable=True)  # daily, weekly, monthly
    lead_time = Column(Integer, nullable=True)  # Hours from commit to deploy
    change_failure_rate = Column(Numeric(5,2), nullable=True)  # % of failed deployments
    mttr = Column(Integer, nullable=True)  # Mean time to recovery (minutes)

    # Business Value
    business_value = Column(Text, nullable=True)
    kpis = Column(JSON, nullable=True)
    stakeholders = Column(JSON, nullable=True)

    # Relationships
    jobs = relationship("Job", back_populates="project")  # one_to_many: Project has many Jobs
    sprints = relationship("Sprint", back_populates="project")  # one_to_many: Project has many Sprints
    artifacts = relationship("Artifact", back_populates="project")  # one_to_many: Project has many Artifacts
    owner = relationship("User", foreign_keys=[owner_id])  # many_to_one: Project owned by one User
    approved_by_user = relationship("User", foreign_keys=[approved_by])  # many_to_one: Project approved by one User
    updated_by_user = relationship("User", foreign_keys=[updated_by])  # many_to_one: Project updated by one User
    team = relationship("Team", back_populates="projects")  # many_to_one: Project belongs to one Team
    environments = relationship("Environment", back_populates="project")  # one_to_many: Project has many Environments
    releases = relationship("Release", back_populates="project")  # one_to_many: Project has many Releases
    audit_logs = relationship("AuditLog", back_populates="project")  # one_to_many: Project has many AuditLogs

class SystemConfig(Base):
    __tablename__ = "system_configs"

    key = Column(String, primary_key=True, index=True)
    value = Column(String) # For simple strings. For sensitive data, consider encryption (out of scope for now)
    category = Column(String, default="general") # e.g., 'llm_provider', 'system', 'notification'
    description = Column(Text, nullable=True)
    is_sensitive = Column(Boolean, default=False)
    environment = Column(String, nullable=True) # development, staging, production
    validation_rules = Column(JSON, nullable=True) # JSON schema for validation
    updated_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    version = Column(Integer, default=1)

    # Relationships
    updated_by_user = relationship("User", foreign_keys=[updated_by])

class Agent(Base):
    __tablename__ = "agents"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    type = Column(String) # architect, coding, testing, etc.
    provider = Column(String, default="xai") # e.g. "anthropic", "openai", "google"
    model = Column(String, nullable=True) # e.g. "claude-3-5-sonnet", "gpt-4o"
    status = Column(String, default="idle") # idle, busy, offline
    current_job_id = Column(Integer, nullable=True)
    last_heartbeat = Column(DateTime, default=datetime.utcnow)

    # Enterprise Features
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=True)
    department = Column(String, nullable=True)
    cost_per_hour = Column(Numeric(8,2), nullable=True) # Cost tracking
    max_concurrent_jobs = Column(Integer, default=1)
    priority = Column(String, default="medium") # low, medium, high, critical

    # Performance Metrics
    total_jobs_completed = Column(Integer, default=0)
    total_jobs_failed = Column(Integer, default=0)
    average_job_duration = Column(Integer, nullable=True) # seconds
    success_rate = Column(Numeric(5,2), nullable=True) # percentage
    last_job_completed_at = Column(DateTime, nullable=True)
    custom_system_prompt = Column(Text, nullable=True)

    # Security & Compliance
    security_clearance = Column(String, default="standard") # standard, elevated, restricted
    allowed_projects = Column(JSON, nullable=True) # List of allowed project IDs
    compliance_requirements = Column(JSON, nullable=True)

    # Operational
    maintenance_mode = Column(Boolean, default=False)
    maintenance_reason = Column(Text, nullable=True)
    version = Column(String, nullable=True) # Agent version
    capabilities = Column(JSON, nullable=True) # What the agent can do

    # Audit Trail
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    owner = relationship("User", foreign_keys=[owner_id])
    created_by_user = relationship("User", foreign_keys=[created_by])
    updated_by_user = relationship("User", foreign_keys=[updated_by])
    team = relationship("Team", back_populates="agents")
    # jobs (Assigned jobs) can be queried via Job.assigned_agent_id

class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    sprint_id = Column(Integer, ForeignKey("sprints.id"), nullable=True)
    type = Column(String, nullable=False)
    status = Column(String, default="pending")
    payload = Column(JSON)
    result = Column(JSON, nullable=True)
    logs = Column(Text, nullable=True)
    assigned_agent_id = Column(Integer, ForeignKey("agents.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Error Recovery
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    failure_reason = Column(Text, nullable=True)
    last_error = Column(Text, nullable=True)
    next_retry_at = Column(DateTime, nullable=True)

    # Enterprise Features
    priority = Column(String, default="medium")  # low, medium, high, critical
    requested_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    review_required = Column(Boolean, default=False)
    reviewed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    reviewed_at = Column(DateTime, nullable=True)

    # Cost Tracking
    estimated_cost = Column(Numeric(10,2), nullable=True)
    actual_cost = Column(Numeric(10,2), nullable=True)
    tokens_used_input = Column(Integer, nullable=True)
    tokens_used_output = Column(Integer, nullable=True)
    tokens_used_total = Column(Integer, nullable=True)

    # Performance
    estimated_duration = Column(Integer, nullable=True)  # seconds
    actual_duration = Column(Integer, nullable=True)  # seconds
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    # Security
    security_level = Column(String, default="standard")
    data_sensitivity = Column(String, nullable=True)
    environment = Column(String, nullable=True)  # dev, staging, prod

    # Quality
    quality_score = Column(Numeric(5,2), nullable=True)
    sla_deadline = Column(DateTime, nullable=True)
    tags = Column(JSON, nullable=True)

    # Relationships
    project = relationship("Project", back_populates="jobs")  # many_to_one: Job belongs to one Project
    sprint = relationship("Sprint", back_populates="jobs")  # many_to_one: Job belongs to one Sprint
    assigned_agent = relationship("Agent")  # many_to_one: Job assigned to one Agent
    artifacts = relationship("Artifact", back_populates="job")  # one_to_many: Job has many Artifacts
    requested_by_user = relationship("User", foreign_keys=[requested_by])
    approved_by_user = relationship("User", foreign_keys=[approved_by])
    reviewed_by_user = relationship("User", foreign_keys=[reviewed_by])

class Sprint(Base):
    __tablename__ = "sprints"

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    name = Column(String, nullable=False)
    goal = Column(Text)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    status = Column(String, default="planning")  # planning, active, completed, cancelled
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Audit fields (FK to User for traceability)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    updated_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Relationships
    project = relationship("Project", back_populates="sprints")  # many_to_one: Sprint belongs to one Project
    jobs = relationship("Job", back_populates="sprint")  # one_to_many: Sprint has many Jobs
    created_by_user = relationship("User", foreign_keys=[created_by])  # many_to_one: Sprint created by one User
    updated_by_user = relationship("User", foreign_keys=[updated_by])  # many_to_one: Sprint updated by one User

class Artifact(Base):
    __tablename__ = "artifacts"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=True)
    name = Column(String, index=True)
    path = Column(String) # Path to file
    type = Column(String) # file, image, diff, log, report, test_result
    created_at = Column(DateTime, default=datetime.utcnow)

    # Enterprise Features
    size_bytes = Column(Integer, nullable=True) # File size
    checksum = Column(String, nullable=True) # SHA256 or similar
    mime_type = Column(String, nullable=True) # MIME type
    version = Column(String, nullable=True) # Version tag

    # Security & Compliance
    security_level = Column(String, default="internal")
    data_classification = Column(String, nullable=True) # PII, PHI, financial, etc.
    retention_policy = Column(String, nullable=True) # how long to keep
    encryption_status = Column(String, default="none") # none, encrypted, encrypted_at_rest

    # Access Control
    access_level = Column(String, default="team") # public, team, private, restricted
    allowed_users = Column(JSON, nullable=True) # List of user IDs with access
    download_count = Column(Integer, default=0)

    # Metadata
    custom_metadata = Column(JSON, nullable=True) # Additional metadata
    tags = Column(JSON, nullable=True) # Custom tags
    description = Column(Text, nullable=True)

    # Audit Trail
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    uploaded_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    uploaded_at = Column(DateTime, nullable=True)
    last_accessed = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True) # For retention policies

    # Relationships
    project = relationship("Project", back_populates="artifacts")  # many_to_one: Artifact belongs to one Project
    job = relationship("Job", back_populates="artifacts")  # many_to_one: Artifact belongs to one Job
    created_by_user = relationship("User", foreign_keys=[created_by])  # many_to_one: Artifact created by one User
    uploaded_by_user = relationship("User", foreign_keys=[uploaded_by])  # many_to_one: Artifact uploaded by one User



class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    name = Column(String)
    password_hash = Column(String, nullable=True)  # Hashed password for authentication
    role = Column(String, default="developer")  # admin, manager, developer, viewer
    department = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)

    # Relationships
    owned_projects = relationship("Project", foreign_keys="Project.owner_id", back_populates="owner")
    approved_projects = relationship("Project", foreign_keys="Project.approved_by", back_populates="approved_by_user")
    updated_projects = relationship("Project", foreign_keys="Project.updated_by", back_populates="updated_by_user")
    teams = relationship("TeamMember", back_populates="user")
    audit_logs = relationship("AuditLog", back_populates="user")
    api_keys = relationship("APIKey", back_populates="user")


class APIKey(Base):
    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    key = Column(String, unique=True, index=True)  # The actual API key
    name = Column(String, nullable=True)  # User-friendly name
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_used_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)  # Optional expiration
    scopes = Column(JSON, nullable=True)  # Permissions/scopes for this key

    # Relationships
    user = relationship("User", back_populates="api_keys")


class Team(Base):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(Text, nullable=True)
    department = Column(String, nullable=True)
    manager_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Enterprise Features
    budget_allocated = Column(Numeric(10,2), nullable=True)
    cost_center = Column(String, nullable=True)
    max_members = Column(Integer, nullable=True)
    is_active = Column(Boolean, default=True)
    tags = Column(JSON, nullable=True)

    # Relationships
    manager = relationship("User", foreign_keys=[manager_id])
    projects = relationship("Project", back_populates="team")
    members = relationship("TeamMember", back_populates="team")
    agents = relationship("Agent", back_populates="team")


class TeamMember(Base):
    __tablename__ = "team_members"

    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    role = Column(String, default="member")  # lead, member, observer
    joined_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    team = relationship("Team", back_populates="members")
    user = relationship("User", back_populates="teams")


class Environment(Base):
    __tablename__ = "environments"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    name = Column(String)  # development, staging, production
    url = Column(String, nullable=True)
    status = Column(String, default="active")  # active, inactive, maintenance
    last_deployment = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    project = relationship("Project", back_populates="environments")


class Release(Base):
    __tablename__ = "releases"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    version = Column(String)  # v1.0.0, 2024.01.15, etc.
    name = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    status = Column(String, default="draft")  # draft, released, rolled_back
    released_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    released_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    project = relationship("Project", back_populates="releases")
    released_by_user = relationship("User", foreign_keys=[released_by])


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String)  # create, update, delete, approve, deploy
    entity_type = Column(String)  # project, job, agent, release
    entity_id = Column(Integer, nullable=True)
    old_values = Column(JSON, nullable=True)
    new_values = Column(JSON, nullable=True)
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    project = relationship("Project", back_populates="audit_logs")
    user = relationship("User", back_populates="audit_logs")