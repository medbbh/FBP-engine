from app.schemas.declaration import DeclarationRead
from app.schemas.payment import PaymentRead


def to_fhir_measure_report(declaration: DeclarationRead, payment: PaymentRead) -> dict:
    """FHIR R4 MeasureReport resource for HIS interoperability."""
    return {
        "resourceType": "MeasureReport",
        "status": "complete",
        "type": "summary",
        "measure": "https://fbp-engine.mr/fhir/Measure/PBF-quarterly",
        "subject": {
            "reference": f"Organization/{declaration.facility_id}",
        },
        "period": {
            "start": f"{declaration.year}-{(declaration.quarter - 1) * 3 + 1:02d}-01",
            "end": f"{declaration.year}-{declaration.quarter * 3:02d}-30",
        },
        "group": [
            {
                "id": "quantity-subtotal",
                "measureScore": {
                    "value": float(payment.quantity_subtotal),
                    "unit": "MRU",
                    "system": "urn:iso:std:iso:4217",
                    "code": "MRU",
                },
            },
            {
                "id": "quality-score",
                "measureScore": {
                    "value": float(payment.quality_score_pct),
                    "unit": "%",
                    "system": "http://unitsofmeasure.org",
                    "code": "%",
                },
            },
            {
                "id": "net-payment",
                "measureScore": {
                    "value": float(payment.net_amount),
                    "unit": "MRU",
                    "system": "urn:iso:std:iso:4217",
                    "code": "MRU",
                },
            },
        ],
        "extension": [
            {
                "url": "https://fbp-engine.mr/fhir/StructureDefinition/equity-coefficient",
                "valueDecimal": float(payment.equity_multiplier),
            },
            {
                "url": "https://fbp-engine.mr/fhir/StructureDefinition/fraud-flag",
                "valueBoolean": payment.fraud_flag,
            },
        ],
    }
