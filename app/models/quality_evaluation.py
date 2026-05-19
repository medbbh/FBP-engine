from decimal import Decimal

import sqlalchemy as sa
from sqlalchemy import ForeignKey, Numeric, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class QualityEvaluation(Base):
    __tablename__ = "quality_evaluations"
    __table_args__ = (
        sa.UniqueConstraint("declaration_id", "item_id", name="uq_evaluation_declaration_item"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    declaration_id: Mapped[int] = mapped_column(
        ForeignKey("quarterly_declarations.id"), nullable=False
    )
    item_id: Mapped[int] = mapped_column(
        ForeignKey("quality_checklist_items.id"), nullable=False
    )
    score_obtained: Mapped[Decimal] = mapped_column(Numeric(6, 2), nullable=False)
    max_score: Mapped[Decimal] = mapped_column(Numeric(6, 2), nullable=False)
    evaluator_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    declaration: Mapped["QuarterlyDeclaration"] = relationship(back_populates="quality_evaluations")  # type: ignore[name-defined]  # noqa: F821
    checklist_item: Mapped["QualityChecklistItem"] = relationship(back_populates="evaluations")  # type: ignore[name-defined]  # noqa: F821
