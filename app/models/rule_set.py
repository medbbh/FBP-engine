from datetime import date
from decimal import Decimal

from sqlalchemy import Date, JSON, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class RuleSet(Base):
    __tablename__ = "rule_sets"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    quality_threshold: Mapped[Decimal] = mapped_column(Numeric(4, 2), nullable=False, default=Decimal("0.50"))
    quality_multiplier_mode: Mapped[str] = mapped_column(String(20), nullable=False, default="deflator")
    # JSON: list of {"max_discrepancy": "0.05", "abatement_factor": "0.0"}
    abatement_brackets: Mapped[list] = mapped_column(JSON, nullable=False)
    equity_min: Mapped[Decimal] = mapped_column(Numeric(4, 2), nullable=False, default=Decimal("1.0"))
    equity_max: Mapped[Decimal] = mapped_column(Numeric(4, 2), nullable=False, default=Decimal("1.5"))
    payment_floor: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False, default=Decimal("0"))
    bonus_above_quality: Mapped[Decimal | None] = mapped_column(Numeric(4, 2), nullable=True)
    bonus_pct: Mapped[Decimal | None] = mapped_column(Numeric(4, 2), nullable=True)

    effective_from: Mapped[date] = mapped_column(Date, nullable=False)
    effective_to: Mapped[date | None] = mapped_column(Date, nullable=True)
