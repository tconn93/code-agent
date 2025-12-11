"""Initial migration

Revision ID: 01a395831217
Revises: 
Create Date: 2025-12-11 00:40:40.642936

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '01a395831217'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('team_members',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('team_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('role', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('joined_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['team_id'], ['teams.id'], name=op.f('team_members_team_id_fkey')),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name=op.f('team_members_user_id_fkey')),
    sa.PrimaryKeyConstraint('id', name=op.f('team_members_pkey'))
    )
    op.create_index(op.f('ix_team_members_id'), 'team_members', ['id'], unique=False)
    op.create_table('releases',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('project_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('version', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('name', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('description', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('status', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('released_by', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('released_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['project_id'], ['projects.id'], name=op.f('releases_project_id_fkey')),
    sa.ForeignKeyConstraint(['released_by'], ['users.id'], name=op.f('releases_released_by_fkey')),
    sa.PrimaryKeyConstraint('id', name=op.f('releases_pkey'))
    )
    op.create_index(op.f('ix_releases_id'), 'releases', ['id'], unique=False)
    op.create_table('system_configs',
    sa.Column('key', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('value', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('category', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('description', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('is_sensitive', sa.BOOLEAN(), autoincrement=False, nullable=True),
    sa.Column('environment', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('validation_rules', postgresql.JSON(astext_type=sa.Text()), autoincrement=False, nullable=True),
    sa.Column('updated_by', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('updated_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('version', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['updated_by'], ['users.id'], name=op.f('system_configs_updated_by_fkey')),
    sa.PrimaryKeyConstraint('key', name=op.f('system_configs_pkey'))
    )
    op.create_index(op.f('ix_system_configs_key'), 'system_configs', ['key'], unique=False)
    op.create_table('audit_logs',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('project_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('action', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('entity_type', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('entity_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('old_values', postgresql.JSON(astext_type=sa.Text()), autoincrement=False, nullable=True),
    sa.Column('new_values', postgresql.JSON(astext_type=sa.Text()), autoincrement=False, nullable=True),
    sa.Column('ip_address', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('user_agent', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['project_id'], ['projects.id'], name=op.f('audit_logs_project_id_fkey')),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name=op.f('audit_logs_user_id_fkey')),
    sa.PrimaryKeyConstraint('id', name=op.f('audit_logs_pkey'))
    )
    op.create_index(op.f('ix_audit_logs_id'), 'audit_logs', ['id'], unique=False)
    op.create_table('agents',
    sa.Column('id', sa.INTEGER(), server_default=sa.text("nextval('agents_id_seq'::regclass)"), autoincrement=True, nullable=False),
    sa.Column('name', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('type', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('provider', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('model', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('status', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('current_job_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('last_heartbeat', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('owner_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('team_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('department', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('cost_per_hour', sa.NUMERIC(precision=8, scale=2), autoincrement=False, nullable=True),
    sa.Column('max_concurrent_jobs', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('priority', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('total_jobs_completed', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('total_jobs_failed', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('average_job_duration', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('success_rate', sa.NUMERIC(precision=5, scale=2), autoincrement=False, nullable=True),
    sa.Column('last_job_completed_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('custom_system_prompt', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('security_clearance', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('allowed_projects', postgresql.JSON(astext_type=sa.Text()), autoincrement=False, nullable=True),
    sa.Column('compliance_requirements', postgresql.JSON(astext_type=sa.Text()), autoincrement=False, nullable=True),
    sa.Column('maintenance_mode', sa.BOOLEAN(), autoincrement=False, nullable=True),
    sa.Column('maintenance_reason', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('version', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('capabilities', postgresql.JSON(astext_type=sa.Text()), autoincrement=False, nullable=True),
    sa.Column('created_by', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('updated_by', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('updated_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['created_by'], ['users.id'], name='agents_created_by_fkey'),
    sa.ForeignKeyConstraint(['owner_id'], ['users.id'], name='agents_owner_id_fkey'),
    sa.ForeignKeyConstraint(['team_id'], ['teams.id'], name='agents_team_id_fkey'),
    sa.ForeignKeyConstraint(['updated_by'], ['users.id'], name='agents_updated_by_fkey'),
    sa.PrimaryKeyConstraint('id', name='agents_pkey'),
    postgresql_ignore_search_path=False
    )
    op.create_index(op.f('ix_agents_name'), 'agents', ['name'], unique=True)
    op.create_index(op.f('ix_agents_id'), 'agents', ['id'], unique=False)
    op.create_table('teams',
    sa.Column('id', sa.INTEGER(), server_default=sa.text("nextval('teams_id_seq'::regclass)"), autoincrement=True, nullable=False),
    sa.Column('name', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('description', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('department', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('manager_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('budget_allocated', sa.NUMERIC(precision=10, scale=2), autoincrement=False, nullable=True),
    sa.Column('cost_center', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('max_members', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('is_active', sa.BOOLEAN(), autoincrement=False, nullable=True),
    sa.Column('tags', postgresql.JSON(astext_type=sa.Text()), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['manager_id'], ['users.id'], name='teams_manager_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='teams_pkey'),
    postgresql_ignore_search_path=False
    )
    op.create_index(op.f('ix_teams_name'), 'teams', ['name'], unique=True)
    op.create_index(op.f('ix_teams_id'), 'teams', ['id'], unique=False)
    op.create_table('environments',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('project_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('name', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('url', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('status', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('last_deployment', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['project_id'], ['projects.id'], name=op.f('environments_project_id_fkey')),
    sa.PrimaryKeyConstraint('id', name=op.f('environments_pkey'))
    )
    op.create_index(op.f('ix_environments_id'), 'environments', ['id'], unique=False)
    op.create_table('jobs',
    sa.Column('id', sa.INTEGER(), server_default=sa.text("nextval('jobs_id_seq'::regclass)"), autoincrement=True, nullable=False),
    sa.Column('project_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('sprint_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('type', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('status', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('payload', postgresql.JSON(astext_type=sa.Text()), autoincrement=False, nullable=True),
    sa.Column('assigned_agent_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('updated_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['assigned_agent_id'], ['agents.id'], name='jobs_assigned_agent_id_fkey'),
    sa.ForeignKeyConstraint(['project_id'], ['projects.id'], name='jobs_project_id_fkey'),
    sa.ForeignKeyConstraint(['sprint_id'], ['sprints.id'], name='jobs_sprint_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='jobs_pkey'),
    postgresql_ignore_search_path=False
    )
    op.create_table('users',
    sa.Column('id', sa.INTEGER(), server_default=sa.text("nextval('users_id_seq'::regclass)"), autoincrement=True, nullable=False),
    sa.Column('email', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('name', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('role', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('department', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('is_active', sa.BOOLEAN(), autoincrement=False, nullable=True),
    sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('last_login', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id', name='users_pkey'),
    postgresql_ignore_search_path=False
    )
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_table('sprints',
    sa.Column('id', sa.INTEGER(), server_default=sa.text("nextval('sprints_id_seq'::regclass)"), autoincrement=True, nullable=False),
    sa.Column('project_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('name', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('goal', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('start_date', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('end_date', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('status', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('updated_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('created_by', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('updated_by', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['created_by'], ['users.id'], name='sprints_created_by_fkey'),
    sa.ForeignKeyConstraint(['project_id'], ['projects.id'], name='sprints_project_id_fkey'),
    sa.ForeignKeyConstraint(['updated_by'], ['users.id'], name='sprints_updated_by_fkey'),
    sa.PrimaryKeyConstraint('id', name='sprints_pkey'),
    postgresql_ignore_search_path=False
    )
    op.create_table('projects',
    sa.Column('id', sa.INTEGER(), server_default=sa.text("nextval('projects_id_seq'::regclass)"), autoincrement=True, nullable=False),
    sa.Column('name', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('description', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('repo_url', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('owner_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('team_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('department', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('business_unit', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('cost_center', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('status', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('priority', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('start_date', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('end_date', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('budget_allocated', sa.NUMERIC(precision=10, scale=2), autoincrement=False, nullable=True),
    sa.Column('requires_approval', sa.BOOLEAN(), autoincrement=False, nullable=True),
    sa.Column('approved_by', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('approved_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('review_due_date', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('security_level', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('data_classification', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('compliance_requirements', postgresql.JSON(astext_type=sa.Text()), autoincrement=False, nullable=True),
    sa.Column('visibility', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('allowed_domains', postgresql.JSON(astext_type=sa.Text()), autoincrement=False, nullable=True),
    sa.Column('ip_restrictions', postgresql.JSON(astext_type=sa.Text()), autoincrement=False, nullable=True),
    sa.Column('updated_by', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('updated_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('version', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('primary_language', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('frameworks', postgresql.JSON(astext_type=sa.Text()), autoincrement=False, nullable=True),
    sa.Column('deployment_target', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('code_coverage_target', sa.NUMERIC(precision=5, scale=2), autoincrement=False, nullable=True),
    sa.Column('test_success_rate', sa.NUMERIC(precision=5, scale=2), autoincrement=False, nullable=True),
    sa.Column('last_quality_scan', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('quality_score', sa.NUMERIC(precision=5, scale=2), autoincrement=False, nullable=True),
    sa.Column('webhook_urls', postgresql.JSON(astext_type=sa.Text()), autoincrement=False, nullable=True),
    sa.Column('api_endpoints', postgresql.JSON(astext_type=sa.Text()), autoincrement=False, nullable=True),
    sa.Column('external_ids', postgresql.JSON(astext_type=sa.Text()), autoincrement=False, nullable=True),
    sa.Column('estimated_cost', sa.NUMERIC(precision=10, scale=2), autoincrement=False, nullable=True),
    sa.Column('actual_cost', sa.NUMERIC(precision=10, scale=2), autoincrement=False, nullable=True),
    sa.Column('cost_per_month', sa.NUMERIC(precision=10, scale=2), autoincrement=False, nullable=True),
    sa.Column('deployment_frequency', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('lead_time', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('change_failure_rate', sa.NUMERIC(precision=5, scale=2), autoincrement=False, nullable=True),
    sa.Column('mttr', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('business_value', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('kpis', postgresql.JSON(astext_type=sa.Text()), autoincrement=False, nullable=True),
    sa.Column('stakeholders', postgresql.JSON(astext_type=sa.Text()), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['approved_by'], ['users.id'], name='projects_approved_by_fkey'),
    sa.ForeignKeyConstraint(['owner_id'], ['users.id'], name='projects_owner_id_fkey'),
    sa.ForeignKeyConstraint(['team_id'], ['teams.id'], name='projects_team_id_fkey'),
    sa.ForeignKeyConstraint(['updated_by'], ['users.id'], name='projects_updated_by_fkey'),
    sa.PrimaryKeyConstraint('id', name='projects_pkey'),
    postgresql_ignore_search_path=False
    )
    op.create_index(op.f('ix_projects_name'), 'projects', ['name'], unique=False)
    op.create_index(op.f('ix_projects_id'), 'projects', ['id'], unique=False)
    op.create_table('artifacts',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('project_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('job_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('name', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('path', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('type', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('size_bytes', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('checksum', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('mime_type', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('version', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('security_level', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('data_classification', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('retention_policy', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('encryption_status', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('access_level', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('allowed_users', postgresql.JSON(astext_type=sa.Text()), autoincrement=False, nullable=True),
    sa.Column('download_count', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('custom_metadata', postgresql.JSON(astext_type=sa.Text()), autoincrement=False, nullable=True),
    sa.Column('tags', postgresql.JSON(astext_type=sa.Text()), autoincrement=False, nullable=True),
    sa.Column('description', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('created_by', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('uploaded_by', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('uploaded_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('last_accessed', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('expires_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['created_by'], ['users.id'], name=op.f('artifacts_created_by_fkey')),
    sa.ForeignKeyConstraint(['job_id'], ['jobs.id'], name=op.f('artifacts_job_id_fkey')),
    sa.ForeignKeyConstraint(['project_id'], ['projects.id'], name=op.f('artifacts_project_id_fkey')),
    sa.ForeignKeyConstraint(['uploaded_by'], ['users.id'], name=op.f('artifacts_uploaded_by_fkey')),
    sa.PrimaryKeyConstraint('id', name=op.f('artifacts_pkey'))
    )
    op.create_index(op.f('ix_artifacts_name'), 'artifacts', ['name'], unique=False)
    op.create_index(op.f('ix_artifacts_id'), 'artifacts', ['id'], unique=False)
    


def downgrade() -> None:
    """Downgrade schema."""
    ### commands auto generated by Alembic - please adjust! ###
    ### end Alembic commands ###

    ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_artifacts_id'), table_name='artifacts')
    op.drop_index(op.f('ix_artifacts_name'), table_name='artifacts')
    op.drop_table('artifacts')
    op.drop_index(op.f('ix_projects_id'), table_name='projects')
    op.drop_index(op.f('ix_projects_name'), table_name='projects')
    op.drop_table('projects')
    op.drop_table('sprints')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_table('users')
    op.drop_table('jobs')
    op.drop_index(op.f('ix_environments_id'), table_name='environments')
    op.drop_table('environments')
    op.drop_index(op.f('ix_teams_id'), table_name='teams')
    op.drop_index(op.f('ix_teams_name'), table_name='teams')
    op.drop_table('teams')
    op.drop_index(op.f('ix_agents_id'), table_name='agents')
    op.drop_index(op.f('ix_agents_name'), table_name='agents')
    op.drop_table('agents')
    op.drop_index(op.f('ix_audit_logs_id'), table_name='audit_logs')
    op.drop_table('audit_logs')
    op.drop_index(op.f('ix_system_configs_key'), table_name='system_configs')
    op.drop_table('system_configs')
    op.drop_index(op.f('ix_releases_id'), table_name='releases')
    op.drop_table('releases')
    op.drop_index(op.f('ix_team_members_id'), table_name='team_members')
    op.drop_table('team_members')
    # ### end Alembic commands ###