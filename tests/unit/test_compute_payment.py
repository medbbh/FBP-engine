from decimal import Decimal

import pytest

from app.engine.calculations import compute_payment
from app.schemas.rule_set import AbatementBracket, RuleSet


@pytest.fixture
def rules() -> RuleSet:
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
    )


def test_quality_deflator_at_80_pct_reduces_payment_proportionally(rules):
    result = compute_payment(
        quantity_subtotal=Decimal("100000"),
        quality_score=Decimal("0.80"),
        equity_coefficient=Decimal("1.0"),
        rules=rules,
    )
    assert result.gross_amount == Decimal("80000")
    assert result.net_amount == Decimal("80000")


def test_quality_below_threshold_returns_zero_payment(rules):
    result = compute_payment(
        quantity_subtotal=Decimal("100000"),
        quality_score=Decimal("0.49"),
        equity_coefficient=Decimal("1.0"),
        rules=rules,
    )
    assert result.gross_amount == Decimal("0")
    assert result.net_amount == Decimal("0")
    assert "threshold" in result.abatement_reason.lower()


def test_quality_exactly_at_threshold_is_not_zeroed(rules):
    result = compute_payment(
        quantity_subtotal=Decimal("100000"),
        quality_score=Decimal("0.50"),
        equity_coefficient=Decimal("1.0"),
        rules=rules,
    )
    assert result.gross_amount == Decimal("50000")


def test_perfect_quality_score_with_equity_multiplier(rules):
    result = compute_payment(
        quantity_subtotal=Decimal("78000"),
        quality_score=Decimal("1.0"),
        equity_coefficient=Decimal("1.3"),
        rules=rules,
    )
    # 78000 × 1.0 × 1.3 = 101400
    assert result.gross_amount == Decimal("101400")


def test_payment_floor_applied_when_computed_value_is_lower():
    rules_with_floor = RuleSet(
        quality_threshold=Decimal("0.50"),
        quality_multiplier_mode="deflator",
        abatement_brackets=[
            AbatementBracket(max_discrepancy=Decimal("0.05"), abatement_factor=Decimal("0")),
        ],
        equity_min=Decimal("1.0"),
        equity_max=Decimal("1.5"),
        payment_floor=Decimal("10000"),
    )
    result = compute_payment(
        quantity_subtotal=Decimal("5000"),
        quality_score=Decimal("0.60"),
        equity_coefficient=Decimal("1.0"),
        rules=rules_with_floor,
    )
    # 5000 × 0.6 = 3000, but floor = 10000
    assert result.gross_amount == Decimal("10000")


def test_bonus_threshold_mode_applies_bonus_above_quality():
    rules_bonus = RuleSet(
        quality_threshold=Decimal("0.50"),
        quality_multiplier_mode="bonus_threshold",
        abatement_brackets=[
            AbatementBracket(max_discrepancy=Decimal("0.05"), abatement_factor=Decimal("0")),
        ],
        equity_min=Decimal("1.0"),
        equity_max=Decimal("1.5"),
        payment_floor=Decimal("0"),
        bonus_above_quality=Decimal("0.90"),
        bonus_pct=Decimal("0.10"),
    )
    result = compute_payment(
        quantity_subtotal=Decimal("100000"),
        quality_score=Decimal("0.95"),
        equity_coefficient=Decimal("1.0"),
        rules=rules_bonus,
    )
    # 100000 × 0.95 × 1.0 = 95000, then × 1.10 = 104500
    assert result.gross_amount == Decimal("104500")


def test_all_payment_breakdown_components_are_populated(rules):
    result = compute_payment(
        quantity_subtotal=Decimal("50000"),
        quality_score=Decimal("0.75"),
        equity_coefficient=Decimal("1.2"),
        rules=rules,
    )
    assert result.quantity_subtotal == Decimal("50000")
    assert result.quality_score_pct == Decimal("0.75")
    assert result.equity_multiplier == Decimal("1.2")
    assert result.gross_amount is not None
    assert result.net_amount is not None
