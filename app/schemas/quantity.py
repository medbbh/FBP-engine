from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class QuantitySubmit(BaseModel):
    indicator_id: int
    declared_quantity: Decimal = Field(..., ge=Decimal("0"))
    verified_quantity: Decimal = Field(..., ge=Decimal("0"))


class QuantityRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    declaration_id: int
    indicator_id: int
    declared_quantity: Decimal
    verified_quantity: Decimal
    discrepancy_rate: Decimal
