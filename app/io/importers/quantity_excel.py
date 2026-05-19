import io
from decimal import Decimal, InvalidOperation

import openpyxl

from app.io.importers.base import ImportResult
from app.schemas.quantity import QuantitySubmit


def parse_quantity_excel(content: bytes) -> ImportResult:
    """Parse an Excel file with headers: indicator_id, declared_quantity, verified_quantity."""
    result = ImportResult()
    try:
        wb = openpyxl.load_workbook(io.BytesIO(content), read_only=True, data_only=True)
        ws = wb.active
    except Exception as e:
        result.errors.append(f"Failed to open Excel file: {e}")
        return result

    rows = list(ws.iter_rows(values_only=True))
    if not rows:
        result.errors.append("Excel file is empty")
        return result

    headers = [str(h).strip().lower() if h else "" for h in rows[0]]
    try:
        idx_id = headers.index("indicator_id")
        idx_declared = headers.index("declared_quantity")
        idx_verified = headers.index("verified_quantity")
    except ValueError as e:
        result.errors.append(f"Missing header: {e}")
        return result

    for row_num, row in enumerate(rows[1:], start=2):
        try:
            item = QuantitySubmit(
                indicator_id=int(row[idx_id]),
                declared_quantity=Decimal(str(row[idx_declared])),
                verified_quantity=Decimal(str(row[idx_verified])),
            )
            result.data.append(item)
            result.rows += 1
        except (ValueError, InvalidOperation, TypeError) as e:
            result.errors.append(f"Row {row_num}: {e}")

    return result
