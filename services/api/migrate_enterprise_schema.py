#!/usr/bin/env python3
"""
Migration script to add enterprise features to the Project model.
Run this script to update your database schema.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from sqlalchemy import create_engine, text
from services.api.database import Base
from services.api.models import Project, User, Team, TeamMember, Environment, Release, AuditLog

def migrate_database():
    """Add enterprise columns and tables to existing database"""

    # Database connection
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://agent_user:agent_password@localhost:5432/agent_platform")
    engine = create_engine(DATABASE_URL)

    print("Starting enterprise schema migration...")

    with engine.connect() as conn:
        # Add new columns to projects table
        print("Adding enterprise columns to projects table...")

        # Project Management & Governance
        conn.execute(text("ALTER TABLE projects ADD COLUMN IF NOT EXISTS owner_id INTEGER REFERENCES users(id)"))
        conn.execute(text("ALTER TABLE projects ADD COLUMN IF NOT EXISTS team_id INTEGER REFERENCES teams(id)"))
        conn.execute(text("ALTER TABLE projects ADD COLUMN IF NOT EXISTS department VARCHAR(255)"))
        conn.execute(text("ALTER TABLE projects ADD COLUMN IF NOT EXISTS business_unit VARCHAR(255)"))
        conn.execute(text("ALTER TABLE projects ADD COLUMN IF NOT EXISTS cost_center VARCHAR(255)"))

        # Project Lifecycle
        conn.execute(text("ALTER TABLE projects ADD COLUMN IF NOT EXISTS status VARCHAR(50) DEFAULT 'active'"))
        conn.execute(text("ALTER TABLE projects ADD COLUMN IF NOT EXISTS priority VARCHAR(20) DEFAULT 'medium'"))
        conn.execute(text("ALTER TABLE projects ADD COLUMN IF NOT EXISTS start_date TIMESTAMP"))
        conn.execute(text("ALTER TABLE projects ADD COLUMN IF NOT EXISTS end_date TIMESTAMP"))
        conn.execute(text("ALTER TABLE projects ADD COLUMN IF NOT EXISTS budget_allocated NUMERIC(10,2)"))

        # Approval & Review
        conn.execute(text("ALTER TABLE projects ADD COLUMN IF NOT EXISTS requires_approval BOOLEAN DEFAULT FALSE"))
        conn.execute(text("ALTER TABLE projects ADD COLUMN IF NOT EXISTS approved_by INTEGER REFERENCES users(id)"))
        conn.execute(text("ALTER TABLE projects ADD COLUMN IF NOT EXISTS approved_at TIMESTAMP"))
        conn.execute(text("ALTER TABLE projects ADD COLUMN IF NOT EXISTS review_due_date TIMESTAMP"))

        # Security & Compliance
        conn.execute(text("ALTER TABLE projects ADD COLUMN IF NOT EXISTS security_level VARCHAR(50) DEFAULT 'internal'"))
        conn.execute(text("ALTER TABLE projects ADD COLUMN IF NOT EXISTS data_classification VARCHAR(100)"))
        conn.execute(text("ALTER TABLE projects ADD COLUMN IF NOT EXISTS compliance_requirements JSONB"))

        # Access Control
        conn.execute(text("ALTER TABLE projects ADD COLUMN IF NOT EXISTS visibility VARCHAR(20) DEFAULT 'team'"))
        conn.execute(text("ALTER TABLE projects ADD COLUMN IF NOT EXISTS allowed_domains JSONB"))
        conn.execute(text("ALTER TABLE projects ADD COLUMN IF NOT EXISTS ip_restrictions JSONB"))

        # Audit Trail
        conn.execute(text("ALTER TABLE projects ADD COLUMN IF NOT EXISTS updated_by INTEGER REFERENCES users(id)"))
        conn.execute(text("ALTER TABLE projects ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP"))
        conn.execute(text("ALTER TABLE projects ADD COLUMN IF NOT EXISTS version INTEGER DEFAULT 1"))

        # Technical & Quality Metrics
        conn.execute(text("ALTER TABLE projects ADD COLUMN IF NOT EXISTS primary_language VARCHAR(100)"))
        conn.execute(text("ALTER TABLE projects ADD COLUMN IF NOT EXISTS frameworks JSONB"))
        conn.execute(text("ALTER TABLE projects ADD COLUMN IF NOT EXISTS deployment_target VARCHAR(100)"))

        # Quality Metrics
        conn.execute(text("ALTER TABLE projects ADD COLUMN IF NOT EXISTS code_coverage_target NUMERIC(5,2) DEFAULT 80.0"))
        conn.execute(text("ALTER TABLE projects ADD COLUMN IF NOT EXISTS test_success_rate NUMERIC(5,2)"))
        conn.execute(text("ALTER TABLE projects ADD COLUMN IF NOT EXISTS last_quality_scan TIMESTAMP"))
        conn.execute(text("ALTER TABLE projects ADD COLUMN IF NOT EXISTS quality_score NUMERIC(5,2)"))

        # Integration
        conn.execute(text("ALTER TABLE projects ADD COLUMN IF NOT EXISTS webhook_urls JSONB"))
        conn.execute(text("ALTER TABLE projects ADD COLUMN IF NOT EXISTS api_endpoints JSONB"))
        conn.execute(text("ALTER TABLE projects ADD COLUMN IF NOT EXISTS external_ids JSONB"))

        # Business Intelligence
        conn.execute(text("ALTER TABLE projects ADD COLUMN IF NOT EXISTS estimated_cost NUMERIC(10,2)"))
        conn.execute(text("ALTER TABLE projects ADD COLUMN IF NOT EXISTS actual_cost NUMERIC(10,2)"))
        conn.execute(text("ALTER TABLE projects ADD COLUMN IF NOT EXISTS cost_per_month NUMERIC(10,2)"))

        # Performance Metrics
        conn.execute(text("ALTER TABLE projects ADD COLUMN IF NOT EXISTS deployment_frequency VARCHAR(20)"))
        conn.execute(text("ALTER TABLE projects ADD COLUMN IF NOT EXISTS lead_time INTEGER"))
        conn.execute(text("ALTER TABLE projects ADD COLUMN IF NOT EXISTS change_failure_rate NUMERIC(5,2)"))
        conn.execute(text("ALTER TABLE projects ADD COLUMN IF NOT EXISTS mttr INTEGER"))

        # Business Value
        conn.execute(text("ALTER TABLE projects ADD COLUMN IF NOT EXISTS business_value TEXT"))
        conn.execute(text("ALTER TABLE projects ADD COLUMN IF NOT EXISTS kpis JSONB"))
        conn.execute(text("ALTER TABLE projects ADD COLUMN IF NOT EXISTS stakeholders JSONB"))

        # Enhance SystemConfig table
        print("Enhancing system_configs table...")
        conn.execute(text("ALTER TABLE system_configs ADD COLUMN IF NOT EXISTS description TEXT"))
        conn.execute(text("ALTER TABLE system_configs ADD COLUMN IF NOT EXISTS is_sensitive BOOLEAN DEFAULT FALSE"))
        conn.execute(text("ALTER TABLE system_configs ADD COLUMN IF NOT EXISTS environment VARCHAR(50)"))
        conn.execute(text("ALTER TABLE system_configs ADD COLUMN IF NOT EXISTS validation_rules JSONB"))
        conn.execute(text("ALTER TABLE system_configs ADD COLUMN IF NOT EXISTS updated_by INTEGER REFERENCES users(id)"))
        conn.execute(text("ALTER TABLE system_configs ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP"))
        conn.execute(text("ALTER TABLE system_configs ADD COLUMN IF NOT EXISTS version INTEGER DEFAULT 1"))

        # Enhance Agents table
        print("Enhancing agents table...")
        conn.execute(text("ALTER TABLE agents ADD COLUMN IF NOT EXISTS owner_id INTEGER REFERENCES users(id)"))
        conn.execute(text("ALTER TABLE agents ADD COLUMN IF NOT EXISTS team_id INTEGER REFERENCES teams(id)"))
        conn.execute(text("ALTER TABLE agents ADD COLUMN IF NOT EXISTS department VARCHAR(255)"))
        conn.execute(text("ALTER TABLE agents ADD COLUMN IF NOT EXISTS cost_per_hour NUMERIC(8,2)"))
        conn.execute(text("ALTER TABLE agents ADD COLUMN IF NOT EXISTS max_concurrent_jobs INTEGER DEFAULT 1"))
        conn.execute(text("ALTER TABLE agents ADD COLUMN IF NOT EXISTS priority VARCHAR(20) DEFAULT 'medium'"))
        conn.execute(text("ALTER TABLE agents ADD COLUMN IF NOT EXISTS total_jobs_completed INTEGER DEFAULT 0"))
        conn.execute(text("ALTER TABLE agents ADD COLUMN IF NOT EXISTS total_jobs_failed INTEGER DEFAULT 0"))
        conn.execute(text("ALTER TABLE agents ADD COLUMN IF NOT EXISTS average_job_duration INTEGER"))
        conn.execute(text("ALTER TABLE agents ADD COLUMN IF NOT EXISTS success_rate NUMERIC(5,2)"))
        conn.execute(text("ALTER TABLE agents ADD COLUMN IF NOT EXISTS last_job_completed_at TIMESTAMP"))
        conn.execute(text("ALTER TABLE agents ADD COLUMN IF NOT EXISTS security_clearance VARCHAR(50) DEFAULT 'standard'"))
        conn.execute(text("ALTER TABLE agents ADD COLUMN IF NOT EXISTS allowed_projects JSONB"))
        conn.execute(text("ALTER TABLE agents ADD COLUMN IF NOT EXISTS compliance_requirements JSONB"))
        conn.execute(text("ALTER TABLE agents ADD COLUMN IF NOT EXISTS maintenance_mode BOOLEAN DEFAULT FALSE"))
        conn.execute(text("ALTER TABLE agents ADD COLUMN IF NOT EXISTS maintenance_reason TEXT"))
        conn.execute(text("ALTER TABLE agents ADD COLUMN IF NOT EXISTS version VARCHAR(50)"))
        conn.execute(text("ALTER TABLE agents ADD COLUMN IF NOT EXISTS capabilities JSONB"))
        conn.execute(text("ALTER TABLE agents ADD COLUMN IF NOT EXISTS created_by INTEGER REFERENCES users(id)"))
        conn.execute(text("ALTER TABLE agents ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP"))
        conn.execute(text("ALTER TABLE agents ADD COLUMN IF NOT EXISTS updated_by INTEGER REFERENCES users(id)"))
        conn.execute(text("ALTER TABLE agents ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP"))

        # Enhance Jobs table
        print("Enhancing jobs table...")
        conn.execute(text("ALTER TABLE jobs ADD COLUMN IF NOT EXISTS priority VARCHAR(20) DEFAULT 'medium'"))
        conn.execute(text("ALTER TABLE jobs ADD COLUMN IF NOT EXISTS requested_by INTEGER REFERENCES users(id)"))
        conn.execute(text("ALTER TABLE jobs ADD COLUMN IF NOT EXISTS approved_by INTEGER REFERENCES users(id)"))
        conn.execute(text("ALTER TABLE jobs ADD COLUMN IF NOT EXISTS approved_at TIMESTAMP"))
        conn.execute(text("ALTER TABLE jobs ADD COLUMN IF NOT EXISTS estimated_cost NUMERIC(8,2)"))
        conn.execute(text("ALTER TABLE jobs ADD COLUMN IF NOT EXISTS actual_cost NUMERIC(8,2)"))
        conn.execute(text("ALTER TABLE jobs ADD COLUMN IF NOT EXISTS estimated_duration INTEGER"))
        conn.execute(text("ALTER TABLE jobs ADD COLUMN IF NOT EXISTS actual_duration INTEGER"))
        conn.execute(text("ALTER TABLE jobs ADD COLUMN IF NOT EXISTS sla_deadline TIMESTAMP"))
        conn.execute(text("ALTER TABLE jobs ADD COLUMN IF NOT EXISTS quality_score NUMERIC(5,2)"))
        conn.execute(text("ALTER TABLE jobs ADD COLUMN IF NOT EXISTS review_required BOOLEAN DEFAULT FALSE"))
        conn.execute(text("ALTER TABLE jobs ADD COLUMN IF NOT EXISTS reviewed_by INTEGER REFERENCES users(id)"))
        conn.execute(text("ALTER TABLE jobs ADD COLUMN IF NOT EXISTS reviewed_at TIMESTAMP"))
        conn.execute(text("ALTER TABLE jobs ADD COLUMN IF NOT EXISTS review_comments TEXT"))
        conn.execute(text("ALTER TABLE jobs ADD COLUMN IF NOT EXISTS security_level VARCHAR(50) DEFAULT 'standard'"))
        conn.execute(text("ALTER TABLE jobs ADD COLUMN IF NOT EXISTS data_sensitivity VARCHAR(50)"))
        conn.execute(text("ALTER TABLE jobs ADD COLUMN IF NOT EXISTS compliance_tags JSONB"))
        conn.execute(text("ALTER TABLE jobs ADD COLUMN IF NOT EXISTS retry_count INTEGER DEFAULT 0"))
        conn.execute(text("ALTER TABLE jobs ADD COLUMN IF NOT EXISTS max_retries INTEGER DEFAULT 3"))
        conn.execute(text("ALTER TABLE jobs ADD COLUMN IF NOT EXISTS failure_reason TEXT"))
        conn.execute(text("ALTER TABLE jobs ADD COLUMN IF NOT EXISTS environment VARCHAR(50)"))
        conn.execute(text("ALTER TABLE jobs ADD COLUMN IF NOT EXISTS tags JSONB"))
        conn.execute(text("ALTER TABLE jobs ADD COLUMN IF NOT EXISTS created_by INTEGER REFERENCES users(id)"))
        conn.execute(text("ALTER TABLE jobs ADD COLUMN IF NOT EXISTS updated_by INTEGER REFERENCES users(id)"))

        # Enhance Artifacts table
        print("Enhancing artifacts table...")
        conn.execute(text("ALTER TABLE artifacts ADD COLUMN IF NOT EXISTS size_bytes INTEGER"))
        conn.execute(text("ALTER TABLE artifacts ADD COLUMN IF NOT EXISTS checksum VARCHAR(255)"))
        conn.execute(text("ALTER TABLE artifacts ADD COLUMN IF NOT EXISTS mime_type VARCHAR(255)"))
        conn.execute(text("ALTER TABLE artifacts ADD COLUMN IF NOT EXISTS version VARCHAR(50)"))
        conn.execute(text("ALTER TABLE artifacts ADD COLUMN IF NOT EXISTS security_level VARCHAR(50) DEFAULT 'internal'"))
        conn.execute(text("ALTER TABLE artifacts ADD COLUMN IF NOT EXISTS data_classification VARCHAR(100)"))
        conn.execute(text("ALTER TABLE artifacts ADD COLUMN IF NOT EXISTS retention_policy VARCHAR(100)"))
        conn.execute(text("ALTER TABLE artifacts ADD COLUMN IF NOT EXISTS encryption_status VARCHAR(50) DEFAULT 'none'"))
        conn.execute(text("ALTER TABLE artifacts ADD COLUMN IF NOT EXISTS access_level VARCHAR(50) DEFAULT 'team'"))
        conn.execute(text("ALTER TABLE artifacts ADD COLUMN IF NOT EXISTS allowed_users JSONB"))
        conn.execute(text("ALTER TABLE artifacts ADD COLUMN IF NOT EXISTS download_count INTEGER DEFAULT 0"))
        conn.execute(text("ALTER TABLE artifacts ADD COLUMN IF NOT EXISTS custom_metadata JSONB"))
        conn.execute(text("ALTER TABLE artifacts ADD COLUMN IF NOT EXISTS tags JSONB"))
        conn.execute(text("ALTER TABLE artifacts ADD COLUMN IF NOT EXISTS description TEXT"))
        conn.execute(text("ALTER TABLE artifacts ADD COLUMN IF NOT EXISTS created_by INTEGER REFERENCES users(id)"))
        conn.execute(text("ALTER TABLE artifacts ADD COLUMN IF NOT EXISTS uploaded_by INTEGER REFERENCES users(id)"))
        conn.execute(text("ALTER TABLE artifacts ADD COLUMN IF NOT EXISTS uploaded_at TIMESTAMP"))
        conn.execute(text("ALTER TABLE artifacts ADD COLUMN IF NOT EXISTS last_accessed TIMESTAMP"))
        conn.execute(text("ALTER TABLE artifacts ADD COLUMN IF NOT EXISTS expires_at TIMESTAMP"))

        # Enhance Teams table
        print("Enhancing teams table...")
        conn.execute(text("ALTER TABLE teams ADD COLUMN IF NOT EXISTS budget_allocated NUMERIC(10,2)"))
        conn.execute(text("ALTER TABLE teams ADD COLUMN IF NOT EXISTS cost_center VARCHAR(255)"))
        conn.execute(text("ALTER TABLE teams ADD COLUMN IF NOT EXISTS max_members INTEGER"))
        conn.execute(text("ALTER TABLE teams ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE"))
        conn.execute(text("ALTER TABLE teams ADD COLUMN IF NOT EXISTS tags JSONB"))

        # Create new tables
        print("Creating new tables...")

        # Users table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                email VARCHAR(255) UNIQUE NOT NULL,
                name VARCHAR(255) NOT NULL,
                role VARCHAR(50) DEFAULT 'developer',
                department VARCHAR(255),
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP
            )
        """))

        # Teams table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS teams (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) UNIQUE NOT NULL,
                description TEXT,
                department VARCHAR(255),
                manager_id INTEGER REFERENCES users(id),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))

        # Team members table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS team_members (
                id SERIAL PRIMARY KEY,
                team_id INTEGER NOT NULL REFERENCES teams(id),
                user_id INTEGER NOT NULL REFERENCES users(id),
                role VARCHAR(50) DEFAULT 'member',
                joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(team_id, user_id)
            )
        """))

        # Environments table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS environments (
                id SERIAL PRIMARY KEY,
                project_id INTEGER NOT NULL REFERENCES projects(id),
                name VARCHAR(100) NOT NULL,
                url VARCHAR(500),
                status VARCHAR(50) DEFAULT 'active',
                last_deployment TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))

        # Releases table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS releases (
                id SERIAL PRIMARY KEY,
                project_id INTEGER NOT NULL REFERENCES projects(id),
                version VARCHAR(100) NOT NULL,
                name VARCHAR(255),
                description TEXT,
                status VARCHAR(50) DEFAULT 'draft',
                released_by INTEGER REFERENCES users(id),
                released_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))

        # Audit logs table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS audit_logs (
                id SERIAL PRIMARY KEY,
                project_id INTEGER REFERENCES projects(id),
                user_id INTEGER REFERENCES users(id),
                action VARCHAR(100) NOT NULL,
                entity_type VARCHAR(100) NOT NULL,
                entity_id INTEGER,
                old_values JSONB,
                new_values JSONB,
                ip_address VARCHAR(45),
                user_agent TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))

        # Create indexes for performance
        print("Creating indexes...")

        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_projects_owner ON projects(owner_id)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_projects_team ON projects(team_id)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_projects_status ON projects(status)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_projects_priority ON projects(priority)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_projects_department ON projects(department)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_teams_name ON teams(name)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_audit_logs_project ON audit_logs(project_id)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_audit_logs_user ON audit_logs(user_id)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_audit_logs_created ON audit_logs(created_at)"))

        conn.commit()

    print("Migration completed successfully!")
    print("\nNext steps:")
    print("1. Restart your API server to load the new models")
    print("2. Update your API endpoints to handle the new fields")
    print("3. Consider adding data migration scripts for existing projects")

if __name__ == "__main__":
    migrate_database()