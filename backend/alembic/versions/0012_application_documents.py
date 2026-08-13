"""Persist Application Document metadata linked to immutable material revisions."""

import sqlalchemy as sa
from alembic import op

revision = "0012"
down_revision = "0011"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "application_documents",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("material_id", sa.String(36), nullable=False),
        sa.Column("material_revision", sa.Integer(), nullable=False),
        sa.Column("original_filename", sa.String(300), nullable=False),
        sa.Column("media_type", sa.String(100), nullable=False),
        sa.Column("byte_size", sa.Integer(), nullable=False),
        sa.Column("sha256", sa.String(64), nullable=False),
        sa.Column("storage_ref", sa.String(500), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["material_id", "material_revision"],
            ["application_material_revisions.material_id", "application_material_revisions.revision"],
            name="fk_application_documents_material_revision",
        ),
        sa.UniqueConstraint("material_id", "material_revision", name="uq_application_documents_material_revision"),
        sa.CheckConstraint("material_revision >= 1", name="ck_application_documents_material_revision"),
        sa.CheckConstraint("byte_size >= 0", name="ck_application_documents_byte_size"),
        sa.CheckConstraint("length(trim(original_filename)) > 0", name="ck_application_documents_filename_nonempty"),
        sa.CheckConstraint("length(trim(storage_ref)) > 0", name="ck_application_documents_storage_ref_nonempty"),
        sa.CheckConstraint(
            "media_type IN ('application/pdf','text/plain','text/markdown')",
            name="ck_application_documents_media_type",
        ),
        sa.CheckConstraint(
            "length(sha256) = 64 AND sha256 = lower(sha256) AND sha256 NOT GLOB '*[^0-9a-f]*'",
            name="ck_application_documents_sha256",
        ),
    )


def downgrade() -> None:
    op.drop_table("application_documents")
