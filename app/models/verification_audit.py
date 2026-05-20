import enum
from datetime import datetime

from sqlalchemy import Boolean, ForeignKey, Integer, String, Text, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class AuditType(str, enum.Enum):
    COMMUNITY = "community"
    COUNTER_VERIFICATION = "counter_verification"
    RISK_BASED = "risk_based"


class VerificationAudit(Base):
    __tablename__ = "verification_audits"

    id: Mapped[int] = mapped_column(primary_key=True)
    declaration_id: Mapped[int] = mapped_column(
        ForeignKey("quarterly_declarations.id"), nullable=False
    )
    audit_type: Mapped[str] = mapped_column(String(30), nullable=False)
    patients_sampled: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    patients_confirmed: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    anomaly_flag: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    conducted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    declaration: Mapped["QuarterlyDeclaration"] = relationship(back_populates="audits")  # type: ignore[name-defined]  # noqa: F821
