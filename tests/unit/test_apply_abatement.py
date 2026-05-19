from decimal import Decimal

import pytest

from app.engine.calculations import apply_abatement
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


def test_discrepancy_below_5_pct_has_no_abatement(rules):
    net, pct, fraud, reason = apply_abatement(Decimal("100000"), Decimal("0.04"), rules)
    assert net == Decimal("100000")
    assert pct == Decimal("0")
    assert fraud is False


def test_discrepancy_at_exactly_5_pct_has_no_abatement(rules):
    net, pct, fraud, reason = apply_abatement(Decimal("100000"), Decimal("0.05"), rules)
    assert net == Decimal("100000")
    assert pct == Decimal("0")
    assert fraud is False


def test_discrepancy_between_5_and_10_pct_applies_proportional_abatement(rules):
    net, pct, fraud, reason = apply_abatement(Decimal("100000"), Decimal("0.08"), rules)
    # 0.08 × 1 × 1.5 = 0.12 abatement → net = 88000
    assert pct == Decimal("0.12")
    assert net == Decimal("88000")
    assert fraud is False


def test_discrepancy_above_10_pct_triggers_full_abatement_and_fraud_flag(rules):
    net, pct, fraud, reason = apply_abatement(Decimal("100000"), Decimal("0.15"), rules)
    assert net == Decimal("0")
    assert pct == Decimal("1")
    assert fraud is True
    assert "fraud" in reason.lower()


def test_zero_discrepancy_returns_full_payment(rules):
    net, pct, fraud, _ = apply_abatement(Decimal("50000"), Decimal("0"), rules)
    assert net == Decimal("50000")
    assert fraud is False


def test_abatement_never_increases_payment(rules):
    payment = Decimal("75000")
    for disc in [Decimal("0"), Decimal("0.03"), Decimal("0.07"), Decimal("0.12")]:
        net, _, _, _ = apply_abatement(payment, disc, rules)
        assert net <= payment


def test_empty_brackets_returns_original_payment():
    rules_no_brackets = RuleSet(
        quality_threshold=Decimal("0.50"),
        quality_multiplier_mode="deflator",
        abatement_brackets=[],
        equity_min=Decimal("1.0"),
        equity_max=Decimal("1.5"),
        payment_floor=Decimal("0"),
    )
    net, pct, fraud, _ = apply_abatement(Decimal("100000"), Decimal("0.15"), rules_no_brackets)
    assert net == Decimal("100000")
    assert fraud is False
