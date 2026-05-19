# PBF Methodology — Theoretical Framework

## What is PBF / FBP?

**Performance-Based Financing (PBF)** — or *Financement Basé sur la Performance (FBP)* — is a health system financing approach where health facilities are paid according to the **quantity** and **quality** of services they deliver, rather than receiving a fixed budget.

> "Instead of paying inputs (salaries, supplies), you pay results."

## The Three Pillars

### 1. Quantity Indicators

Each service category has a defined list of countable outputs with a **unit tariff** (in local currency):

| Category | Example Indicators | Typical Tariff Range (MRU) |
|----------|-------------------|--------------------------|
| Maternal Health | CPN1, CPN4, Assisted Delivery, C-Section | 300–2000 |
| Child Health | BCG, Pentavalent3, Measles vaccine | 200–500 |
| Curative Care | External consultation, Medical hospitalization | 80–500 |
| Prevention | TB screening, HIV screening, MILDA | 100–300 |
| TB-HIV | DOTS initiation, ARV initiation | 800–1500 |

An external verification team (ACV) physically counts services in facility registers and compares against declared figures.

### 2. Quality Indicators

A checklist of **100–200 criteria** evaluated per facility, covering:

| Service Area | # Items | Examples |
|-------------|---------|---------|
| Hygiene | 15 | Handwashing station, sterile equipment log |
| Patient Records | 20 | Registers up to date, birth certificates |
| Drug Management | 20 | No expired drugs, cold chain temperatures |
| Equipment | 15 | Functional delivery table, autoclave |
| Clinical Protocols | 20 | IMCI protocol used, partogram completed |
| Management | 10 | Staff meeting minutes, financial report |

The aggregate score is: `quality_score = Σ(score_obtained) / Σ(max_score) ∈ [0, 1]`

### 3. Equity Coefficient

To compensate for geographic inequities and encourage health workers in difficult zones:

| Zone Type | Coefficient |
|-----------|-------------|
| Urban (Nouakchott) | 1.0 |
| Peri-urban / Regional capital | 1.1–1.2 |
| Semi-rural (Trarza, Brakna) | 1.2–1.3 |
| Rural / Remote (Adrar, Tiris Zemmour) | 1.4–1.5 |

---

## The Standard PBF Payment Formula

```
Payment = (Σ quantity_i × tariff_i) × quality_score × equity_coefficient
```

### Worked Example — CSB Rosso, Trarza (Q1 2024)

**Facility:** CSB Rosso, rural, equity = 1.3

**Step 1 — Quantity subtotal:**
```
 95 CPN1         × 300 MRU  =  28,500 MRU
 42 CPN4         × 500 MRU  =  21,000 MRU
 38 Accouchements × 1,200 MRU = 45,600 MRU
110 Pentavalent3  × 300 MRU  =  33,000 MRU
430 Consultations ×  80 MRU  =  34,400 MRU
─────────────────────────────────────────
Subtotal                     = 162,500 MRU
```

**Step 2 — Quality score:**
```
48 items scored 1.0/1.0 + 12 items scored 0.5/1.0
= (48 + 6) / 60 = 54/60 = 0.90 (90%)
```

**Step 3 — Gross payment:**
```
162,500 × 0.90 × 1.3 = 190,125 MRU
```

**Step 4 — Abatement (3% discrepancy → bracket ≤5% → no abatement):**
```
Net payment = 190,125 MRU
```

---

## The Carrot-and-Stick Model

Quality is a **deflating multiplier**: 80% quality → 80% of quantity payment.

| Quality Score | Payment % |
|---------------|----------|
| ≥ 90% | 90–100% |
| 75–89% | 75–89% |
| 50–74% | 50–74% |
| < 50% | **0%** (threshold) |

Some programmes (Rwanda bonus model) add a **positive bonus** above 90%:
```
if quality_score ≥ 0.90: gross × (1 + bonus_pct)
```

---

## Abatement Rules

When the ACV finds a discrepancy between declared and verified quantities:

| Discrepancy | Action |
|-------------|--------|
| ≤ 5% | No abatement — normal counting error tolerance |
| 5–10% | Proportional abatement = discrepancy × 1.5 |
| > 10% | **100% abatement** + fraud flag + investigation |

---

## Counter-Verification (Community Verification)

A random sample of patients is traced in the community to confirm they received the declared services. If confirmation rate is low, additional abatement is applied.

---

## Anomaly Detection (AI Module)

This engine implements a statistical anomaly detection module to **prioritize on-site verifications** (risk-based verification, a Burkina Faso 2020 evidence-based approach):

| Rule | Trigger |
|------|---------|
| Own-history z-score | `|z| > 2.5` vs facility's own 4-quarter history |
| Peer z-score | `|z| > 2.5` vs same type+region facilities, same quarter |
| Sudden jump | Increase > 50% vs previous quarter |
| Quality drop | Drop > 20 percentage points vs previous quarter |

**Risk levels:** `low` (0 flags) → `medium` (1–2 flags) → `high` (3+ flags)

A `scikit-learn` IsolationForest ensemble model is planned as a v2 enhancement.

---

## References

1. Fritsche GB, Soeters R, Meessen B (2014). *Performance-Based Financing Toolkit*. Washington DC: World Bank. ISBN 978-1-4648-0069-6.
2. Rwanda Ministry of Health (2012). *PBF Procedures Manual*. Kigali: MOH Rwanda.
3. Burkina Faso Ministère de la Santé (2020). *Rapport d'évaluation à mi-parcours PPTE-PBF*. Ouagadougou.
4. Meessen B, Soucat A, Sekabaraga C (2011). Performance-based financing: just a donor fad or a catalyst towards comprehensive health-care reform? *Bulletin of the World Health Organization*, 89(2), 153-156.
