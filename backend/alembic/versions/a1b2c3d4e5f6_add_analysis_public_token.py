"""add analysis public_token

Revision ID: a1b2c3d4e5f6
Revises: e062eb1193f2
Create Date: 2026-08-18 00:00:00.000000

This migration closes a privacy gap: the "analyses" table's id column counts
up one at a time (1, 2, 3...), and the API used that same number in public
result URLs. That meant anyone could "walk" the URL (/results/1, /results/2,
...) and read every anonymously submitted piece of code, including ones they
had no link to. The fix is a second column, public_token, holding a random
22-character string that's used in the URL instead — effectively impossible
to guess, unlike a small counting number.

Existing rows (if any) don't have a token yet, so this migration also
backfills one for each of them before making the column required.
"""
from typing import Sequence, Union
import secrets

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = 'e062eb1193f2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Step 1: add the column as nullable first — you can't add a NOT NULL
    # column to a table that might already have rows without first giving
    # every existing row a value.
    op.add_column('analyses', sa.Column('public_token', sa.String(length=22), nullable=True))

    # Step 2: backfill a random token onto every row that doesn't have one
    # yet. A plain column default can't do this because every row needs a
    # *different* random value, not the same fixed default.
    connection = op.get_bind()
    analyses_table = sa.table('analyses', sa.column('id', sa.Integer), sa.column('public_token', sa.String))
    existing_ids = connection.execute(sa.select(analyses_table.c.id)).fetchall()
    for (row_id,) in existing_ids:
        connection.execute(
            analyses_table.update()
            .where(analyses_table.c.id == row_id)
            .values(public_token=secrets.token_urlsafe(16))
        )

    # Step 3: now that every row has a value, lock the column down to what
    # it should always have been — required, and unique so two analyses can
    # never collide on the same public URL.
    op.alter_column('analyses', 'public_token', nullable=False)
    op.create_index(op.f('ix_analyses_public_token'), 'analyses', ['public_token'], unique=True)


def downgrade() -> None:
    op.drop_index(op.f('ix_analyses_public_token'), table_name='analyses')
    op.drop_column('analyses', 'public_token')
