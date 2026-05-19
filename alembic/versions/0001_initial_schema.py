"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-05-19
"""
from decimal import Decimal

import sqlalchemy as sa
from alembic import op

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "health_facilities",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("type", sa.String(50), nullable=False),
        sa.Column("region", sa.String(100), nullable=False),
        sa.Column("district", sa.String(100), nullable=False),
        sa.Column("is_rural", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("equity_coefficient", sa.Numeric(4, 2), nullable=False, server_default="1.0"),
        sa.CheckConstraint(
            "equity_coefficient >= 1.0 AND equity_coefficient <= 1.5",
            name="ck_equity_coefficient_range",
        ),
    )

    op.create_table(
        "quantity_indicators",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("code", sa.String(30), nullable=False, unique=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("unit_tariff", sa.Numeric(14, 2), nullable=False),
        sa.Column("service_category", sa.String(50), nullable=False),
    )

    op.create_table(
        "quality_checklist_items",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("code", sa.String(30), nullable=False, unique=True),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("service_area", sa.String(50), nullable=False),
        sa.Column("max_points", sa.Numeric(6, 2), nullable=False),
        sa.Column("applies_to_facility_type", sa.String(50), nullable=True),
    )

    op.create_table(
        "rule_sets",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("quality_threshold", sa.Numeric(4, 2), nullable=False, server_default="0.50"),
        sa.Column("quality_multiplier_mode", sa.String(20), nullable=False, server_default="deflator"),
        sa.Column("abatement_brackets", sa.JSON(), nullable=False),
        sa.Column("equity_min", sa.Numeric(4, 2), nullable=False, server_default="1.0"),
        sa.Column("equity_max", sa.Numeric(4, 2), nullable=False, server_default="1.5"),
        sa.Column("payment_floor", sa.Numeric(14, 2), nullable=False, server_default="0"),
        sa.Column("bonus_above_quality", sa.Numeric(4, 2), nullable=True),
        sa.Column("bonus_pct", sa.Numeric(4, 2), nullable=True),
        sa.Column("effective_from", sa.Date(), nullable=False),
        sa.Column("effective_to", sa.Date(), nullable=True),
    )

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(200), nullable=False, unique=True),
        sa.Column("hashed_password", sa.String(200), nullable=False),
        sa.Column("role", sa.String(30), nullable=False, server_default="facility_user"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    declaration_status = sa.Enum(
        "draft", "declared", "verified", "paid", "rejected",
        name="declaration_status",
    )
    declaration_status.create(op.get_bind())

    op.create_table(
        "quarterly_declarations",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("facility_id", sa.Integer(), sa.ForeignKey("health_facilities.id"), nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("quarter", sa.Integer(), nullable=False),
        sa.Column("status", declaration_status, nullable=False, server_default="draft"),
        sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "quantity_declarations",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("declaration_id", sa.Integer(), sa.ForeignKey("quarterly_declarations.id"), nullable=False),
        sa.Column("indicator_id", sa.Integer(), sa.ForeignKey("quantity_indicators.id"), nullable=False),
        sa.Column("declared_quantity", sa.Numeric(12, 2), nullable=False),
        sa.Column("verified_quantity", sa.Numeric(12, 2), nullable=False),
        sa.Column("discrepancy_rate", sa.Numeric(6, 4), nullable=False, server_default="0"),
    )

    op.create_table(
        "quality_evaluations",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("declaration_id", sa.Integer(), sa.ForeignKey("quarterly_declarations.id"), nullable=False),
        sa.Column("item_id", sa.Integer(), sa.ForeignKey("quality_checklist_items.id"), nullable=False),
        sa.Column("score_obtained", sa.Numeric(6, 2), nullable=False),
        sa.Column("max_score", sa.Numeric(6, 2), nullable=False),
        sa.Column("evaluator_notes", sa.Text(), nullable=True),
    )

    op.create_table(
        "payments",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("declaration_id", sa.Integer(), sa.ForeignKey("quarterly_declarations.id"), nullable=False, unique=True),
        sa.Column("quantity_subtotal", sa.Numeric(14, 2), nullable=False),
        sa.Column("quality_score_pct", sa.Numeric(6, 4), nullable=False),
        sa.Column("equity_multiplier", sa.Numeric(4, 2), nullable=False),
        sa.Column("gross_amount", sa.Numeric(14, 2), nullable=False),
        sa.Column("abatement_pct", sa.Numeric(6, 4), nullable=False, server_default="0"),
        sa.Column("abatement_reason", sa.Text(), nullable=True),
        sa.Column("net_amount", sa.Numeric(14, 2), nullable=False),
        sa.Column("fraud_flag", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("paid_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("computed_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    audit_type = sa.Enum(
        "community", "counter_verification", "risk_based",
        name="audit_type",
    )
    audit_type.create(op.get_bind())

    op.create_table(
        "verification_audits",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("declaration_id", sa.Integer(), sa.ForeignKey("quarterly_declarations.id"), nullable=False),
        sa.Column("audit_type", audit_type, nullable=False),
        sa.Column("patients_sampled", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("patients_confirmed", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("anomaly_flag", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("conducted_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("verification_audits")
    sa.Enum(name="audit_type").drop(op.get_bind())
    op.drop_table("payments")
    op.drop_table("quality_evaluations")
    op.drop_table("quantity_declarations")
    op.drop_table("quarterly_declarations")
    sa.Enum(name="declaration_status").drop(op.get_bind())
    op.drop_table("users")
    op.drop_table("rule_sets")
    op.drop_table("quality_checklist_items")
    op.drop_table("quantity_indicators")
    op.drop_table("health_facilities")
