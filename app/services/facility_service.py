from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.health_facility import HealthFacility
from app.schemas.health_facility import FacilityCreate, FacilityList, FacilityRead


async def create_facility(session: AsyncSession, data: FacilityCreate) -> FacilityRead:
    facility = HealthFacility(**data.model_dump())
    session.add(facility)
    await session.flush()
    await session.refresh(facility)
    return FacilityRead.model_validate(facility)


async def list_facilities(
    session: AsyncSession, skip: int = 0, limit: int = 100
) -> FacilityList:
    count_result = await session.execute(select(func.count()).select_from(HealthFacility))
    total = count_result.scalar_one()

    result = await session.execute(select(HealthFacility).offset(skip).limit(limit))
    items = [FacilityRead.model_validate(f) for f in result.scalars().all()]
    return FacilityList(items=items, total=total)


async def get_facility(session: AsyncSession, facility_id: int) -> HealthFacility | None:
    result = await session.execute(
        select(HealthFacility).where(HealthFacility.id == facility_id)
    )
    return result.scalar_one_or_none()
