from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import require_role
from app.core.database import get_db
from app.models.user import User
from app.services import report_service

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/facility/{facility_id}")
async def facility_report(
    facility_id: int,
    session: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(["admin", "auditor", "verifier", "facility_user"])),
) -> list[dict]:
    return await report_service.get_facility_report(session, facility_id)


@router.get("/national/{year}/{quarter}")
async def national_report(
    year: int,
    quarter: int,
    session: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(["admin"])),
) -> dict:
    return await report_service.get_national_report(session, year, quarter)
