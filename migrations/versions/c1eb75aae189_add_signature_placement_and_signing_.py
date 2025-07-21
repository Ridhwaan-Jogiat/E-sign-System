"""Add signature_placement and signing_method to Document

Revision ID: c1eb75aae189
Revises: b1ae4566941e
Create Date: 2025-05-08 10:28:12.303424

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c1eb75aae189'
down_revision = 'b1ae4566941e'
branch_labels = None
depends_on = None


def upgrade():
    # This migration is now a no-op because signature_placement and signing_method already exist in the database.
    pass


def downgrade():
    # This migration is now a no-op because signature_placement and signing_method already exist in the database.
    pass
