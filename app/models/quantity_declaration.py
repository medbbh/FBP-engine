from decimal import Decimal

from sqlalchemy import ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class QuantityDeclaration(Base):
    __tablename__ = "quantity_declarations"

    id: Mapped[int] = mapped_column(primary_key=True)
    declaration_id: Mapped[int] = mapped_column(
        ForeignKey("quarterly_declarations.id"), nullable=False
    )
    indicator_id: Mapped[int] = mapped_column(
        ForeignKey("quantity_indicators.id"), nullable=False
    )
    declared_quantity: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    verified_quantity: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    # persisted at verification time — never recomputed (audit trail)
    discrepancy_rate: Mapped[Decimal] = mapped_column(Numeric(6, 4), nullable=False, default=Decimal("0"))

    declaration: Mapped["QuarterlyDeclaration"] = relationship(back_populates="quantity_declarations")  # type: ignore[name-defined]  # noqa: F821
    indicator: Mapped["QuantityIndicator"] = relationship(back_populates="quantity_declarations")  # type: ignore[name-defined]  # noqa: F821
