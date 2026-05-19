from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class QualitySubmit(BaseModel):
    item_id: int
    score_obtained: Decimal = Field(..., ge=Decimal("0"))
    max_score: Decimal = Field(..., gt=Decimal("0"))
    evaluator_notes: str | None = None


class QualityRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    declaration_id: int
    item_id: int
    score_obtained: Decimal
    max_score: Decimal
    evaluator_notes: str | None = None
