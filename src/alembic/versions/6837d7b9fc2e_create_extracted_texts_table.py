"""Create extracted_texts table

Revision ID: 6837d7b9fc2e
Revises: 
Create Date: 2024-02-13 00:41:28.343481

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "6837d7b9fc2e"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "extracted_texts",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(255), nullable=False, unique=True),
        sa.Column("text", sa.LargeBinary, nullable=False),
        mysql_charset="utf8mb4",
        mysql_collate="utf8mb4_0900_ai_ci",
    )


def downgrade():
    op.drop_table("extracted_texts")
