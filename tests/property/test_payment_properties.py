"""
Property-based tests using hypothesis.
These verify invariants that must hold for ALL valid inputs.
"""
from decimal import Decimal

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from app.engine.calculations import apply_abatement, compute_payment, compute_quality_score, compute_quantity_subtotal
from app.engine.models import QualityLine, QuantityLine
from app.schemas.rule_set import AbatementBracket, RuleSet

_DEFAULT_RULES = RuleSet(
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

_decimal_qty = st.decimals(min_value=Decimal("0"), max_value=Decimal("10000000"), places=2, allow_nan=False, allow_infinity=False)
_decimal_quality = st.decimals(min_value=Decimal("0"), max_value=Decimal("1"), places=4, allow_nan=False, allow_infinity=False)
_decimal_equity = st.decimals(min_value=Decimal("1.0"), max_value=Decimal("1.5"), places=2, allow_nan=False, allow_infinity=False)
_decimal_discrepancy = st.decimals(min_value=Decimal("0"), max_value=Decimal("0.5"), places=4, allow_nan=False, allow_infinity=False)


@given(
    quantity_subtotal=_decimal_qty,
    quality_score=_decimal_quality,
    equity_coefficient=_decimal_equity,
)
@settings(max_examples=200)
def test_payment_always_in_valid_range(quantity_subtotal, quality_score, equity_coefficient):
    result = compute_payment(quantity_subtotal, quality_score, equity_coefficient, _DEFAULT_RULES)
    assert result.net_amount >= Decimal("0"), "Payment cannot be negative"
    upper_bound = quantity_subtotal * _DEFAULT_RULES.equity_max
    assert result.net_amount <= upper_bound + Decimal("1"), (
        f"Payment {result.net_amount} exceeds max possible {upper_bound}"
    )


@given(
    payment=_decimal_qty,
    discrepancy=_decimal_discrepancy,
)
@settings(max_examples=200)
def test_abatement_never_increases_payment(payment, discrepancy):
    net, _, _, _ = apply_abatement(payment, discrepancy, _DEFAULT_RULES)
    assert net <= payment, f"Abatement increased payment from {payment} to {net}"


@given(
    quantity_subtotal=_decimal_qty,
    equity_coefficient=_decimal_equity,
)
@settings(max_examples=100)
def test_quality_below_threshold_always_yields_zero_payment(quantity_subtotal, equity_coefficient):
    quality_score = Decimal("0.49")  # always below 0.50 threshold
    result = compute_payment(quantity_subtotal, quality_score, equity_coefficient, _DEFAULT_RULES)
    assert result.net_amount == Decimal("0"), (
        f"Expected zero payment for quality {quality_score} below threshold, got {result.net_amount}"
    )


@given(
    lines=st.lists(
        st.builds(
            QuantityLine,
            indicator_code=st.just("CODE"),
            verified_quantity=st.decimals(min_value=Decimal("0"), max_value=Decimal("10000"), places=2, allow_nan=False, allow_infinity=False),
            unit_tariff=st.decimals(min_value=Decimal("0"), max_value=Decimal("5000"), places=2, allow_nan=False, allow_infinity=False),
        ),
        min_size=0,
        max_size=30,
    )
)
@settings(max_examples=100)
def test_quantity_subtotal_is_always_non_negative(lines):
    result = compute_quantity_subtotal(lines)
    assert result >= Decimal("0")


@given(
    lines=st.lists(
        st.builds(
            QualityLine,
            item_code=st.just("ITEM"),
            score_obtained=st.decimals(min_value=Decimal("0"), max_value=Decimal("1"), places=2, allow_nan=False, allow_infinity=False),
            max_score=st.decimals(min_value=Decimal("0.01"), max_value=Decimal("1"), places=2, allow_nan=False, allow_infinity=False),
        ),
        min_size=1,
        max_size=100,
    )
)
@settings(max_examples=100)
def test_quality_score_always_in_0_to_1_range(lines):
    result = compute_quality_score(lines)
    assert Decimal("0") <= result <= Decimal("1"), f"Quality score {result} out of [0, 1]"
