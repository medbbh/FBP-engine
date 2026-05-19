"""
Golden integration test: full quarterly cycle computation for CSB Rosso.

This test verifies the exact MRU amount produced by the engine without a database.
The expected values were hand-calculated against the PBF formula:
    payment = quantity_subtotal × quality_score × equity_coefficient

CSB Rosso, Trarza, rural, equity_coefficient = 1.3
Quarter: Q1 2024
"""
from decimal import Decimal

import pytest

from app.engine.calculations import apply_abatement, compute_payment, compute_quality_score, compute_quantity_subtotal
from app.engine.models import QualityLine, QuantityLine
from app.schemas.rule_set import AbatementBracket, RuleSet

ROSSO_EQUITY = Decimal("1.3")

MAURITANIAN_RULES = RuleSet(
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

QUANTITY_LINES = [
    QuantityLine("CPN1", verified_quantity=Decimal("95"), unit_tariff=Decimal("300")),
    QuantityLine("CPN4", verified_quantity=Decimal("42"), unit_tariff=Decimal("500")),
    QuantityLine("ACC_ASSIST", verified_quantity=Decimal("38"), unit_tariff=Decimal("1200")),
    QuantityLine("VAC_PENTA3", verified_quantity=Decimal("110"), unit_tariff=Decimal("300")),
    QuantityLine("CONSULT_CUR", verified_quantity=Decimal("430"), unit_tariff=Decimal("80")),
]

# 60 quality items: 48 scored full (1.0), 12 scored partial (0.5)
QUALITY_LINES = (
    [QualityLine(f"FULL-{i}", Decimal("1.0"), Decimal("1.0")) for i in range(48)]
    + [QualityLine(f"PART-{i}", Decimal("0.5"), Decimal("1.0")) for i in range(12)]
)

# No discrepancy (perfect verification match)
MAX_DISCREPANCY = Decimal("0.03")


def test_golden_quarterly_cycle_csb_rosso_exact_net_amount():
    """
    Full quarterly cycle for CSB Rosso, Trarza, Q1/2024.

    quantity_subtotal:
        95×300 + 42×500 + 38×1200 + 110×300 + 430×80
        = 28500 + 21000 + 45600 + 33000 + 34400 = 162500 MRU

    quality_score:
        (48×1.0 + 12×0.5) / 60 = (48 + 6) / 60 = 54/60 = 0.9

    gross_amount:
        162500 × 0.9 × 1.3 = 162500 × 1.17 = 190125 MRU

    discrepancy = 0.03 → below 5% bracket → no abatement
    net_amount = 190125 MRU
    """
    qty_subtotal = compute_quantity_subtotal(QUANTITY_LINES)
    assert qty_subtotal == Decimal("162500"), f"Expected 162500, got {qty_subtotal}"

    quality_score = compute_quality_score(QUALITY_LINES)
    assert quality_score == Decimal("0.9"), f"Expected 0.9, got {quality_score}"

    breakdown = compute_payment(qty_subtotal, quality_score, ROSSO_EQUITY, MAURITANIAN_RULES)
    assert breakdown.gross_amount == Decimal("190125"), f"Expected 190125, got {breakdown.gross_amount}"

    net, abatement_pct, fraud_flag, _ = apply_abatement(
        breakdown.gross_amount, MAX_DISCREPANCY, MAURITANIAN_RULES
    )
    assert fraud_flag is False
    assert abatement_pct == Decimal("0")
    assert net == Decimal("190125"), f"Expected net 190125 MRU, got {net}"


def test_golden_cycle_with_discrepancy_reduces_payment():
    """
    Same CSB Rosso scenario but with 8% discrepancy.
    abatement = 0.08 × 1 × 1.5 = 0.12 → net = 190125 × 0.88 = 167310 MRU
    """
    qty_subtotal = compute_quantity_subtotal(QUANTITY_LINES)
    quality_score = compute_quality_score(QUALITY_LINES)
    breakdown = compute_payment(qty_subtotal, quality_score, ROSSO_EQUITY, MAURITANIAN_RULES)

    net, pct, fraud, _ = apply_abatement(breakdown.gross_amount, Decimal("0.08"), MAURITANIAN_RULES)
    assert fraud is False
    assert pct == Decimal("0.12")
    assert net == Decimal("167310"), f"Expected 167310 MRU after abatement, got {net}"


def test_golden_cycle_quality_below_threshold_zeroes_payment():
    """CSB Rosso with low quality (45%) → payment = 0."""
    low_quality_lines = [QualityLine(f"ITEM-{i}", Decimal("0.45"), Decimal("1.0")) for i in range(60)]
    qty_subtotal = compute_quantity_subtotal(QUANTITY_LINES)
    quality_score = compute_quality_score(low_quality_lines)

    assert quality_score < MAURITANIAN_RULES.quality_threshold

    breakdown = compute_payment(qty_subtotal, quality_score, ROSSO_EQUITY, MAURITANIAN_RULES)
    assert breakdown.net_amount == Decimal("0")
