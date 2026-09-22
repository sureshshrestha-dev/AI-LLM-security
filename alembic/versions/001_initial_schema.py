"""Initial Schema Migration

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-09-22 12:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('username', sa.String(length=50), nullable=False, unique=True, index=True),
        sa.Column('email', sa.String(length=100), nullable=False, unique=True, index=True),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('score', sa.Integer(), nullable=False, default=0),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False)
    )

    op.create_table(
        'challenges',
        sa.Column('id', sa.String(length=50), nullable=False, primary_key=True),
        sa.Column('title', sa.String(length=100), nullable=False),
        sa.Column('category', sa.String(length=50), nullable=False),
        sa.Column('difficulty', sa.String(length=20), nullable=False),
        sa.Column('points', sa.Integer(), nullable=False, default=100),
        sa.Column('flag', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('vulnerable_endpoint', sa.String(length=100), nullable=True),
        sa.Column('safe_endpoint', sa.String(length=100), nullable=True)
    )

    op.create_table(
        'user_progress',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('challenge_id', sa.String(length=50), sa.ForeignKey('challenges.id'), nullable=False),
        sa.Column('is_solved', sa.Boolean(), nullable=False, default=True),
        sa.Column('solved_at', sa.DateTime(timezone=True), nullable=False)
    )

    op.create_table(
        'academic_students',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('student_code', sa.String(length=20), nullable=False, unique=True),
        sa.Column('full_name', sa.String(length=100), nullable=False),
        sa.Column('email', sa.String(length=100), nullable=False),
        sa.Column('department', sa.String(length=50), nullable=False),
        sa.Column('gpa', sa.Float(), nullable=False, default=3.5),
        sa.Column('academic_notes', sa.Text(), nullable=False)
    )

    op.create_table(
        'knowledge_documents',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('doc_key', sa.String(length=50), nullable=False, unique=True, index=True),
        sa.Column('title', sa.String(length=100), nullable=False),
        sa.Column('classification', sa.String(length=20), nullable=False, default='Public'),
        sa.Column('content', sa.Text(), nullable=False)
    )

def downgrade() -> None:
    op.drop_table('knowledge_documents')
    op.drop_table('academic_students')
    op.drop_table('user_progress')
    op.drop_table('challenges')
    op.drop_table('users')
