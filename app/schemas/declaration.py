import enum
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class DeclarationStatus(str, enum.Enum):
    DRAFT = "draft"
    DECLARED = "declared"
    VERIFIED = "verified"
    PAID = "paid"
    REJECTED = "rejected"


class DeclarationCreate(BaseModel):
    facility_id: int
    year: int = Field(..., ge=2000, le=2100)
    quarter: int = Field(..., ge=1, le=4)


class DeclarationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    facility_id: int
    year: int
    quarter: int
    status: str
    submitted_at: datetime | None = None
    verified_at: datetime | None = None
    created_at: datetime
