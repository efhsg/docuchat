"""Add domains table and domain_id to extracted_texts

Revision ID: d0090ad818e3
Revises: 6837d7b9fc2e
Create Date: 2024-02-13 01:35:04.309994

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import text


# revision identifiers, used by Alembic.
revision: str = "d0090ad818e3"
down_revision: Union[str, None] = "6837d7b9fc2e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table(
        "domains",
        sa.Column(
            "id", sa.Integer, nullable=False, autoincrement=True, primary_key=True
        ),
        sa.Column("name", sa.String(255), nullable=False, unique=True),
        mysql_charset="utf8mb4",
        mysql_collate="utf8mb4_0900_ai_ci",
    )

    op.add_column(
        "extracted_texts",
        sa.Column(
            "domain_id",
            sa.Integer,
            nullable=False,
        ),
    )

    op.create_foreign_key(
        "fk_domain_id", "extracted_texts", "domains", ["domain_id"], ["id"]
    )


def downgrade():
    op.drop_constraint("fk_domain_id", "extracted_texts", type_="foreignkey")
    op.drop_column("extracted_texts", "domain_id")

    op.drop_table("domains")
