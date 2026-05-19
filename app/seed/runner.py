from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.health_facility import HealthFacility
from app.models.quality_checklist_item import QualityChecklistItem
from app.models.quantity_indicator import QuantityIndicator
from app.models.rule_set import RuleSet
from app.seed.checklist import CHECKLIST_ITEMS
from app.seed.facilities import FACILITIES
from app.seed.indicators import INDICATORS


async def seed(session: AsyncSession) -> None:
    await _seed_facilities(session)
    await _seed_indicators(session)
    await _seed_checklist(session)
    await _seed_default_ruleset(session)
    await session.commit()
    print("Seed complete.")  # noqa: T201


async def _seed_facilities(session: AsyncSession) -> None:
    for data in FACILITIES:
        existing = await session.execute(
            select(HealthFacility).where(HealthFacility.name == data["name"])
        )
        if existing.scalar_one_or_none() is None:
            session.add(HealthFacility(**data))
    print(f"  Facilities: {len(FACILITIES)} processed")  # noqa: T201


async def _seed_indicators(session: AsyncSession) -> None:
    for data in INDICATORS:
        existing = await session.execute(
            select(QuantityIndicator).where(QuantityIndicator.code == data["code"])
        )
        if existing.scalar_one_or_none() is None:
            session.add(QuantityIndicator(**data))
    print(f"  Indicators: {len(INDICATORS)} processed")  # noqa: T201


async def _seed_checklist(session: AsyncSession) -> None:
    for data in CHECKLIST_ITEMS:
        existing = await session.execute(
            select(QualityChecklistItem).where(QualityChecklistItem.code == data["code"])
        )
        if existing.scalar_one_or_none() is None:
            session.add(QualityChecklistItem(**data))
    print(f"  Checklist items: {len(CHECKLIST_ITEMS)} processed")  # noqa: T201


async def _seed_default_ruleset(session: AsyncSession) -> None:
    existing = await session.execute(
        select(RuleSet).where(RuleSet.name == "Mauritanie Standard 2024")
    )
    if existing.scalar_one_or_none() is None:
        session.add(RuleSet(
            name="Mauritanie Standard 2024",
            description="Règles FBP standard Mauritanie — programme INAYA 2024",
            quality_threshold="0.50",
            quality_multiplier_mode="deflator",
            abatement_brackets=[
                {"max_discrepancy": "0.05", "abatement_factor": "0"},
                {"max_discrepancy": "0.10", "abatement_factor": "1"},
            ],
            equity_min="1.0",
            equity_max="1.5",
            payment_floor="0",
            bonus_above_quality=None,
            bonus_pct=None,
            effective_from=date(2024, 1, 1),
            effective_to=None,
        ))
    print("  Default ruleset processed")  # noqa: T201
