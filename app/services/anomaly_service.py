from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.engine.anomaly import detect_anomalies
from app.models.health_facility import HealthFacility
from app.models.quality_evaluation import QualityEvaluation
from app.models.quantity_declaration import QuantityDeclaration
from app.models.quarterly_declaration import QuarterlyDeclaration
from app.schemas.audit import AnomalyResult


async def run(session: AsyncSession, declaration_id: int) -> AnomalyResult:
    declaration = await session.get(QuarterlyDeclaration, declaration_id)
    if declaration is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Declaration not found")

    facility = await session.get(HealthFacility, declaration.facility_id)

    current_quantities = await _get_quantities(session, declaration_id)
    current_quality = await _get_quality_score(session, declaration_id)
    discrepancy_rates = await _get_discrepancy_rates(session, declaration_id)

    historical_qtys, historical_scores = await _get_facility_history(
        session, declaration.facility_id, declaration.year, declaration.quarter
    )
    peer_qtys = await _get_peer_quantities(
        session, facility, declaration.year, declaration.quarter, declaration_id
    )

    return detect_anomalies(
        current_quantities=current_quantities,
        historical_quantities=historical_qtys,
        peer_quantities=peer_qtys,
        current_quality_score=current_quality,
        historical_quality_scores=historical_scores,
        discrepancy_rates=discrepancy_rates,
    )


async def _get_discrepancy_rates(session: AsyncSession, declaration_id: int) -> dict[str, Decimal]:
    from app.models.quantity_indicator import QuantityIndicator
    result = await session.execute(
        select(QuantityDeclaration, QuantityIndicator)
        .join(QuantityIndicator, QuantityDeclaration.indicator_id == QuantityIndicator.id)
        .where(QuantityDeclaration.declaration_id == declaration_id)
    )
    return {ind.code: qty.discrepancy_rate for qty, ind in result.all()}


async def _get_quantities(session: AsyncSession, declaration_id: int) -> dict[str, Decimal]:
    from app.models.quantity_indicator import QuantityIndicator
    result = await session.execute(
        select(QuantityDeclaration, QuantityIndicator)
        .join(QuantityIndicator, QuantityDeclaration.indicator_id == QuantityIndicator.id)
        .where(QuantityDeclaration.declaration_id == declaration_id)
    )
    return {ind.code: qty.verified_quantity for qty, ind in result.all()}


async def _get_quality_score(session: AsyncSession, declaration_id: int) -> Decimal:
    result = await session.execute(
        select(QualityEvaluation).where(QualityEvaluation.declaration_id == declaration_id)
    )
    evals = result.scalars().all()
    if not evals:
        return Decimal("0")
    total_max = sum(e.max_score for e in evals)
    if total_max == Decimal("0"):
        return Decimal("0")
    return sum(e.score_obtained for e in evals) / total_max


async def _get_facility_history(
    session: AsyncSession, facility_id: int, current_year: int, current_quarter: int
) -> tuple[list[dict[str, Decimal]], list[Decimal]]:
    result = await session.execute(
        select(QuarterlyDeclaration)
        .where(
            QuarterlyDeclaration.facility_id == facility_id,
            ~(
                (QuarterlyDeclaration.year == current_year)
                & (QuarterlyDeclaration.quarter == current_quarter)
            ),
        )
        .order_by(QuarterlyDeclaration.year.desc(), QuarterlyDeclaration.quarter.desc())
        .limit(4)
    )
    past_declarations = result.scalars().all()

    historical_qtys = []
    historical_scores = []
    for decl in past_declarations:
        qtys = await _get_quantities(session, decl.id)
        historical_qtys.append(qtys)
        score = await _get_quality_score(session, decl.id)
        historical_scores.append(score)

    return list(reversed(historical_qtys)), list(reversed(historical_scores))


async def _get_peer_quantities(
    session: AsyncSession,
    facility: HealthFacility,
    year: int,
    quarter: int,
    exclude_declaration_id: int,
) -> list[dict[str, Decimal]]:
    peer_result = await session.execute(
        select(QuarterlyDeclaration)
        .join(HealthFacility, QuarterlyDeclaration.facility_id == HealthFacility.id)
        .where(
            HealthFacility.type == facility.type,
            HealthFacility.region == facility.region,
            QuarterlyDeclaration.year == year,
            QuarterlyDeclaration.quarter == quarter,
            QuarterlyDeclaration.id != exclude_declaration_id,
        )
    )
    peer_declarations = peer_result.scalars().all()
    return [await _get_quantities(session, d.id) for d in peer_declarations]
