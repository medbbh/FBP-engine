from decimal import Decimal

import pytest

from app.engine.calculations import compute_quality_score
from app.engine.models import QualityLine


def test_empty_checklist_returns_zero_quality_score():
    assert compute_quality_score([]) == Decimal("0")


def test_perfect_quality_score_when_all_items_at_max():
    lines = [QualityLine(f"ITEM-{i}", Decimal("1"), Decimal("1")) for i in range(10)]
    assert compute_quality_score(lines) == Decimal("1")


def test_zero_score_on_all_items_returns_zero():
    lines = [QualityLine(f"ITEM-{i}", Decimal("0"), Decimal("1")) for i in range(5)]
    assert compute_quality_score(lines) == Decimal("0")


def test_quality_score_at_80_pct_with_uniform_items():
    lines = [QualityLine(f"ITEM-{i}", Decimal("0.8"), Decimal("1")) for i in range(5)]
    score = compute_quality_score(lines)
    assert score == Decimal("0.8")


def test_weighted_score_across_mixed_service_areas():
    lines = [
        QualityLine("HYG-01", Decimal("0.8"), Decimal("1.0")),
        QualityLine("REC-01", Decimal("0.9"), Decimal("1.0")),
        QualityLine("MED-01", Decimal("0.7"), Decimal("1.0")),
        QualityLine("EQP-01", Decimal("1.0"), Decimal("1.0")),
        QualityLine("PROT-01", Decimal("0.6"), Decimal("1.0")),
    ]
    # (0.8+0.9+0.7+1.0+0.6) / 5 = 4.0 / 5 = 0.8
    assert compute_quality_score(lines) == Decimal("0.8")


def test_score_does_not_exceed_one():
    lines = [QualityLine("ITEM-01", Decimal("1.0"), Decimal("1.0"))]
    assert compute_quality_score(lines) <= Decimal("1")


def test_zero_max_score_returns_zero_without_error():
    lines = [QualityLine("ITEM-01", Decimal("0"), Decimal("0"))]
    assert compute_quality_score(lines) == Decimal("0")
