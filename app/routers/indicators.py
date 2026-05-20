from decimal import Decimal

from fastapi import APIRouter, Depends
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import require_role
from app.core.database import get_db
from app.models.quality_checklist_item import QualityChecklistItem
from app.models.quantity_indicator import QuantityIndicator
from app.models.user import User
from app.schemas.indicator import IndicatorRead


class ChecklistRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    description: str
    service_area: str
    max_points: Decimal
    applies_to_facility_type: str | None = None


router = APIRouter(prefix="/indicators", tags=["indicators"])


@router.get("/", response_model=list[IndicatorRead])
async def list_indicators(
    skip: int = 0,
    limit: int = 100,
    session: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(["admin", "facility_user", "verifier", "auditor"])),
) -> list[IndicatorRead]:
    result = await session.execute(select(QuantityIndicator).offset(skip).limit(limit))
    return [IndicatorRead.model_validate(r) for r in result.scalars().all()]


@router.get("/checklist", response_model=list[ChecklistRead])
async def list_checklist(
    skip: int = 0,
    limit: int = 100,
    session: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(["admin", "facility_user", "verifier", "auditor"])),
) -> list[ChecklistRead]:
    result = await session.execute(select(QualityChecklistItem).offset(skip).limit(limit))
    return [ChecklistRead.model_validate(r) for r in result.scalars().all()]
