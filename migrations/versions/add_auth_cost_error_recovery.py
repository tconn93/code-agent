"""Add authentication, cost tracking, and error recovery features

Revision ID: add_auth_cost_error_recovery
Revises:
Create Date: 2025-01-12

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_auth_cost_error_recovery'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    """Upgrade database schema."""

    # Add password_hash to users table
    op.add_column('users', sa.Column('password_hash', sa.String(), nullable=True))

    # Create api_keys table
    op.create_table('api_keys',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('key', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now()),
        sa.Column('last_used_at', sa.DateTime(), nullable=True),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
        sa.Column('scopes', postgresql.JSON(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('key')
    )
    op.create_index('ix_api_keys_key', 'api_keys', ['key'])
    op.create_index('ix_api_keys_user_id', 'api_keys', ['user_id'])

    # Add error recovery fields to jobs table
    op.add_column('jobs', sa.Column('retry_count', sa.Integer(), default=0))
    op.add_column('jobs', sa.Column('max_retries', sa.Integer(), default=3))
    op.add_column('jobs', sa.Column('failure_reason', sa.Text(), nullable=True))
    op.add_column('jobs', sa.Column('last_error', sa.Text(), nullable=True))
    op.add_column('jobs', sa.Column('next_retry_at', sa.DateTime(), nullable=True))

    # Add cost tracking fields to jobs table
    op.add_column('jobs', sa.Column('estimated_cost', sa.Numeric(10, 2), nullable=True))
    op.add_column('jobs', sa.Column('actual_cost', sa.Numeric(10, 2), nullable=True))
    op.add_column('jobs', sa.Column('tokens_used_input', sa.Integer(), nullable=True))
    op.add_column('jobs', sa.Column('tokens_used_output', sa.Integer(), nullable=True))
    op.add_column('jobs', sa.Column('tokens_used_total', sa.Integer(), nullable=True))

    # Add performance tracking fields to jobs table
    op.add_column('jobs', sa.Column('estimated_duration', sa.Integer(), nullable=True))
    op.add_column('jobs', sa.Column('actual_duration', sa.Integer(), nullable=True))
    op.add_column('jobs', sa.Column('started_at', sa.DateTime(), nullable=True))
    op.add_column('jobs', sa.Column('completed_at', sa.DateTime(), nullable=True))

    # Add enterprise fields to jobs table (if not exist)
    op.add_column('jobs', sa.Column('priority', sa.String(), default='medium'))
    op.add_column('jobs', sa.Column('requested_by', sa.Integer(), nullable=True))
    op.add_column('jobs', sa.Column('approved_by', sa.Integer(), nullable=True))
    op.add_column('jobs', sa.Column('approved_at', sa.DateTime(), nullable=True))
    op.add_column('jobs', sa.Column('review_required', sa.Boolean(), default=False))
    op.add_column('jobs', sa.Column('reviewed_by', sa.Integer(), nullable=True))
    op.add_column('jobs', sa.Column('reviewed_at', sa.DateTime(), nullable=True))
    op.add_column('jobs', sa.Column('security_level', sa.String(), default='standard'))
    op.add_column('jobs', sa.Column('data_sensitivity', sa.String(), nullable=True))
    op.add_column('jobs', sa.Column('environment', sa.String(), nullable=True))
    op.add_column('jobs', sa.Column('quality_score', sa.Numeric(5, 2), nullable=True))
    op.add_column('jobs', sa.Column('sla_deadline', sa.DateTime(), nullable=True))
    op.add_column('jobs', sa.Column('tags', postgresql.JSON(), nullable=True))
    op.add_column('jobs', sa.Column('result', postgresql.JSON(), nullable=True))
    op.add_column('jobs', sa.Column('logs', sa.Text(), nullable=True))

    # Add foreign key constraints for job relationships
    op.create_foreign_key('fk_jobs_requested_by', 'jobs', 'users', ['requested_by'], ['id'])
    op.create_foreign_key('fk_jobs_approved_by', 'jobs', 'users', ['approved_by'], ['id'])
    op.create_foreign_key('fk_jobs_reviewed_by', 'jobs', 'users', ['reviewed_by'], ['id'])

    # Add indexes for performance
    op.create_index('ix_jobs_status', 'jobs', ['status'])
    op.create_index('ix_jobs_project_id', 'jobs', ['project_id'])
    op.create_index('ix_jobs_created_at', 'jobs', ['created_at'])
    op.create_index('ix_jobs_next_retry_at', 'jobs', ['next_retry_at'])


def downgrade():
    """Downgrade database schema."""

    # Remove indexes
    op.drop_index('ix_jobs_next_retry_at', 'jobs')
    op.drop_index('ix_jobs_created_at', 'jobs')
    op.drop_index('ix_jobs_project_id', 'jobs')
    op.drop_index('ix_jobs_status', 'jobs')

    # Remove foreign keys
    op.drop_constraint('fk_jobs_reviewed_by', 'jobs', type_='foreignkey')
    op.drop_constraint('fk_jobs_approved_by', 'jobs', type_='foreignkey')
    op.drop_constraint('fk_jobs_requested_by', 'jobs', type_='foreignkey')

    # Remove job columns
    op.drop_column('jobs', 'logs')
    op.drop_column('jobs', 'result')
    op.drop_column('jobs', 'tags')
    op.drop_column('jobs', 'sla_deadline')
    op.drop_column('jobs', 'quality_score')
    op.drop_column('jobs', 'environment')
    op.drop_column('jobs', 'data_sensitivity')
    op.drop_column('jobs', 'security_level')
    op.drop_column('jobs', 'reviewed_at')
    op.drop_column('jobs', 'reviewed_by')
    op.drop_column('jobs', 'review_required')
    op.drop_column('jobs', 'approved_at')
    op.drop_column('jobs', 'approved_by')
    op.drop_column('jobs', 'requested_by')
    op.drop_column('jobs', 'priority')
    op.drop_column('jobs', 'completed_at')
    op.drop_column('jobs', 'started_at')
    op.drop_column('jobs', 'actual_duration')
    op.drop_column('jobs', 'estimated_duration')
    op.drop_column('jobs', 'tokens_used_total')
    op.drop_column('jobs', 'tokens_used_output')
    op.drop_column('jobs', 'tokens_used_input')
    op.drop_column('jobs', 'actual_cost')
    op.drop_column('jobs', 'estimated_cost')
    op.drop_column('jobs', 'next_retry_at')
    op.drop_column('jobs', 'last_error')
    op.drop_column('jobs', 'failure_reason')
    op.drop_column('jobs', 'max_retries')
    op.drop_column('jobs', 'retry_count')

    # Drop api_keys table
    op.drop_index('ix_api_keys_user_id', 'api_keys')
    op.drop_index('ix_api_keys_key', 'api_keys')
    op.drop_table('api_keys')

    # Remove password_hash from users
    op.drop_column('users', 'password_hash')
