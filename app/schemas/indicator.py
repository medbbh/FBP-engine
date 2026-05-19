from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class IndicatorCreate(BaseModel):
    code: str
    name: str
    unit_tariff: Decimal
    service_category: str


class IndicatorRead(IndicatorCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
