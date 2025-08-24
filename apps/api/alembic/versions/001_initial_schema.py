"""Initial schema

Revision ID: 001
Revises:
Create Date: 2024-01-01 00:00:00.000000

"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create users table
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('display_name', sa.String(), nullable=False),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('role', sa.Enum('STUDENT', 'AUTHOR', 'ADMIN', name='userrole'), nullable=False),
        sa.Column('is_active', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)

    # Create problems table
    op.create_table('problems',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('slug', sa.String(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('statement_md', sa.Text(), nullable=False),
        sa.Column('tags', sa.JSON(), nullable=True),
        sa.Column('difficulty', sa.Enum('EASY', 'MEDIUM', 'HARD', 'EXPERT', name='problemdifficulty'), nullable=True),
        sa.Column('checker_type', sa.Enum('DIFF', 'TOKEN', 'FLOAT_EPS', 'CUSTOM', name='checkertype'), nullable=True),
        sa.Column('time_limit_ms', sa.Integer(), nullable=True),
        sa.Column('memory_limit_mb', sa.Integer(), nullable=True),
        sa.Column('output_limit_kb', sa.Integer(), nullable=True),
        sa.Column('solve_time_limit_sec', sa.Integer(), nullable=True),
        sa.Column('max_attempts', sa.Integer(), nullable=True),
        sa.Column('visible_from_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('visible_until_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('attempt_open_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('attempt_close_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('availability_policy', sa.Enum('HARD_CLOSE', 'SOFT_GRACE', name='availabilitypolicy'), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.Column('version', sa.Integer(), nullable=True),
        sa.Column('status', sa.Enum('DRAFT', 'REVIEW', 'PUBLISHED', 'ARCHIVED', name='problemstatus'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_problems_id'), 'problems', ['id'], unique=False)
    op.create_index(op.f('ix_problems_slug'), 'problems', ['slug'], unique=True)

    # Create testcases table
    op.create_table('testcases',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('problem_id', sa.Integer(), nullable=False),
        sa.Column('group', sa.String(), nullable=True),
        sa.Column('idx', sa.Integer(), nullable=False),
        sa.Column('input_blob', sa.Text(), nullable=False),
        sa.Column('output_blob', sa.Text(), nullable=False),
        sa.Column('points', sa.Integer(), nullable=True),
        sa.Column('is_sample', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['problem_id'], ['problems.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_testcases_id'), 'testcases', ['id'], unique=False)

    # Create attempts table
    op.create_table('attempts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('problem_id', sa.Integer(), nullable=False),
        sa.Column('started_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('status', sa.Enum('ACTIVE', 'COMPLETED', 'EXPIRED', 'ABANDONED', name='attemptstatus'), nullable=True),
        sa.Column('integrity_snapshot_json', sa.Text(), nullable=True),
        sa.Column('late_by_sec', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['problem_id'], ['problems.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_attempts_id'), 'attempts', ['id'], unique=False)

    # Create submissions table
    op.create_table('submissions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('attempt_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('problem_id', sa.Integer(), nullable=False),
        sa.Column('lang', sa.Enum('PYTHON', 'CPP', 'JAVA', 'JAVASCRIPT', 'GO', 'RUST', name='submissionlanguage'), nullable=False),
        sa.Column('source_ref', sa.String(), nullable=False),
        sa.Column('verdict', sa.Enum('PENDING', 'JUDGING', 'AC', 'WA', 'TLE', 'MLE', 'RE', 'CE', 'OLE', name='submissionverdict'), nullable=True),
        sa.Column('time_ms', sa.Integer(), nullable=True),
        sa.Column('memory_kb', sa.Integer(), nullable=True),
        sa.Column('compile_log', sa.Text(), nullable=True),
        sa.Column('first_failed_test', sa.Integer(), nullable=True),
        sa.Column('test_results', sa.JSON(), nullable=True),
        sa.Column('integrity_flagged', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('judged_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['attempt_id'], ['attempts.id'], ),
        sa.ForeignKeyConstraint(['problem_id'], ['problems.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_submissions_id'), 'submissions', ['id'], unique=False)

    # Create gamification tables
    op.create_table('gamification_profiles',
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('xp', sa.Integer(), nullable=True),
        sa.Column('level', sa.Integer(), nullable=True),
        sa.Column('streak_days', sa.Integer(), nullable=True),
        sa.Column('last_streak_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('problems_solved', sa.Integer(), nullable=True),
        sa.Column('total_submissions', sa.Integer(), nullable=True),
        sa.Column('fastest_solve_sec', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('user_id')
    )

    op.create_table('badges',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('criteria_json', sa.JSON(), nullable=False),
        sa.Column('icon_url', sa.String(), nullable=True),
        sa.Column('rarity', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_badges_id'), 'badges', ['id'], unique=False)

    op.create_table('user_badges',
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('badge_id', sa.Integer(), nullable=False),
        sa.Column('awarded_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('problem_id', sa.Integer(), nullable=True),
        sa.Column('submission_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['badge_id'], ['badges.id'], ),
        sa.ForeignKeyConstraint(['problem_id'], ['problems.id'], ),
        sa.ForeignKeyConstraint(['submission_id'], ['submissions.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('user_id', 'badge_id')
    )

    # Create integrity events table
    op.create_table('integrity_events',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('session_id', sa.String(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('ts', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('ai_detected', sa.Integer(), nullable=True),
        sa.Column('multi_display', sa.Integer(), nullable=True),
        sa.Column('clipboard_blocked', sa.Integer(), nullable=True),
        sa.Column('screen_capture_blocked', sa.Integer(), nullable=True),
        sa.Column('sources_json', sa.Text(), nullable=True),
        sa.Column('app_version', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_integrity_events_id'), 'integrity_events', ['id'], unique=False)
    op.create_index(op.f('ix_integrity_events_session_id'), 'integrity_events', ['session_id'], unique=False)

    # Create platform settings table
    op.create_table('platform_settings',
        sa.Column('key', sa.String(), nullable=False),
        sa.Column('value', sa.Text(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('key')
    )


def downgrade() -> None:
    op.drop_table('platform_settings')
    op.drop_index(op.f('ix_integrity_events_session_id'), table_name='integrity_events')
    op.drop_index(op.f('ix_integrity_events_id'), table_name='integrity_events')
    op.drop_table('integrity_events')
    op.drop_table('user_badges')
    op.drop_index(op.f('ix_badges_id'), table_name='badges')
    op.drop_table('badges')
    op.drop_table('gamification_profiles')
    op.drop_index(op.f('ix_submissions_id'), table_name='submissions')
    op.drop_table('submissions')
    op.drop_index(op.f('ix_attempts_id'), table_name='attempts')
    op.drop_table('attempts')
    op.drop_index(op.f('ix_testcases_id'), table_name='testcases')
    op.drop_table('testcases')
    op.drop_index(op.f('ix_problems_slug'), table_name='problems')
    op.drop_index(op.f('ix_problems_id'), table_name='problems')
    op.drop_table('problems')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_table('users')
