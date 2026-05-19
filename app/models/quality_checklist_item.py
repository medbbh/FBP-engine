import enum
from decimal import Decimal

from sqlalchemy import Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class ServiceArea(str, enum.Enum):
    HYGIENE = "Hygiene"
    PATIENT_RECORDS = "Patient Records"
    DRUG_MANAGEMENT = "Drug Management"
    EQUIPMENT = "Equipment"
    CLINICAL_PROTOCOLS = "Clinical Protocols"
    MANAGEMENT = "Management"


class QualityChecklistItem(Base):
    __tablename__ = "quality_checklist_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(30), nullable=False, unique=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    service_area: Mapped[str] = mapped_column(String(50), nullable=False)
    max_points: Mapped[Decimal] = mapped_column(Numeric(6, 2), nullable=False)
    applies_to_facility_type: Mapped[str | None] = mapped_column(String(50), nullable=True)

    evaluations: Mapped[list["QualityEvaluation"]] = relationship(  # type: ignore[name-defined]  # noqa: F821
        back_populates="checklist_item"
    )
