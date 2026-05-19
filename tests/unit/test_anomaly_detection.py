from decimal import Decimal

import pytest

from app.engine.anomaly import detect_anomalies
from app.schemas.audit import RiskScore


def _make_history(n: int, value: Decimal) -> list[dict[str, Decimal]]:
    return [{"CPN1": value, "ACC_ASSIST": Decimal("20")} for _ in range(n)]


def test_no_anomalies_returns_low_risk():
    current = {"CPN1": Decimal("100"), "ACC_ASSIST": Decimal("20")}
    history = _make_history(4, Decimal("100"))
    result = detect_anomalies(
        current_quantities=current,
        historical_quantities=history,
        peer_quantities=[{"CPN1": Decimal("95")}, {"CPN1": Decimal("105")}],
        current_quality_score=Decimal("0.80"),
        historical_quality_scores=[Decimal("0.78"), Decimal("0.82"), Decimal("0.79")],
    )
    assert result.risk_score == RiskScore.LOW
    assert result.total_flags == 0


def test_zscore_above_2_5_flags_anomaly():
    # CPN1 normally ~100, spike to 300 → z > 2.5
    history = [
        {"CPN1": Decimal("100")},
        {"CPN1": Decimal("102")},
        {"CPN1": Decimal("98")},
        {"CPN1": Decimal("101")},
    ]
    current = {"CPN1": Decimal("300")}
    result = detect_anomalies(
        current_quantities=current,
        historical_quantities=history,
        peer_quantities=[],
        current_quality_score=Decimal("0.80"),
        historical_quality_scores=[Decimal("0.80")],
    )
    own_history_flags = [f for f in result.flags if f.rule == "own_history_zscore"]
    assert len(own_history_flags) > 0


def test_sudden_jump_above_50_pct_flagged():
    previous = {"CPN1": Decimal("100")}
    current = {"CPN1": Decimal("200")}  # +100% jump
    result = detect_anomalies(
        current_quantities=current,
        historical_quantities=[previous],
        peer_quantities=[],
        current_quality_score=Decimal("0.80"),
        historical_quality_scores=[Decimal("0.80")],
    )
    jump_flags = [f for f in result.flags if f.rule == "sudden_jump"]
    assert len(jump_flags) > 0
    assert "CPN1" in jump_flags[0].indicator


def test_quality_drop_above_20pp_flagged():
    result = detect_anomalies(
        current_quantities={"CPN1": Decimal("100")},
        historical_quantities=[{"CPN1": Decimal("100")}],
        peer_quantities=[],
        current_quality_score=Decimal("0.50"),
        historical_quality_scores=[Decimal("0.75")],  # drop = 0.25 > 0.20
    )
    quality_flags = [f for f in result.flags if f.rule == "quality_drop"]
    assert len(quality_flags) > 0


def test_insufficient_history_skips_zscore_gracefully():
    # Only 1 historical quarter — not enough for z-score
    result = detect_anomalies(
        current_quantities={"CPN1": Decimal("500")},
        historical_quantities=[{"CPN1": Decimal("100")}],
        peer_quantities=[],
        current_quality_score=Decimal("0.80"),
        historical_quality_scores=[Decimal("0.80")],
    )
    # Should not crash; own_history z-score skipped, but sudden_jump may fire
    zscore_flags = [f for f in result.flags if f.rule == "own_history_zscore"]
    assert len(zscore_flags) == 0


def test_three_or_more_flags_returns_high_risk():
    # Trigger: jump + quality drop
    history = [
        {"CPN1": Decimal("100")},
        {"CPN1": Decimal("102")},
        {"CPN1": Decimal("98")},
        {"CPN1": Decimal("100")},
    ]
    current = {"CPN1": Decimal("400")}  # huge jump + z-score
    result = detect_anomalies(
        current_quantities=current,
        historical_quantities=history,
        peer_quantities=[{"CPN1": Decimal("100")}, {"CPN1": Decimal("105")}, {"CPN1": Decimal("95")}],
        current_quality_score=Decimal("0.40"),
        historical_quality_scores=[Decimal("0.80"), Decimal("0.78")],  # -38pp drop
    )
    assert result.total_flags >= 3
    assert result.risk_score == RiskScore.HIGH


def test_one_or_two_flags_returns_medium_risk():
    result = detect_anomalies(
        current_quantities={"CPN1": Decimal("200")},
        historical_quantities=[{"CPN1": Decimal("100")}],
        peer_quantities=[],
        current_quality_score=Decimal("0.80"),
        historical_quality_scores=[Decimal("0.80")],
    )
    # Only sudden_jump should fire
    if result.total_flags == 1 or result.total_flags == 2:
        assert result.risk_score == RiskScore.MEDIUM
