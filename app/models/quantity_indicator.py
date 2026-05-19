import enum
from decimal import Decimal

from sqlalchemy import Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class ServiceCategory(str, enum.Enum):
    MATERNAL_HEALTH = "Maternal Health"
    CHILD_HEALTH = "Child Health"
    CURATIVE_CARE = "Curative Care"
    PREVENTION = "Prevention"
    TB_HIV = "TB-HIV"


class QuantityIndicator(Base):
    __tablename__ = "quantity_indicators"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(30), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    unit_tariff: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    service_category: Mapped[str] = mapped_column(String(50), nullable=False)

    quantity_declarations: Mapped[list["QuantityDeclaration"]] = relationship(  # type: ignore[name-defined]  # noqa: F821
        back_populates="indicator"
    )
