from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import require_role
from app.core.database import get_db
from app.models.user import User
from app.schemas.declaration import DeclarationCreate, DeclarationRead
from app.schemas.quality import QualityRead, QualitySubmit
from app.schemas.quantity import QuantityRead, QuantitySubmit
from app.services import declaration_service

router = APIRouter(prefix="/declarations", tags=["declarations"])


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
