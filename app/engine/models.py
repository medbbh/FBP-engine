from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class QuantityLine:
    indicator_code: str
    verified_quantity: Decimal
    unit_tariff: Decimal


@dataclass(frozen=True)
class QualityLine:
    item_code: str
    score_obtained: Decimal
    max_score: Decimal
