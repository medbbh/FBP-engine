from datetime import date
from decimal import Decimal

from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.rule_set import RuleSet as RuleSetModel
from app.schemas.rule_set import AbatementBracket, RuleSet

DEFAULT_RULESET = RuleSet(
    quality_threshold=Decimal("0.50"),
    quality_multiplier_mode="deflator",
    abatement_brackets=[
        AbatementBracket(max_discrepancy=Decimal("0.05"), abatement_factor=Decimal("0")),
        AbatementBracket(max_discrepancy=Decimal("0.10"), abatement_factor=Decimal("1")),
    ],
    equity_min=Decimal("1.0"),
    equity_max=Decimal("1.5"),
    payment_floor=Decimal("0"),
    bonus_above_quality=None,
    bonus_pct=None,
)


async def get_active_ruleset(session: AsyncSession, declaration_date: date) -> RuleSet:
    """Return the RuleSet active on the given date. Falls back to DEFAULT_RULESET."""
    stmt = select(RuleSetModel).where(
        and_(
            RuleSetModel.effective_from <= declaration_date,
            or_(
                RuleSetModel.effective_to.is_(None),
                RuleSetModel.effective_to >= declaration_date,
            ),
        )
    ).order_by(RuleSetModel.effective_from.desc()).limit(1)

    result = await session.execute(stmt)
    db_rule = result.scalar_one_or_none()
    if db_rule is None:
        return DEFAULT_RULESET

    brackets = [
        AbatementBracket(
            max_discrepancy=Decimal(str(b["max_discrepancy"])),
            abatement_factor=Decimal(str(b["abatement_factor"])),
        )
        for b in db_rule.abatement_brackets
    ]
    return RuleSet(
        quality_threshold=db_rule.quality_threshold,
        quality_multiplier_mode=db_rule.quality_multiplier_mode,  # type: ignore[arg-type]
        abatement_brackets=brackets,
        equity_min=db_rule.equity_min,
        equity_max=db_rule.equity_max,
        payment_floor=db_rule.payment_floor,
        bonus_above_quality=db_rule.bonus_above_quality,
        bonus_pct=db_rule.bonus_pct,
    )
