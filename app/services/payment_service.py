from datetime import date, datetime, timezone
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.engine.calculations import apply_abatement, compute_payment, compute_quality_score, compute_quantity_subtotal
from app.engine.models import QualityLine, QuantityLine
from app.engine.rule_engine import get_active_ruleset
from app.models.payment import Payment
from app.models.quality_evaluation import QualityEvaluation
from app.models.quantity_declaration import QuantityDeclaration
from app.models.quantity_indicator import QuantityIndicator
from app.models.quarterly_declaration import QuarterlyDeclaration
from app.schemas.payment import PaymentBreakdown, PaymentRead


async def compute_and_persist(session: AsyncSession, declaration_id: int) -> PaymentRead:
    # Idempotent: return existing payment if already computed
    existing = await session.execute(
        select(Payment).where(Payment.declaration_id == declaration_id)
    )
    existing_payment = existing.scalar_one_or_none()
    if existing_payment is not None:
        return PaymentRead.model_validate(existing_payment)

    declaration = await session.get(QuarterlyDeclaration, declaration_id)
    if declaration is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Declaration not found")
    if declaration.status not in ("verified", "paid"):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Declaration must be verified before payment can be computed",
        )

    declaration_date = date(declaration.year, declaration.quarter * 3, 1)
    rules = await get_active_ruleset(session, declaration_date)
    facility = await session.get(type(declaration.facility if hasattr(declaration, "facility") else object), declaration.facility_id)

    # Load facility equity coefficient
    from app.models.health_facility import HealthFacility
    fac_result = await session.execute(
        select(HealthFacility).where(HealthFacility.id == declaration.facility_id)
    )
    facility = fac_result.scalar_one_or_none()
    equity = facility.equity_coefficient if facility else Decimal("1.0")

    # Build quantity lines
    qty_result = await session.execute(
        select(QuantityDeclaration, QuantityIndicator)
        .join(QuantityIndicator, QuantityDeclaration.indicator_id == QuantityIndicator.id)
        .where(QuantityDeclaration.declaration_id == declaration_id)
    )
    qty_lines = [
        QuantityLine(
            indicator_code=ind.code,
            verified_quantity=qty.verified_quantity,
            unit_tariff=ind.unit_tariff,
        )
        for qty, ind in qty_result.all()
    ]

    # Build quality lines
    qual_result = await session.execute(
        select(QualityEvaluation).where(QualityEvaluation.declaration_id == declaration_id)
    )
    qual_lines = [
        QualityLine(
            item_code=str(ev.item_id),
            score_obtained=ev.score_obtained,
            max_score=ev.max_score,
        )
        for ev in qual_result.scalars().all()
    ]

    qty_subtotal = compute_quantity_subtotal(qty_lines)
    quality_score = compute_quality_score(qual_lines)
    breakdown = compute_payment(qty_subtotal, quality_score, equity, rules)

    # Apply abatement using the maximum discrepancy across all quantity lines
    max_discrepancy = max(
        (qty.discrepancy_rate for qty in await _get_qty_rows(session, declaration_id)),
        default=Decimal("0"),
    )
    net, abatement_pct, fraud_flag, abatement_reason = apply_abatement(
        breakdown.gross_amount, max_discrepancy, rules
    )
    if breakdown.gross_amount == Decimal("0"):
        net = Decimal("0")
        abatement_reason = breakdown.abatement_reason

    payment = Payment(
        declaration_id=declaration_id,
        quantity_subtotal=qty_subtotal,
        quality_score_pct=quality_score,
        equity_multiplier=equity,
        gross_amount=breakdown.gross_amount,
        abatement_pct=abatement_pct,
        abatement_reason=abatement_reason,
        net_amount=net,
        fraud_flag=fraud_flag,
    )
    session.add(payment)
    await session.flush()
    await session.refresh(payment)
    return PaymentRead.model_validate(payment)


async def _get_qty_rows(session: AsyncSession, declaration_id: int):
    result = await session.execute(
        select(QuantityDeclaration).where(QuantityDeclaration.declaration_id == declaration_id)
    )
    return result.scalars().all()
