# FBP Engine — Moteur de Financement Basé sur la Performance

[![Tests](https://img.shields.io/badge/tests-41%20passed-green)](tests/)
[![Python](https://img.shields.io/badge/python-3.11-blue)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Live Demo](https://img.shields.io/badge/demo-live-brightgreen)](https://fbp-engine.onrender.com)

**Live demo: https://fbp-engine.onrender.com**

---

## Français

### Présentation

Ce module est un moteur de calcul **FBP/PBF** (Financement Basé sur la Performance) open-source pour les systèmes de santé, aligné sur les standards du **World Bank PBF Toolkit** (Fritsche, Soeters, Meessen 2014) et utilisé au Rwanda, Burundi, Burkina Faso. Il est conçu pour le programme **INAYA** en Mauritanie.

### Formule de paiement

```
Paiement = (Σ quantité_i × tarif_i) × score_qualité × coefficient_équité
```

- **Quantité** : services vérifiés × tarif unitaire (en MRU)
- **Qualité** : score checklist agrégé [0.0–1.0] — multiplicateur déflateur
- **Équité** : coefficient géographique [1.0–1.5] pour les zones rurales enclavées
- **Seuil** : si qualité < 50%, paiement = 0
- **Abattement** : si écart déclaré/vérifié > 10%, abattement total + signalement fraude

### Démarrage rapide

```bash
git clone <repo-url> fbp-engine
cd fbp-engine
cp .env.example .env
make up         # démarre l'API + PostgreSQL
make migrate    # applique les migrations Alembic
make seed       # injecte 20 structures, 30 indicateurs, 100 critères qualité
make test       # lance les 41 tests (unitaires, intégration, propriétés)
```

API disponible sur `http://localhost:8000/docs` (Swagger interactif).

### Références

- Fritsche GB, Soeters R, Meessen B (2014). *Performance-Based Financing Toolkit*. Washington DC: World Bank.
- Rwanda PBF Procedures Manual (2012). MINALOC / MOH Rwanda.
- Burkina Faso PPTE-PBF (2020). Rapport d'évaluation à mi-parcours.

---

## English

### Overview

A standalone, open-source **PBF/FBP (Performance-Based Financing)** calculation engine for health facilities. Implements the World Bank PBF Toolkit standards used in Rwanda, Burundi, Burkina Faso, and now Mauritania (INAYA programme).

### Payment Formula

```
Payment = (Σ quantity_i × tariff_i) × quality_score × equity_coefficient
```

| Component | Description |
|-----------|-------------|
| `quantity_subtotal` | Σ(verified_quantity × unit_tariff) across all indicators |
| `quality_score` | Weighted checklist score [0.0–1.0] — acts as a deflator |
| `equity_coefficient` | Geographic bonus [1.0–1.5] for rural/remote facilities |
| Quality threshold | If score < 50%, payment = 0 |
| Abatement | Discrepancy > 10% → 100% abatement + fraud flag |

### Stack

| Layer | Technology |
|-------|-----------|
| API | FastAPI + Uvicorn |
| Database | PostgreSQL 15 + SQLAlchemy 2.0 (async) + Alembic |
| Validation | Pydantic v2 |
| Testing | pytest + hypothesis (property-based) |
| Statistics | numpy + scipy |
| Reports | reportlab (PDF) + openpyxl (Excel) |
| Auth | JWT (python-jose) + bcrypt (passlib) |
| Infrastructure | Docker + docker-compose |

### Quick Start

```bash
cp .env.example .env
make up && make migrate && make seed && make test
```

### Demo Credentials

The seed script creates a default admin account:

| Field    | Value          |
|----------|----------------|
| Email    | `admin@fbp.mr` |
| Password | `Admin1234!`   |
| Role     | `admin`        |

Frontend: `http://localhost:3000` — Backend Swagger: `http://localhost:8000/docs`

### API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/auth/token` | Login (OAuth2 password) |
| `POST` | `/facilities/` | Create facility (admin) |
| `GET` | `/facilities/` | List facilities |
| `POST` | `/declarations/` | Create quarterly declaration |
| `POST` | `/declarations/{id}/quantity` | Submit verified quantities |
| `POST` | `/declarations/{id}/quality` | Submit checklist scores |
| `POST` | `/declarations/{id}/verify` | Mark as verified |
| `GET` | `/declarations/{id}/payment` | Compute & return payment breakdown |
| `POST` | `/declarations/{id}/audit` | Record counter-verification |
| `GET` | `/declarations/{id}/anomalies` | Run anomaly detection |
| `GET` | `/reports/facility/{id}` | Facility quarterly report |
| `GET` | `/reports/national/{year}/{quarter}` | National aggregation (admin) |
| `POST` | `/import/quantity/{id}` | Upload CSV/Excel declaration |

### Architecture

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for ER diagrams and sequence diagrams.
See [docs/PBF_METHODOLOGY.md](docs/PBF_METHODOLOGY.md) for the theoretical framework.

### License

MIT — see [LICENSE](LICENSE).
