from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Numeric, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(primary_key=True)
    declaration_id: Mapped[int] = mapped_column(
        ForeignKey("quarterly_declarations.id"), nullable=False, unique=True
    )
    quantity_subtotal: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    quality_score_pct: Mapped[Decimal] = mapped_column(Numeric(6, 4), nullable=False)
    equity_multiplier: Mapped[Decimal] = mapped_column(Numeric(4, 2), nullable=False)
    gross_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    abatement_pct: Mapped[Decimal] = mapped_column(Numeric(6, 4), nullable=False, default=Decimal("0"))
    abatement_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    net_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    fraud_flag: Mapped[bool] = mapped_column(nullable=False, default=False)
    paid_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    computed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    declaration: Mapped["QuarterlyDeclaration"] = relationship(back_populates="payment")  # type: ignore[name-defined]  # noqa: F821
