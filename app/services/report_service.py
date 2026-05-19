from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.health_facility import HealthFacility
from app.models.payment import Payment
from app.models.quarterly_declaration import QuarterlyDeclaration
from app.schemas.declaration import DeclarationRead
from app.schemas.health_facility import FacilityRead
from app.schemas.payment import PaymentRead


async def get_facility_report(
    session: AsyncSession, facility_id: int
) -> list[dict]:
    fac_result = await session.execute(
        select(HealthFacility).where(HealthFacility.id == facility_id)
    )
    facility = fac_result.scalar_one_or_none()
    if facility is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Facility not found")

    decl_result = await session.execute(
        select(QuarterlyDeclaration)
        .where(QuarterlyDeclaration.facility_id == facility_id)
        .order_by(QuarterlyDeclaration.year.desc(), QuarterlyDeclaration.quarter.desc())
    )
    declarations = decl_result.scalars().all()

    rows = []
    for decl in declarations:
        pay_result = await session.execute(
            select(Payment).where(Payment.declaration_id == decl.id)
        )
        payment = pay_result.scalar_one_or_none()
        rows.append({
            "facility": FacilityRead.model_validate(facility).model_dump(),
            "declaration": DeclarationRead.model_validate(decl).model_dump(),
            "payment": PaymentRead.model_validate(payment).model_dump() if payment else None,
        })
    return rows


async def get_national_report(session: AsyncSession, year: int, quarter: int) -> dict:
    result = await session.execute(
        select(QuarterlyDeclaration, Payment, HealthFacility)
        .join(Payment, Payment.declaration_id == QuarterlyDeclaration.id, isouter=True)
        .join(HealthFacility, QuarterlyDeclaration.facility_id == HealthFacility.id)
        .where(
            QuarterlyDeclaration.year == year,
            QuarterlyDeclaration.quarter == quarter,
        )
    )
    rows = result.all()

    by_region: dict[str, dict] = {}
    for decl, payment, facility in rows:
        region = facility.region
        if region not in by_region:
            by_region[region] = {"facilities": 0, "total_net_amount": Decimal("0"), "declarations": []}
        by_region[region]["facilities"] += 1
        if payment:
            by_region[region]["total_net_amount"] += payment.net_amount
        by_region[region]["declarations"].append({
            "facility_name": facility.name,
            "status": decl.status,
            "net_amount": str(payment.net_amount) if payment else None,
        })

    return {
        "year": year,
        "quarter": quarter,
        "regions": {k: {**v, "total_net_amount": str(v["total_net_amount"])} for k, v in by_region.items()},
    }
