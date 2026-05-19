from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class FacilityCreate(BaseModel):
    name: str
    type: str
    region: str
    district: str
    is_rural: bool = False
    equity_coefficient: Decimal = Field(default=Decimal("1.0"), ge=Decimal("1.0"), le=Decimal("1.5"))


class FacilityRead(FacilityCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int


class FacilityList(BaseModel):
    items: list[FacilityRead]
    total: int
