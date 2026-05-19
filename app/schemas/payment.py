from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class PaymentBreakdown(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    quantity_subtotal: Decimal
    quality_score_pct: Decimal
    equity_multiplier: Decimal
    gross_amount: Decimal
    abatement_pct: Decimal
    abatement_reason: str | None
    net_amount: Decimal
    fraud_flag: bool


class PaymentRead(PaymentBreakdown):
    id: int
    declaration_id: int
    paid_at: datetime | None = None
    computed_at: datetime
