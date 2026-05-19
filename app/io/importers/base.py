from dataclasses import dataclass, field

from app.schemas.quantity import QuantitySubmit


@dataclass
class ImportResult:
    rows: int = 0
    errors: list[str] = field(default_factory=list)
    data: list[QuantitySubmit] = field(default_factory=list)

    @property
    def success(self) -> bool:
        return len(self.errors) == 0
