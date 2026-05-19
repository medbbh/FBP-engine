import decimal
from decimal import Decimal

from app.engine.models import QualityLine, QuantityLine
from app.schemas.payment import PaymentBreakdown
from app.schemas.rule_set import RuleSet

DECIMAL_CTX = decimal.Context(prec=10, rounding=decimal.ROUND_HALF_UP)


def _d(value: Decimal) -> Decimal:
    return DECIMAL_CTX.create_decimal(value)


def compute_quantity_subtotal(lines: list[QuantityLine]) -> Decimal:
    """Sum of (verified_quantity × unit_tariff) across all indicators."""
    return _d(sum((_d(line.verified_quantity) * _d(line.unit_tariff) for line in lines), Decimal("0")))


def compute_quality_score(lines: list[QualityLine]) -> Decimal:
    """Returns weighted score in [0.0, 1.0]: aggregate score_obtained / max_score."""
    total_max = sum((_d(line.max_score) for line in lines), Decimal("0"))
    if total_max == Decimal("0"):
        return Decimal("0")
    total_obtained = sum((_d(line.score_obtained) for line in lines), Decimal("0"))
    return _d(total_obtained / total_max)


def compute_payment(
    quantity_subtotal: Decimal,
    quality_score: Decimal,
    equity_coefficient: Decimal,
    rules: RuleSet,
) -> PaymentBreakdown:
    """
    Standard PBF carrot-and-stick formula:
        payment = quantity_subtotal × quality_score × equity_coefficient

    If quality_score < quality_threshold, payment = 0.
    Applies bonus_pct when mode is bonus_threshold and score exceeds bonus_above_quality.
    Applies payment_floor as a minimum guarantee.
    """
    qty = _d(quantity_subtotal)
    qs = _d(quality_score)
    eq = _d(equity_coefficient)

    if qs < _d(rules.quality_threshold):
        return PaymentBreakdown(
            quantity_subtotal=qty,
            quality_score_pct=qs,
            equity_multiplier=eq,
            gross_amount=Decimal("0"),
            abatement_pct=Decimal("0"),
            abatement_reason="Quality score below threshold — payment zeroed",
            net_amount=Decimal("0"),
            fraud_flag=False,
        )

    gross = _d(qty * qs * eq)

    if (
        rules.quality_multiplier_mode == "bonus_threshold"
        and rules.bonus_above_quality is not None
        and rules.bonus_pct is not None
        and qs >= _d(rules.bonus_above_quality)
    ):
        bonus_multiplier = _d(Decimal("1") + rules.bonus_pct)
        gross = _d(gross * bonus_multiplier)

    gross = max(gross, _d(rules.payment_floor))

    return PaymentBreakdown(
        quantity_subtotal=qty,
        quality_score_pct=qs,
        equity_multiplier=eq,
        gross_amount=gross,
        abatement_pct=Decimal("0"),
        abatement_reason=None,
        net_amount=gross,
        fraud_flag=False,
    )


def apply_abatement(
    payment: Decimal,
    discrepancy_rate: Decimal,
    rules: RuleSet,
) -> tuple[Decimal, Decimal, bool, str | None]:
    """
    Apply proportional abatement based on discrepancy between declared and verified quantities.

    Returns (net_payment, abatement_pct, fraud_flag, reason).

    Bracket rules (configurable via RuleSet):
        discrepancy ≤ lowest bracket   → no abatement
        within bracket                  → abatement = discrepancy × abatement_factor × 1.5
        discrepancy > 10%              → 100% abatement + fraud flag
    """
    disc = _d(discrepancy_rate)
    pay = _d(payment)

    # Hard fraud threshold: above the last bracket's max_discrepancy
    brackets = sorted(rules.abatement_brackets, key=lambda b: b.max_discrepancy)
    if not brackets:
        return pay, Decimal("0"), False, None

    last_max = _d(brackets[-1].max_discrepancy)
    if disc > last_max and disc > Decimal("0.10"):
        reason = f"Discrepancy {disc:.2%} exceeds 10% — full abatement (fraud investigation)"
        return Decimal("0"), Decimal("1"), True, reason

    # Walk brackets to find applicable abatement
    for bracket in brackets:
        if disc <= _d(bracket.max_discrepancy):
            factor = _d(bracket.abatement_factor)
            if factor == Decimal("0"):
                return pay, Decimal("0"), False, None
            abatement_pct = _d(disc * factor * Decimal("1.5"))
            abatement_pct = min(abatement_pct, Decimal("1"))
            net = _d(pay * (Decimal("1") - abatement_pct))
            reason = f"Discrepancy {disc:.2%} — abatement applied at {abatement_pct:.2%}"
            return net, abatement_pct, False, reason

    # Above all brackets but ≤ 10% — apply last bracket's factor
    factor = _d(brackets[-1].abatement_factor)
    abatement_pct = _d(disc * factor * Decimal("1.5"))
    abatement_pct = min(abatement_pct, Decimal("1"))
    net = _d(pay * (Decimal("1") - abatement_pct))
    reason = f"Discrepancy {disc:.2%} — abatement applied at {abatement_pct:.2%}"
    return net, abatement_pct, False, reason
