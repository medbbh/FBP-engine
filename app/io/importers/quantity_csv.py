import io
from decimal import Decimal, InvalidOperation

import pandas as pd

from app.io.importers.base import ImportResult
from app.schemas.quantity import QuantitySubmit

REQUIRED_COLUMNS = {"indicator_id", "declared_quantity", "verified_quantity"}


def parse_quantity_csv(content: bytes) -> ImportResult:
    """Parse a CSV file with columns: indicator_id, declared_quantity, verified_quantity."""
    result = ImportResult()
    try:
        df = pd.read_csv(io.BytesIO(content))
    except Exception as e:
        result.errors.append(f"Failed to parse CSV: {e}")
        return result

    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        result.errors.append(f"Missing required columns: {missing}")
        return result

    for i, row in df.iterrows():
        try:
            item = QuantitySubmit(
                indicator_id=int(row["indicator_id"]),
                declared_quantity=Decimal(str(row["declared_quantity"])),
                verified_quantity=Decimal(str(row["verified_quantity"])),
            )
            result.data.append(item)
            result.rows += 1
        except (ValueError, InvalidOperation, KeyError) as e:
            result.errors.append(f"Row {i + 2}: {e}")

    return result
