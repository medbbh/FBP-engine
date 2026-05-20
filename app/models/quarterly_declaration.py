import enum
from datetime import datetime

import sqlalchemy as sa
from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class DeclarationStatus(str, enum.Enum):
    DRAFT = "draft"
    DECLARED = "declared"
    VERIFIED = "verified"
    PAID = "paid"
    REJECTED = "rejected"


class QuarterlyDeclaration(Base):
    __tablename__ = "quarterly_declarations"
    __table_args__ = (
        sa.UniqueConstraint("facility_id", "year", "quarter", name="uq_declaration_facility_year_quarter"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    facility_id: Mapped[int] = mapped_column(ForeignKey("health_facilities.id"), nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    quarter: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="draft")
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    facility: Mapped["HealthFacility"] = relationship(back_populates="declarations")  # type: ignore[name-defined]  # noqa: F821
    quantity_declarations: Mapped[list["QuantityDeclaration"]] = relationship(  # type: ignore[name-defined]  # noqa: F821
        back_populates="declaration", cascade="all, delete-orphan"
    )
    quality_evaluations: Mapped[list["QualityEvaluation"]] = relationship(  # type: ignore[name-defined]  # noqa: F821
        back_populates="declaration", cascade="all, delete-orphan"
    )
    payment: Mapped["Payment | None"] = relationship(  # type: ignore[name-defined]  # noqa: F821
        back_populates="declaration", uselist=False, cascade="all, delete-orphan"
    )
    audits: Mapped[list["VerificationAudit"]] = relationship(  # type: ignore[name-defined]  # noqa: F821
        back_populates="declaration", cascade="all, delete-orphan"
    )
