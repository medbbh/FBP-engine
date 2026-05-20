from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import require_role
from app.core.database import get_db
from app.models.user import User
from app.models.verification_audit import VerificationAudit
from app.schemas.audit import AnomalyResult, AuditCreate, AuditRead
from app.schemas.declaration import DeclarationCreate, DeclarationRead
from app.schemas.payment import PaymentRead
from app.schemas.quality import QualityRead, QualitySubmit
from app.schemas.quantity import QuantityRead, QuantitySubmit
from app.services import anomaly_service, declaration_service, payment_service

router = APIRouter(prefix="/declarations", tags=["declarations"])


@router.get("/{declaration_id}", response_model=DeclarationRead)
async def get_declaration(
    declaration_id: int,
    session: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(["admin", "facility_user", "verifier", "auditor"])),
) -> DeclarationRead:
    declaration = await declaration_service.get_declaration(session, declaration_id)
    return DeclarationRead.model_validate(declaration)


@router.post("/", response_model=DeclarationRead, status_code=status.HTTP_201_CREATED)
async def create_declaration(
    data: DeclarationCreate,
    session: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(["admin", "facility_user"])),
) -> DeclarationRead:
    return await declaration_service.create_declaration(session, data)


@router.post("/{declaration_id}/quantity", response_model=list[QuantityRead])
async def submit_quantity(
    declaration_id: int,
    items: list[QuantitySubmit],
    session: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(["admin", "facility_user"])),
) -> list[QuantityRead]:
    return await declaration_service.submit_quantity(session, declaration_id, items)


@router.post("/{declaration_id}/quality", response_model=list[QualityRead])
async def submit_quality(
    declaration_id: int,
    items: list[QualitySubmit],
    session: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(["admin", "verifier"])),
) -> list[QualityRead]:
    return await declaration_service.submit_quality(session, declaration_id, items)


@router.post("/{declaration_id}/verify", response_model=DeclarationRead)
async def verify_declaration(
    declaration_id: int,
    session: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(["admin", "verifier"])),
) -> DeclarationRead:
    declaration = await declaration_service.get_declaration(session, declaration_id)
    if declaration.status not in ("declared",):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Cannot verify a declaration with status '{declaration.status}'",
        )
    declaration.status = "verified"
    declaration.verified_at = datetime.now(UTC)
    await session.flush()
    await session.refresh(declaration)
    return DeclarationRead.model_validate(declaration)


@router.get("/{declaration_id}/payment", response_model=PaymentRead)
async def get_payment(
    declaration_id: int,
    session: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(["admin", "verifier", "auditor"])),
) -> PaymentRead:
    return await payment_service.compute_and_persist(session, declaration_id)


@router.post("/{declaration_id}/audit", response_model=AuditRead, status_code=status.HTTP_201_CREATED)
async def record_audit(
    declaration_id: int,
    data: AuditCreate,
    session: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(["admin", "auditor"])),
) -> AuditRead:
    await declaration_service.get_declaration(session, declaration_id)
    audit = VerificationAudit(declaration_id=declaration_id, **data.model_dump())
    session.add(audit)
    await session.flush()
    await session.refresh(audit)
    return AuditRead.model_validate(audit)


@router.get("/{declaration_id}/anomalies", response_model=AnomalyResult)
async def get_anomalies(
    declaration_id: int,
    session: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(["admin", "auditor", "verifier"])),
) -> AnomalyResult:
    return await anomaly_service.run(session, declaration_id)
