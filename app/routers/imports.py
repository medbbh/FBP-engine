from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import require_role
from app.core.database import get_db
from app.io.importers.quantity_csv import parse_quantity_csv
from app.io.importers.quantity_excel import parse_quantity_excel
from app.models.user import User
from app.schemas.quantity import QuantityRead
from app.services import declaration_service

router = APIRouter(prefix="/import", tags=["import"])


@router.post("/quantity/{declaration_id}", response_model=list[QuantityRead])
async def import_quantity_csv(
    declaration_id: int,
    file: UploadFile,
    session: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(["admin", "facility_user"])),
) -> list[QuantityRead]:
    content = await file.read()

    filename = file.filename or ""
    if filename.endswith(".xlsx") or filename.endswith(".xls"):
        result = parse_quantity_excel(content)
    else:
        result = parse_quantity_csv(content)

    if not result.success:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"errors": result.errors},
        )

    return await declaration_service.submit_quantity(session, declaration_id, result.data)
