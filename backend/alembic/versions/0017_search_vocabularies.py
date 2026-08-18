"""Add maintainable Search Profile vocabularies."""

from __future__ import annotations

import json
from datetime import UTC, datetime

from alembic import op
import sqlalchemy as sa

revision = "0017"
down_revision = "0016"
branch_labels = None
depends_on = None


def _normalize(value: str) -> str:
    return " ".join(value.strip().casefold().split())


def _row(
    entry_id: str,
    kind: str,
    label: str,
    *,
    aliases: tuple[str, ...] = (),
    group: str | None = None,
) -> dict[str, object]:
    now = datetime.now(UTC)
    return {
        "id": entry_id,
        "kind": kind,
        "label": label,
        "normalized_label": _normalize(label),
        "aliases_json": json.dumps(list(aliases), ensure_ascii=False),
        "group_name": group,
        "is_active": True,
        "is_custom": False,
        "created_at": now,
        "updated_at": now,
    }


def upgrade() -> None:
    table = op.create_table(
        "search_vocabulary_entries",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("kind", sa.String(32), nullable=False),
        sa.Column("label", sa.String(160), nullable=False),
        sa.Column("normalized_label", sa.String(160), nullable=False),
        sa.Column("aliases_json", sa.Text(), nullable=False),
        sa.Column("group_name", sa.String(120), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("is_custom", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("kind", "normalized_label", name="uq_search_vocabulary_kind_label"),
    )
    op.create_index(
        "ix_search_vocabulary_entries_kind",
        "search_vocabulary_entries",
        ["kind"],
    )

    op.bulk_insert(
        table,
        [
            _row(
                "role-software-developer",
                "role",
                "Softwareentwickler",
                aliases=("Software Developer", "Softwareentwicklerin"),
                group="Softwareentwicklung",
            ),
            _row(
                "role-software-engineer",
                "role",
                "Software Engineer",
                aliases=("Software Engineering",),
                group="Softwareentwicklung",
            ),
            _row(
                "role-backend-developer",
                "role",
                "Backend Developer",
                aliases=("Backend Engineer", "Backend-Entwickler"),
                group="Softwareentwicklung",
            ),
            _row(
                "role-frontend-developer",
                "role",
                "Frontend Developer",
                aliases=("Frontend Engineer", "Frontend-Entwickler"),
                group="Softwareentwicklung",
            ),
            _row(
                "role-fullstack-developer",
                "role",
                "Full-Stack Developer",
                aliases=("Full Stack Developer", "Fullstack Developer"),
                group="Softwareentwicklung",
            ),
            _row(
                "role-java-developer",
                "role",
                "Java Developer",
                aliases=("Java-Entwickler", "Java Software Engineer"),
                group="Softwareentwicklung",
            ),
            _row(
                "role-cpp-developer",
                "role",
                "C++ Developer",
                aliases=("C++ Entwickler", "C++ Software Engineer"),
                group="Softwareentwicklung",
            ),
            _row(
                "role-python-developer",
                "role",
                "Python Developer",
                aliases=("Python Engineer", "Python-Entwickler"),
                group="Softwareentwicklung",
            ),
            _row(
                "role-embedded-engineer",
                "role",
                "Embedded Software Engineer",
                aliases=("Embedded Developer", "Embedded Softwareentwickler"),
                group="Embedded",
            ),
            _row(
                "role-test-automation-engineer",
                "role",
                "Test Automation Engineer",
                aliases=("QA Automation Engineer", "Testautomatisierer"),
                group="Qualität",
            ),
            _row(
                "role-devops-engineer",
                "role",
                "DevOps Engineer",
                aliases=("Platform Engineer",),
                group="Platform & Operations",
            ),
            _row(
                "role-cloud-engineer",
                "role",
                "Cloud Engineer",
                aliases=("Cloud Developer",),
                group="Platform & Operations",
            ),
            _row(
                "role-security-engineer",
                "role",
                "Security Engineer",
                aliases=("Software Security Engineer",),
                group="Security",
            ),
            _row(
                "role-ai-engineer",
                "role",
                "AI Engineer",
                aliases=("Artificial Intelligence Engineer",),
                group="AI & Data",
            ),
            _row(
                "role-ml-engineer",
                "role",
                "Machine Learning Engineer",
                aliases=("ML Engineer",),
                group="AI & Data",
            ),
            _row(
                "role-data-engineer",
                "role",
                "Data Engineer",
                aliases=("Data Platform Engineer",),
                group="AI & Data",
            ),
            _row("tech-java", "technology", "Java", group="Programmiersprache"),
            _row("tech-cpp", "technology", "C++", aliases=("CPP",), group="Programmiersprache"),
            _row("tech-c", "technology", "C", group="Programmiersprache"),
            _row("tech-python", "technology", "Python", group="Programmiersprache"),
            _row("tech-javascript", "technology", "JavaScript", aliases=("JS",), group="Programmiersprache"),
            _row("tech-typescript", "technology", "TypeScript", aliases=("TS",), group="Programmiersprache"),
            _row("tech-csharp", "technology", "C#", aliases=("C Sharp",), group="Programmiersprache"),
            _row("tech-rust", "technology", "Rust", group="Programmiersprache"),
            _row("tech-go", "technology", "Go", aliases=("Golang",), group="Programmiersprache"),
            _row("tech-kotlin", "technology", "Kotlin", group="Programmiersprache"),
            _row("tech-react", "technology", "React", aliases=("React.js",), group="Frontend"),
            _row("tech-nodejs", "technology", "Node.js", aliases=("NodeJS", "Node"), group="Backend"),
            _row("tech-spring-boot", "technology", "Spring Boot", aliases=("Spring",), group="Backend"),
            _row("tech-maven", "technology", "Maven", group="Build & Tooling"),
            _row("tech-cmake", "technology", "CMake", group="Build & Tooling"),
            _row("tech-git", "technology", "Git", group="Build & Tooling"),
            _row("tech-docker", "technology", "Docker", group="Platform"),
            _row("tech-kubernetes", "technology", "Kubernetes", aliases=("K8s",), group="Platform"),
            _row("tech-linux", "technology", "Linux", group="Platform"),
            _row("tech-postgresql", "technology", "PostgreSQL", aliases=("Postgres",), group="Datenbank"),
            _row("tech-sql", "technology", "SQL", group="Datenbank"),
            _row("tech-aws", "technology", "AWS", aliases=("Amazon Web Services",), group="Cloud"),
            _row("tech-azure", "technology", "Azure", aliases=("Microsoft Azure",), group="Cloud"),
            _row("industry-software", "industry", "Software / SaaS", aliases=("Software", "SaaS"), group="IT"),
            _row("industry-it-services", "industry", "IT Services", aliases=("IT-Dienstleistungen",), group="IT"),
            _row("industry-cybersecurity", "industry", "Cybersecurity", aliases=("IT Security", "Informationssicherheit"), group="IT"),
            _row("industry-ai", "industry", "AI / Machine Learning", aliases=("Künstliche Intelligenz", "KI"), group="IT"),
            _row("industry-fintech", "industry", "Finance / FinTech", aliases=("FinTech", "Finanzdienstleistungen"), group="Finance"),
            _row("industry-health", "industry", "Healthcare / MedTech", aliases=("MedTech", "Gesundheitswesen"), group="Health"),
            _row("industry-industry", "industry", "Industrie / Manufacturing", aliases=("Manufacturing", "Produktion"), group="Industrie"),
            _row("industry-automotive", "industry", "Automotive", aliases=("Automobil",), group="Industrie"),
            _row("industry-public", "industry", "Öffentlicher Sektor", aliases=("Public Sector", "Verwaltung"), group="Public"),
            _row("industry-ecommerce", "industry", "E-Commerce", aliases=("Onlinehandel",), group="Digital"),
            _row("industry-media", "industry", "Medien", aliases=("Media",), group="Digital"),
            _row("industry-education", "industry", "Bildung / EdTech", aliases=("Education", "EdTech"), group="Education"),
            _row("seniority-internship", "seniority", "Praktikum", aliases=("Internship", "Intern")),
            _row("seniority-trainee", "seniority", "Trainee", aliases=("Graduate Program",)),
            _row("seniority-entry", "seniority", "Entry Level", aliases=("Berufseinstieg", "Entry-Level")),
            _row("seniority-junior", "seniority", "Junior", aliases=("Jr", "Jr.")),
            _row("seniority-mid", "seniority", "Mid Level", aliases=("Professional", "Intermediate")),
            _row("seniority-senior", "seniority", "Senior", aliases=("Sr", "Sr.")),
            _row("seniority-lead", "seniority", "Lead", aliases=("Tech Lead", "Technical Lead")),
            _row("employment-full-time", "employment_type", "Vollzeit", aliases=("Full-time", "Full time")),
            _row("employment-part-time", "employment_type", "Teilzeit", aliases=("Part-time", "Part time")),
            _row("employment-working-student", "employment_type", "Werkstudent", aliases=("Working Student",)),
            _row("employment-internship", "employment_type", "Praktikum", aliases=("Internship",)),
            _row("employment-trainee", "employment_type", "Trainee"),
            _row("employment-contract", "employment_type", "Freelance / Contract", aliases=("Freelance", "Contract")),
        ],
    )


def downgrade() -> None:
    op.drop_index("ix_search_vocabulary_entries_kind", table_name="search_vocabulary_entries")
    op.drop_table("search_vocabulary_entries")
