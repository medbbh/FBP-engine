from decimal import Decimal

import pytest

from app.engine.calculations import compute_quantity_subtotal
from app.engine.models import QuantityLine


def test_empty_list_returns_zero():
    assert compute_quantity_subtotal([]) == Decimal("0")


def test_single_indicator_multiplies_qty_by_tariff():
    lines = [QuantityLine("CPN1", Decimal("50"), Decimal("300"))]
    assert compute_quantity_subtotal(lines) == Decimal("15000")


def test_multiple_indicators_sum_correctly():
    lines = [
        QuantityLine("CPN1", Decimal("100"), Decimal("300")),
        QuantityLine("ACC_ASSIST", Decimal("20"), Decimal("1200")),
        QuantityLine("VAC_PENTA3", Decimal("80"), Decimal("300")),
    ]
    # 100×300 + 20×1200 + 80×300 = 30000 + 24000 + 24000 = 78000
    assert compute_quantity_subtotal(lines) == Decimal("78000")


def test_zero_quantity_does_not_contribute():
    lines = [
        QuantityLine("CPN1", Decimal("0"), Decimal("300")),
        QuantityLine("ACC_ASSIST", Decimal("10"), Decimal("1200")),
    ]
    assert compute_quantity_subtotal(lines) == Decimal("12000")


def test_decimal_tariff_precision_preserved():
    lines = [QuantityLine("CPN1", Decimal("3"), Decimal("333.33"))]
    result = compute_quantity_subtotal(lines)
    assert result == Decimal("999.99")
