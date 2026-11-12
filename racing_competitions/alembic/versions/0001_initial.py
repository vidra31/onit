"""Initial racing competition schema.

Revision ID: 0001
Revises:
"""
from alembic import op
import sqlalchemy as sa
revision = "0001"
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table("teams", sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(120), nullable=False, unique=True),
        sa.Column("country", sa.String(80), nullable=False))
    op.create_table("drivers", sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("number", sa.Integer(), nullable=False, unique=True),
        sa.Column("team_id", sa.Integer(), sa.ForeignKey("teams.id", ondelete="RESTRICT"), nullable=False),
        sa.CheckConstraint("number BETWEEN 1 AND 999", name="ck_driver_number"))
    op.create_table("races", sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(150), nullable=False),
        sa.Column("circuit", sa.String(150), nullable=False),
        sa.Column("laps", sa.Integer(), nullable=False),
        sa.CheckConstraint("laps BETWEEN 1 AND 1000", name="ck_race_laps"))
    op.create_table("results", sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("race_id", sa.Integer(), sa.ForeignKey("races.id", ondelete="CASCADE"), nullable=False),
        sa.Column("driver_id", sa.Integer(), sa.ForeignKey("drivers.id", ondelete="CASCADE"), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("points", sa.Integer(), nullable=False),
        sa.UniqueConstraint("race_id", "driver_id", name="uq_race_driver"),
        sa.UniqueConstraint("race_id", "position", name="uq_race_position"),
        sa.CheckConstraint("position > 0", name="ck_result_position"),
        sa.CheckConstraint("points BETWEEN 0 AND 1000", name="ck_result_points"))

def downgrade():
    op.drop_table("results")
    op.drop_table("races")
    op.drop_table("drivers")
    op.drop_table("teams")
