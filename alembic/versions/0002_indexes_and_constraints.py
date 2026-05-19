"""add indexes and integrity constraints

Revision ID: 0002
Revises: 0001
Create Date: 2026-05-19
"""
import sqlalchemy as sa
from alembic import op

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # quarterly_declarations: one declaration per facility per quarter
    op.create_unique_constraint(
        "uq_declaration_facility_year_quarter",
        "quarterly_declarations",
        ["facility_id", "year", "quarter"],
    )

    # quality_evaluations: one score per checklist item per declaration
    op.create_unique_constraint(
        "uq_evaluation_declaration_item",
        "quality_evaluations",
        ["declaration_id", "item_id"],
    )

    # health_facilities: peer-group queries (anomaly detection)
    op.create_index("ix_facility_region_type", "health_facilities", ["region", "type"])

    # rule_sets: temporal range queries
    op.create_index("ix_ruleset_effective", "rule_sets", ["effective_from", "effective_to"])

    # quantity_declarations: join performance
    op.create_index(
        "ix_quantity_declaration_declaration_id",
        "quantity_declarations",
        ["declaration_id"],
    )

    # quality_evaluations: join performance
    op.create_index(
        "ix_quality_evaluation_declaration_id",
        "quality_evaluations",
        ["declaration_id"],
    )

    # verification_audits: join performance
    op.create_index(
        "ix_verification_audit_declaration_id",
        "verification_audits",
        ["declaration_id"],
    )

    # quarterly_declarations: listing by facility
    op.create_index(
        "ix_quarterly_declaration_facility_id",
        "quarterly_declarations",
        ["facility_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_quarterly_declaration_facility_id", "quarterly_declarations")
    op.drop_index("ix_verification_audit_declaration_id", "verification_audits")
    op.drop_index("ix_quality_evaluation_declaration_id", "quality_evaluations")
    op.drop_index("ix_quantity_declaration_declaration_id", "quantity_declarations")
    op.drop_index("ix_ruleset_effective", "rule_sets")
    op.drop_index("ix_facility_region_type", "health_facilities")
    op.drop_constraint("uq_evaluation_declaration_item", "quality_evaluations")
    op.drop_constraint("uq_declaration_facility_year_quarter", "quarterly_declarations")
