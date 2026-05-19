from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import require_role
from app.core.database import get_db
from app.models.user import User
from app.schemas.health_facility import FacilityCreate, FacilityList, FacilityRead
from app.services import facility_service

router = APIRouter(prefix="/facilities", tags=["facilities"])


@router.post("/", response_model=FacilityRead, status_code=status.HTTP_201_CREATED)
async def create_facility(
    data: FacilityCreate,
    session: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(["admin"])),
) -> FacilityRead:
    return await facility_service.create_facility(session, data)


@router.get("/", response_model=FacilityList)
async def list_facilities(
    skip: int = 0,
    limit: int = 100,
    session: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(["admin", "verifier", "auditor", "facility_user"])),
) -> FacilityList:
    return await facility_service.list_facilities(session, skip=skip, limit=limit)
