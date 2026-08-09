"""Link prompt runs and research imports to prompt context snapshots."""

from alembic import op
import sqlalchemy as sa

revision = "0007"
down_revision = "0006"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("prompt_runs") as batch:
        batch.alter_column("search_profile", existing_type=sa.Text(), nullable=True)
        batch.add_column(
            sa.Column(
                "prompt_context_ref",
                sa.String(200),
                sa.ForeignKey(
                    "prompt_context_snapshots.prompt_context_ref",
                    name="fk_prompt_runs_prompt_context_ref",
                ),
                nullable=True,
            )
        )
        batch.create_unique_constraint("uq_prompt_runs_prompt_context_ref", ["prompt_context_ref"])

    with op.batch_alter_table("research_imports") as batch:
        batch.add_column(sa.Column("bundle_version", sa.String(20), nullable=True))
        batch.add_column(
            sa.Column(
                "prompt_context_ref",
                sa.String(200),
                sa.ForeignKey(
                    "prompt_context_snapshots.prompt_context_ref",
                    name="fk_research_imports_prompt_context_ref",
                ),
                nullable=True,
            )
        )
    op.execute("UPDATE research_imports SET bundle_version = '1.0' WHERE bundle_version IS NULL")
    op.create_index("ix_research_imports_prompt_context_ref", "research_imports", ["prompt_context_ref"])


def downgrade() -> None:
    op.drop_index("ix_research_imports_prompt_context_ref", table_name="research_imports")
    with op.batch_alter_table("research_imports") as batch:
        batch.drop_column("prompt_context_ref")
        batch.drop_column("bundle_version")

    op.execute("UPDATE prompt_runs SET search_profile = '' WHERE search_profile IS NULL")
    with op.batch_alter_table("prompt_runs") as batch:
        batch.drop_constraint("uq_prompt_runs_prompt_context_ref", type_="unique")
        batch.drop_column("prompt_context_ref")
        batch.alter_column("search_profile", existing_type=sa.Text(), nullable=False)
