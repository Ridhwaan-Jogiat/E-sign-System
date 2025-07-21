"""Add signed_by to Document

Revision ID: b1ae4566941e
Revises: 
Create Date: 2025-05-05 11:47:49.566799

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b1ae4566941e'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # This migration is now a no-op because signed_by already exists in the database.
    pass


def downgrade():
    # This migration is now a no-op because signed_by already exists in the database.
    pass
