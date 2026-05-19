from datetime import date
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, field_validator, model_validator


class AbatementBracket(BaseModel):
    max_discrepancy: Decimal
    abatement_factor: Decimal

    @field_validator("abatement_factor")
    @classmethod
    def factor_in_range(cls, v: Decimal) -> Decimal:
        if not (Decimal("0") <= v <= Decimal("1")):
            raise ValueError("abatement_factor must be between 0 and 1")
        return v


class RuleSet(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    quality_threshold: Decimal = Decimal("0.50")
    quality_multiplier_mode: Literal["deflator", "bonus_threshold"] = "deflator"
    abatement_brackets: list[AbatementBracket] = [
        AbatementBracket(max_discrepancy=Decimal("0.05"), abatement_factor=Decimal("0")),
        AbatementBracket(max_discrepancy=Decimal("0.10"), abatement_factor=Decimal("0")),
    ]
    equity_min: Decimal = Decimal("1.0")
    equity_max: Decimal = Decimal("1.5")
    payment_floor: Decimal = Decimal("0")
    bonus_above_quality: Decimal | None = None
    bonus_pct: Decimal | None = None

    @model_validator(mode="after")
    def brackets_sorted(self) -> "RuleSet":
        brackets = self.abatement_brackets
        for i in range(1, len(brackets)):
            if brackets[i].max_discrepancy <= brackets[i - 1].max_discrepancy:
                raise ValueError("abatement_brackets must be sorted by max_discrepancy ascending")
        return self


class RuleSetCreate(BaseModel):
    name: str
    description: str | None = None
    quality_threshold: Decimal = Decimal("0.50")
    quality_multiplier_mode: Literal["deflator", "bonus_threshold"] = "deflator"
    abatement_brackets: list[AbatementBracket]
    equity_min: Decimal = Decimal("1.0")
    equity_max: Decimal = Decimal("1.5")
    payment_floor: Decimal = Decimal("0")
    bonus_above_quality: Decimal | None = None
    bonus_pct: Decimal | None = None
    effective_from: date
    effective_to: date | None = None


class RuleSetRead(RuleSetCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
