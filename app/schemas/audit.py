import enum
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class RiskScore(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class AnomalyFlag(BaseModel):
    rule: str
    indicator: str | None = None
    details: str


class AnomalyResult(BaseModel):
    risk_score: RiskScore
    flags: list[AnomalyFlag]
    total_flags: int


class AuditCreate(BaseModel):
    audit_type: str = Field(..., pattern="^(community|counter_verification|risk_based)$")
    patients_sampled: int = Field(..., ge=0)
    patients_confirmed: int = Field(..., ge=0)
    anomaly_flag: bool = False
    notes: str | None = None


class AuditRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    declaration_id: int
    audit_type: str
    patients_sampled: int
    patients_confirmed: int
    anomaly_flag: bool
    notes: str | None = None
    conducted_at: datetime
