# FBP Engine — Project Idea & Technical Brief

---

## PARTIE 1 : Comprendre le FBP en 5 minutes

### Le principe

Au lieu de payer les hôpitaux/centres de santé selon un budget fixe, on les paie selon ce qu'ils **produisent** et la **qualité** de ce qu'ils produisent.

> "Tu accouches 100 femmes ce trimestre avec qualité X, tu reçois Y MRU."

---

### Les 3 piliers obligatoires

#### 1. Indicateurs de QUANTITÉ
Les "services" comptables : consultations curatives, accouchements assistés, vaccinations enfants, visites prénatales, dépistages, contraception.
Chaque indicateur a un **tarif unitaire fixe**.

#### 2. Indicateurs de QUALITÉ
Un checklist de 100–200 critères regroupés par services (hygiène, dossiers patients complets, médicaments en stock, équipement fonctionnel, prescriptions correctes).
Donne un **score qualité en %**.

#### 3. Indicateurs d'ÉQUITÉ
Un coefficient majorateur pour les structures rurales/enclavées (typiquement **1.0 à 1.4**) pour compenser les coûts d'accès et encourager le travail en zone difficile.

---

### La formule de paiement standard

```
Paiement = (Σ quantité_i × tarif_i) × score_qualité × coefficient_équité
```

C'est le modèle **"carrot-and-stick"** : la qualité est un multiplicateur déflateur.
- Qualité = 80% → paiement réduit à 80%
- Qualité < 50% → paiement = 0 (dans la plupart des programmes)

---

### Le cycle FBP trimestriel

| Étape | Description |
|-------|-------------|
| 1. Déclaration | Le centre de santé remplit un formulaire mensuel, agrégé trimestriellement |
| 2. Vérification quantité | Une équipe externe (ACV) va sur place, compte dans les registres papier, compare au déclaré |
| 3. Vérification qualité | Passage de la grille checklist par un évaluateur |
| 4. Calcul du paiement | Application de la formule standard |
| 5. Contre-vérification | Échantillon de patients retrouvés en communauté pour vérifier qu'ils existent et ont bien été soignés (lutte contre la fraude) |
| 6. Abattement | Si un écart est trouvé, pénalité (ex : écart > 10% → abattement proportionnel ou refus) |
| 7. Audit IA | Détection automatique d'anomalies pour cibler les vérifications (partie moderne demandée dans le TDR) |

---

### Pays de référence

Rwanda (le pionnier, modèle de référence), Burundi, Burkina Faso, RDC, Cameroun.
La **Mauritanie** démarre maintenant via son système national de santé.

---

## PARTIE 2 : Technical Brief

### Project Overview

**Module FBP (Financement Basé sur la Performance)** — moteur de calcul d'indicateurs pour systèmes de santé.

Build a standalone, open-source FBP/PBF (Performance Based Financing) engine for health facilities, aligned with **World Bank PBF Toolkit standards** (Fritsche, Soeters, Meessen 2014) and used in Rwanda, Burundi, Burkina Faso, etc.

> This is a portfolio project demonstrating PBF expertise for a Mauritanian Ministry of Health tender.

- **Repo name:** `fbp-engine` or `pbf-health-engine`
- **License:** MIT
- **README:** French + English

---

### Stack

| Layer | Technology |
|-------|------------|
| Language | Python 3.11 |
| API | FastAPI |
| Database | PostgreSQL (SQLAlchemy 2.0 + Alembic) |
| Validation | Pydantic v2 |
| Testing | pytest |
| Infrastructure | Docker + docker-compose |
| Frontend (optional later) | React / Next.js dashboard |

---

### Domain Model (PostgreSQL Tables)

| Table | Key Fields |
|-------|-----------|
| `health_facilities` | id, name, type (CSB/Centre Santé/Hôpital District/CHR/…), region, district, is_rural (bool), equity_coefficient (1.0–1.5) |
| `quantity_indicators` | id, code (e.g. "CPN1", "ACC_ASSIST", "VAC_PENTA3"), name, unit_tariff (MRU), service_category (Maternal / Child / Curative / Prevention / TB-HIV) |
| `quality_checklist_items` | id, code, description, service_area (Hygiene / Patient Records / Drug Management / Equipment / Clinical Protocols / Management), max_points, applies_to_facility_type |
| `quarterly_declarations` | id, facility_id, year, quarter, status (draft / declared / verified / paid / rejected), submitted_at, verified_at |
| `quantity_declarations` | id, declaration_id, indicator_id, declared_quantity, verified_quantity, discrepancy_rate (computed) |
| `quality_evaluations` | id, declaration_id, item_id, score_obtained, max_score, evaluator_notes |
| `payments` | id, declaration_id, quantity_subtotal, quality_score_pct, equity_multiplier, gross_amount, abatement_pct, abatement_reason, net_amount, paid_at |
| `verification_audits` | id, declaration_id, audit_type (community / counter_verification / risk_based), patients_sampled, patients_confirmed, anomaly_flag |

---

### Core Calculation Engine

Implement these pure functions with full type hints and docstrings:

```python
def compute_quantity_subtotal(declarations: list[QuantityDeclaration]) -> Decimal:
    """Sum of (verified_quantity × unit_tariff) across all indicators."""

def compute_quality_score(evaluations: list[QualityEvaluation]) -> Decimal:
    """Returns weighted % score (0.0 - 1.0). Aggregate score_obtained / max_score across all checklist items."""

def compute_payment(
    quantity_subtotal: Decimal,
    quality_score: Decimal,
    equity_coefficient: Decimal,
    quality_threshold: Decimal = Decimal("0.50"),
) -> PaymentBreakdown:
    """
    Standard PBF formula (carrot-and-stick):
        payment = quantity_subtotal × quality_score × equity_coefficient
    If quality_score < quality_threshold, payment = 0 (or configurable).
    Return a breakdown with each component for audit transparency.
    """

def apply_abatement(payment: Decimal, discrepancy_rate: Decimal) -> tuple[Decimal, Decimal]:
    """
    If verified < declared, apply proportional abatement.
    Returns (final_payment, abatement_pct).
    Rules (configurable):
        discrepancy ≤ 5%           → no abatement
        5% < discrepancy ≤ 10%    → abatement = discrepancy × 1.5
        discrepancy > 10%          → 100% abatement (fraud) + flag for investigation
    """
```

> All amounts use `Decimal`, never `float`. Persist every computed component — never recompute on the fly for displayed payments (audit trail requirement).

---

### Configurable Rules Engine

PBF rules vary by country and contract version. Build a `RuleSet` Pydantic model with:

| Field | Description |
|-------|-------------|
| `quality_threshold` | Default `0.50` |
| `quality_multiplier_mode` | `"deflator"` \| `"bonus_threshold"` (Rwanda uses deflator; some programs add bonus above 75%) |
| `abatement_brackets` | `list[(max_discrepancy, abatement_factor)]` |
| `equity_min`, `equity_max` | Bounds for equity coefficient |
| `payment_floor` | Some contracts guarantee a minimum |
| `bonus_above_quality` | Optional, e.g. +10% above 90% quality |

Rules are **versioned in DB** (`rule_sets` table with `effective_from`, `effective_to`). Recomputations always use the rules valid at declaration date.

---

### Anomaly Detection (IA Module)

A `detect_anomalies(facility_id, current_declaration)` function using basic statistical methods (numpy/scipy — no ML framework needed initially):

- Z-score vs facility's own 4-quarter history per indicator → flag if |z| > 2.5
- Z-score vs peer facilities (same type, same region) → flag if |z| > 2.5
- Sudden jump > 50% in any indicator → flag
- Quality score drop > 20 percentage points → flag

Returns a `RiskScore` (`low` / `medium` / `high`) used to prioritize on-site verifications (risk-based verification, a Burkina Faso 2020 evidence-based approach).

Later, add a `scikit-learn` **IsolationForest** as optional second model. Comment it as `"v2 enhancement"`.

---

### Import / Export

| Direction | Format | Notes |
|-----------|--------|-------|
| Import | CSV / Excel | Template provided — rural facilities submit paper → digitized |
| Export | PDF | Per-facility quarterly reports using `reportlab` |
| Export | Excel | Regional/national rollups using `openpyxl` |
| Export | JSON | FHIR `MeasureReport` resource structure for HIS interoperability |

---

### FastAPI Endpoints (Minimum Viable Surface)

```
POST   /facilities/                        Create facility
GET    /facilities/                        List facilities

POST   /declarations/                      Create quarterly declaration
POST   /declarations/{id}/quantity         Submit quantity numbers
POST   /declarations/{id}/quality          Submit quality checklist scores
POST   /declarations/{id}/verify           Mark verified (with verified quantities)
GET    /declarations/{id}/payment          Compute and return payment breakdown
POST   /declarations/{id}/audit            Record counter-verification result
GET    /declarations/{id}/anomalies        Run anomaly detection

GET    /reports/facility/{id}              Quarterly report (PDF / Excel / JSON)
GET    /reports/national/{year}/{quarter}  Aggregated rollup
```

**Auth:** JWT. **Roles:** `facility_user`, `verifier`, `auditor`, `admin`.
Full request logging required (audit trail mandatory in PBF).

---

### Seed Data

Create realistic fixtures:
- **20 facilities** across Mauritanian regions (Nouakchott, Trarza, Brakna, Adrar, Hodh El Gharbi, etc.)
- **30 standard PBF indicators** with realistic Mauritanian tariffs in MRU
- **100-item quality checklist** split by service area

Use the Rwanda PBF indicator list as inspiration (publicly documented in their PBF Procedures Manual).

---

### Tests (Mandatory — this is the credibility proof)

| Type | Description |
|------|-------------|
| Unit tests | Every calculation function, with worked examples in test names (e.g. `test_quality_deflator_at_80_pct_reduces_payment_proportionally`) |
| Golden integration test | Full quarterly cycle for 1 facility, from declaration to payment, asserting exact MRU amount |
| Property-based tests | `hypothesis`: payment must always be in `[0, quantity_subtotal × equity_max]` |
| Edge cases | Zero quality, perfect quality, all discrepancies, missing checklist items |

---

### Documentation (this convinces the tender committee)

| Document | Content |
|----------|---------|
| `README.md` | French + English, PBF formula explained, references to World Bank PBF Toolkit |
| `docs/PBF_METHODOLOGY.md` | Quantity/quality/equity explained, carrot-and-stick model, citation of Fritsche/Soeters/Meessen 2014, Rwanda/Burundi/Burkina implementations |
| `docs/ARCHITECTURE.md` | ER diagram (Mermaid), sequence diagram for the quarterly cycle |
| `docs/API.md` | Auto-generated from FastAPI OpenAPI |
| Public demo | Cloud Run (free tier) with seeded data — tender committee can click and try |

---

### Git Workflow

**Conventional commits:** `feat:`, `fix:`, `docs:`
**Branches:** `main`, `dev`, `feature/*`

> Conventional commit format aligned with standard healthcare project requirements.
