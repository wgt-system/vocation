"""Persist current map location resolutions."""

import sqlalchemy as sa
from alembic import op

revision = "0010"
down_revision = "0009"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "map_location_resolutions",
        sa.Column(
            "work_location_id",
            sa.String(36),
            sa.ForeignKey("work_locations.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("latitude", sa.Float(), nullable=False),
        sa.Column("longitude", sa.Float(), nullable=False),
        sa.Column("resolution_source", sa.String(20), nullable=False),
        sa.Column("provider_key", sa.String(200)),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("resolved_query", sa.Text(), nullable=False),
        sa.CheckConstraint("latitude >= -90 AND latitude <= 90", name="ck_map_location_resolutions_latitude"),
        sa.CheckConstraint("longitude >= -180 AND longitude <= 180", name="ck_map_location_resolutions_longitude"),
        sa.CheckConstraint(
            "resolution_source IN ('manual','geocoder')",
            name="ck_map_location_resolutions_source",
        ),
        sa.CheckConstraint("length(trim(resolved_query)) > 0", name="ck_map_location_resolutions_query_nonempty"),
        sa.CheckConstraint(
            "(resolution_source = 'manual' AND provider_key IS NULL) "
            "OR (resolution_source = 'geocoder' AND length(trim(provider_key)) > 0)",
            name="ck_map_location_resolutions_provider",
        ),
    )


def downgrade() -> None:
    op.drop_table("map_location_resolutions")
