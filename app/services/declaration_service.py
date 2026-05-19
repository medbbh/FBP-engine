from decimal import Decimal
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.quality_checklist_item import QualityChecklistItem
from app.models.quality_evaluation import QualityEvaluation
from app.models.quantity_declaration import QuantityDeclaration
from app.models.quantity_indicator import QuantityIndicator
from app.models.quarterly_declaration import QuarterlyDeclaration
from app.schemas.declaration import DeclarationCreate, DeclarationRead
from app.schemas.quality import QualityRead, QualitySubmit
from app.schemas.quantity import QuantityRead, QuantitySubmit


async def create_declaration(session: AsyncSession, data: DeclarationCreate) -> DeclarationRead:
    existing = await session.execute(
        select(QuarterlyDeclaration).where(
            QuarterlyDeclaration.facility_id == data.facility_id,
            QuarterlyDeclaration.year == data.year,
            QuarterlyDeclaration.quarter == data.quarter,
        )
    )
    if existing.scalar_one_or_none() is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Declaration for facility {data.facility_id} Q{data.quarter}/{data.year} already exists",
        )

    declaration = QuarterlyDeclaration(**data.model_dump())
    session.add(declaration)
    await session.flush()
    await session.refresh(declaration)
    return DeclarationRead.model_validate(declaration)


async def get_declaration(session: AsyncSession, declaration_id: int) -> QuarterlyDeclaration:
    result = await session.execute(
        select(QuarterlyDeclaration).where(QuarterlyDeclaration.id == declaration_id)
    )
    declaration = result.scalar_one_or_none()
    if declaration is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Declaration not found")
    return declaration


async def submit_quantity(
    session: AsyncSession, declaration_id: int, items: list[QuantitySubmit]
) -> list[QuantityRead]:
    declaration = await get_declaration(session, declaration_id)

    rows = []
    for item in items:
        indicator = await session.get(QuantityIndicator, item.indicator_id)
        if indicator is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Indicator {item.indicator_id} not found",
            )
        declared = item.declared_quantity
        verified = item.verified_quantity
        if declared > Decimal("0"):
            discrepancy = abs(declared - verified) / declared
        else:
            discrepancy = Decimal("0")

        row = QuantityDeclaration(
            declaration_id=declaration_id,
            indicator_id=item.indicator_id,
            declared_quantity=declared,
            verified_quantity=verified,
            discrepancy_rate=discrepancy,
        )
        session.add(row)
        rows.append(row)

    await session.flush()
    for row in rows:
        await session.refresh(row)

    declaration.submitted_at = datetime.now(timezone.utc)
    declaration.status = "declared"
    return [QuantityRead.model_validate(r) for r in rows]


async def submit_quality(
    session: AsyncSession, declaration_id: int, items: list[QualitySubmit]
) -> list[QualityRead]:
    await get_declaration(session, declaration_id)

    rows = []
    for item in items:
        checklist_item = await session.get(QualityChecklistItem, item.item_id)
        if checklist_item is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Checklist item {item.item_id} not found",
            )
        row = QualityEvaluation(
            declaration_id=declaration_id,
            item_id=item.item_id,
            score_obtained=item.score_obtained,
            max_score=item.max_score,
            evaluator_notes=item.evaluator_notes,
        )
        session.add(row)
        rows.append(row)

    await session.flush()
    for row in rows:
        await session.refresh(row)
    return [QualityRead.model_validate(r) for r in rows]
