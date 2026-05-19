from decimal import Decimal

INDICATORS = [
    # --- Maternal Health ---
    {"code": "CPN1", "name": "Consultation prénatale 1ère visite", "unit_tariff": Decimal("300"), "service_category": "Maternal Health"},
    {"code": "CPN4", "name": "Consultation prénatale 4ème visite (complète)", "unit_tariff": Decimal("500"), "service_category": "Maternal Health"},
    {"code": "ACC_ASSIST", "name": "Accouchement assisté par personnel qualifié", "unit_tariff": Decimal("1200"), "service_category": "Maternal Health"},
    {"code": "CPON", "name": "Consultation post-natale (dans les 6 semaines)", "unit_tariff": Decimal("200"), "service_category": "Maternal Health"},
    {"code": "PF_MODERNE", "name": "Nouvelles acceptantes planification familiale (méthode moderne)", "unit_tariff": Decimal("400"), "service_category": "Maternal Health"},
    {"code": "CESAR", "name": "Accouchement par césarienne", "unit_tariff": Decimal("2000"), "service_category": "Maternal Health"},

    # --- Child Health ---
    {"code": "VAC_BCG", "name": "Vaccination BCG (enfants < 1 an)", "unit_tariff": Decimal("250"), "service_category": "Child Health"},
    {"code": "VAC_PENTA3", "name": "Vaccination Pentavalent 3ème dose", "unit_tariff": Decimal("300"), "service_category": "Child Health"},
    {"code": "VAC_ROUGEOLE", "name": "Vaccination anti-rougeoleuse", "unit_tariff": Decimal("250"), "service_category": "Child Health"},
    {"code": "CNPE", "name": "Consultation nutrition enfant (0-5 ans) — pesée", "unit_tariff": Decimal("150"), "service_category": "Child Health"},
    {"code": "MAPE", "name": "Enfants malnutris aigus pris en charge (URENAM/URENAS)", "unit_tariff": Decimal("500"), "service_category": "Child Health"},
    {"code": "VAC_POLIO", "name": "Vaccination antipoliomyélitique orale (dose 3)", "unit_tariff": Decimal("200"), "service_category": "Child Health"},

    # --- Curative Care ---
    {"code": "CONSULT_CUR", "name": "Consultation curative externe (toutes pathologies)", "unit_tariff": Decimal("80"), "service_category": "Curative Care"},
    {"code": "HOSPIT_MED", "name": "Hospitalisation médicale (journée)", "unit_tariff": Decimal("300"), "service_category": "Curative Care"},
    {"code": "HOSPIT_CHIR", "name": "Hospitalisation chirurgicale (journée)", "unit_tariff": Decimal("500"), "service_category": "Curative Care"},
    {"code": "URGENCE", "name": "Consultation urgence (toutes heures)", "unit_tariff": Decimal("150"), "service_category": "Curative Care"},
    {"code": "PALUDISME", "name": "Cas de paludisme confirmé et traité (TDR+)", "unit_tariff": Decimal("200"), "service_category": "Curative Care"},

    # --- Prevention ---
    {"code": "DEPIST_TB", "name": "Dépistage tuberculose (examen crachat)", "unit_tariff": Decimal("300"), "service_category": "Prevention"},
    {"code": "DEPIST_VIH", "name": "Dépistage VIH (conseil-dépistage volontaire)", "unit_tariff": Decimal("200"), "service_category": "Prevention"},
    {"code": "MILDA_DIST", "name": "Moustiquaire imprégnée distribuée (MILDA)", "unit_tariff": Decimal("150"), "service_category": "Prevention"},
    {"code": "CONSULT_DENT", "name": "Consultation dentaire préventive", "unit_tariff": Decimal("100"), "service_category": "Prevention"},
    {"code": "VAC_TETANOS", "name": "Vaccination antitétanique femme enceinte (VAT2+)", "unit_tariff": Decimal("200"), "service_category": "Prevention"},
    {"code": "LAVAGE_MAINS", "name": "Séance d'éducation hygiène (lavage des mains)", "unit_tariff": Decimal("50"), "service_category": "Prevention"},

    # --- TB-HIV ---
    {"code": "DOTS_INIT", "name": "Patient tuberculeux mis sous traitement DOTS", "unit_tariff": Decimal("800"), "service_category": "TB-HIV"},
    {"code": "DOTS_SUIVI", "name": "Patient DOTS — suivi observance (par visite)", "unit_tariff": Decimal("150"), "service_category": "TB-HIV"},
    {"code": "ARV_INIT", "name": "Patient VIH+ mis sous ARV (initiation)", "unit_tariff": Decimal("1500"), "service_category": "TB-HIV"},
    {"code": "ARV_SUIVI", "name": "Patient ARV — consultation de suivi", "unit_tariff": Decimal("300"), "service_category": "TB-HIV"},
    {"code": "PTME", "name": "Femme enceinte VIH+ sous prophylaxie PTME", "unit_tariff": Decimal("600"), "service_category": "TB-HIV"},
    {"code": "TB_GUERIS", "name": "Patient TB déclaré guéri (fin traitement)", "unit_tariff": Decimal("1000"), "service_category": "TB-HIV"},
    {"code": "TB_VIH_COINFECT", "name": "Co-infection TB/VIH dépistée et prise en charge", "unit_tariff": Decimal("900"), "service_category": "TB-HIV"},
]
