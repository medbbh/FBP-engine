import enum
from decimal import Decimal

from sqlalchemy import CheckConstraint, Enum, Numeric, String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class FacilityType(str, enum.Enum):
    CSB = "CSB"
    CENTRE_SANTE = "Centre Santé"
    HOPITAL_DISTRICT = "Hôpital District"
    CHR = "CHR"
    CHN = "CHN"


class HealthFacility(Base):
    __tablename__ = "health_facilities"
    __table_args__ = (
        CheckConstraint(
            "equity_coefficient >= 1.0 AND equity_coefficient <= 1.5",
            name="ck_equity_coefficient_range",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    region: Mapped[str] = mapped_column(String(100), nullable=False)
    district: Mapped[str] = mapped_column(String(100), nullable=False)
    is_rural: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    equity_coefficient: Mapped[Decimal] = mapped_column(
        Numeric(4, 2), nullable=False, default=Decimal("1.0")
    )

    declarations: Mapped[list["QuarterlyDeclaration"]] = relationship(  # type: ignore[name-defined]  # noqa: F821
        back_populates="facility", cascade="all, delete-orphan"
    )
