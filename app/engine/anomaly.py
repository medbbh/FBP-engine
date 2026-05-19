from decimal import Decimal

import numpy as np

from app.schemas.audit import AnomalyFlag, AnomalyResult, RiskScore

_Z_THRESHOLD = 2.5
_JUMP_THRESHOLD = Decimal("0.50")
_QUALITY_DROP_THRESHOLD = Decimal("0.20")


def detect_anomalies(
    current_quantities: dict[str, Decimal],
    historical_quantities: list[dict[str, Decimal]],
    peer_quantities: list[dict[str, Decimal]],
    current_quality_score: Decimal,
    historical_quality_scores: list[Decimal],
) -> AnomalyResult:
    """
    Statistical anomaly detection for a single quarterly declaration.

    Returns AnomalyResult with RiskScore (low/medium/high) based on:
    - Own-history z-score per indicator (|z| > 2.5)
    - Peer z-score per indicator (|z| > 2.5)
    - Sudden quantity jump > 50% vs previous quarter
    - Quality score drop > 20 percentage points vs previous quarter
    """
    flags: list[AnomalyFlag] = []

    flags.extend(_check_own_history_zscore(current_quantities, historical_quantities))
    flags.extend(_check_peer_zscore(current_quantities, peer_quantities))
    flags.extend(_check_sudden_jump(current_quantities, historical_quantities))
    flags.extend(_check_quality_drop(current_quality_score, historical_quality_scores))

    total = len(flags)
    if total == 0:
        risk = RiskScore.LOW
    elif total <= 2:
        risk = RiskScore.MEDIUM
    else:
        risk = RiskScore.HIGH

    return AnomalyResult(risk_score=risk, flags=flags, total_flags=total)


def _check_own_history_zscore(
    current: dict[str, Decimal],
    history: list[dict[str, Decimal]],
) -> list[AnomalyFlag]:
    if len(history) < 2:
        return []

    flags = []
    for code, value in current.items():
        past_values = [float(q[code]) for q in history if code in q]
        if len(past_values) < 2:
            continue
        arr = np.array(past_values, dtype=float)
        std = arr.std()
        if std == 0:
            continue
        z = abs((float(value) - arr.mean()) / std)
        if z > _Z_THRESHOLD:
            flags.append(AnomalyFlag(
                rule="own_history_zscore",
                indicator=code,
                details=f"z={z:.2f} (threshold {_Z_THRESHOLD}) vs own 4-quarter history",
            ))
    return flags


def _check_peer_zscore(
    current: dict[str, Decimal],
    peers: list[dict[str, Decimal]],
) -> list[AnomalyFlag]:
    if len(peers) < 2:
        return []

    flags = []
    for code, value in current.items():
        peer_values = [float(p[code]) for p in peers if code in p]
        if len(peer_values) < 2:
            continue
        arr = np.array(peer_values, dtype=float)
        std = arr.std()
        if std == 0:
            continue
        z = abs((float(value) - arr.mean()) / std)
        if z > _Z_THRESHOLD:
            flags.append(AnomalyFlag(
                rule="peer_zscore",
                indicator=code,
                details=f"z={z:.2f} (threshold {_Z_THRESHOLD}) vs peer facilities",
            ))
    return flags


def _check_sudden_jump(
    current: dict[str, Decimal],
    history: list[dict[str, Decimal]],
) -> list[AnomalyFlag]:
    if not history:
        return []

    previous = history[-1]
    flags = []
    for code, value in current.items():
        if code not in previous:
            continue
        prev_value = previous[code]
        if prev_value == Decimal("0"):
            continue
        jump = (value - prev_value) / prev_value
        if jump > _JUMP_THRESHOLD:
            flags.append(AnomalyFlag(
                rule="sudden_jump",
                indicator=code,
                details=f"Increase of {jump:.1%} vs previous quarter (threshold {_JUMP_THRESHOLD:.0%})",
            ))
    return flags


def _check_quality_drop(
    current_score: Decimal,
    history_scores: list[Decimal],
) -> list[AnomalyFlag]:
    if not history_scores:
        return []

    previous_score = history_scores[-1]
    drop = previous_score - current_score
    if drop > _QUALITY_DROP_THRESHOLD:
        return [AnomalyFlag(
            rule="quality_drop",
            indicator=None,
            details=f"Quality dropped {drop:.1%} (from {previous_score:.1%} to {current_score:.1%}), threshold {_QUALITY_DROP_THRESHOLD:.0%}",
        )]
    return []
