from decimal import Decimal
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from app.schemas.declaration import DeclarationRead
from app.schemas.health_facility import FacilityRead
from app.schemas.payment import PaymentRead


def generate_facility_report(
    facility: FacilityRead,
    declaration: DeclarationRead,
    payment: PaymentRead | None,
) -> bytes:
    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, rightMargin=2 * cm, leftMargin=2 * cm,
                            topMargin=2 * cm, bottomMargin=2 * cm)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph(f"<b>Rapport FBP — {facility.name}</b>", styles["Title"]))
    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph(
        f"Région: {facility.region} | District: {facility.district} | Type: {facility.type}",
        styles["Normal"],
    ))
    story.append(Paragraph(
        f"Période: Q{declaration.quarter}/{declaration.year} | Statut: {declaration.status}",
        styles["Normal"],
    ))
    story.append(Spacer(1, 0.5 * cm))

    if payment:
        story.append(Paragraph("<b>Décomposition du paiement</b>", styles["Heading2"]))
        payment_data = [
            ["Composante", "Valeur"],
            ["Sous-total quantité (MRU)", f"{payment.quantity_subtotal:,.2f}"],
            ["Score qualité", f"{payment.quality_score_pct:.1%}"],
            ["Coefficient d'équité", f"×{payment.equity_multiplier}"],
            ["Montant brut (MRU)", f"{payment.gross_amount:,.2f}"],
            ["Abattement", f"{payment.abatement_pct:.1%}"],
            ["Montant net (MRU)", f"{payment.net_amount:,.2f}"],
            ["Alerte fraude", "OUI" if payment.fraud_flag else "Non"],
        ]
        table = Table(payment_data, colWidths=[10 * cm, 6 * cm])
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2563EB")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F1F5F9")]),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
        ]))
        story.append(table)

        if payment.abatement_reason:
            story.append(Spacer(1, 0.3 * cm))
            story.append(Paragraph(f"<i>Note abattement: {payment.abatement_reason}</i>", styles["Normal"]))
    else:
        story.append(Paragraph("<i>Paiement non encore calculé.</i>", styles["Normal"]))

    doc.build(story)
    return buf.getvalue()
