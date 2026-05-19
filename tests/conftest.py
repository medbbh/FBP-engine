from decimal import Decimal

import pytest

from app.engine.models import QualityLine, QuantityLine
from app.schemas.rule_set import AbatementBracket, RuleSet


@pytest.fixture
def default_ruleset() -> RuleSet:
    """Standard Mauritanian FBP ruleset."""
    return RuleSet(
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


@pytest.fixture
def sample_quantity_lines() -> list[QuantityLine]:
    return [
        QuantityLine(indicator_code="CPN1", verified_quantity=Decimal("100"), unit_tariff=Decimal("300")),
        QuantityLine(indicator_code="ACC_ASSIST", verified_quantity=Decimal("20"), unit_tariff=Decimal("1200")),
        QuantityLine(indicator_code="VAC_PENTA3", verified_quantity=Decimal("80"), unit_tariff=Decimal("300")),
    ]


@pytest.fixture
def sample_quality_lines() -> list[QualityLine]:
    return [
        QualityLine(item_code="HYG-01", score_obtained=Decimal("0.8"), max_score=Decimal("1.0")),
        QualityLine(item_code="REC-01", score_obtained=Decimal("0.9"), max_score=Decimal("1.0")),
        QualityLine(item_code="MED-01", score_obtained=Decimal("0.7"), max_score=Decimal("1.0")),
        QualityLine(item_code="EQP-01", score_obtained=Decimal("1.0"), max_score=Decimal("1.0")),
        QualityLine(item_code="PROT-01", score_obtained=Decimal("0.6"), max_score=Decimal("1.0")),
    ]
