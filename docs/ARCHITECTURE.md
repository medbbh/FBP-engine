# Architecture

## Component Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                        FastAPI App                           │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────────────┐ │
│  │ /auth        │  │ /facilities  │  │ /declarations     │ │
│  │ /import      │  │ /reports     │  │ /anomalies        │ │
│  └──────┬───────┘  └──────┬───────┘  └────────┬──────────┘ │
│         │                 │                    │             │
│  ┌──────▼─────────────────▼────────────────────▼──────────┐ │
│  │                   Service Layer                          │ │
│  │  facility_service  declaration_service  payment_service │ │
│  │  anomaly_service   report_service                       │ │
│  └──────┬─────────────────────────────────────┬───────────┘ │
│         │                                     │             │
│  ┌──────▼──────────┐               ┌──────────▼──────────┐ │
│  │  Engine Layer    │               │   Database Layer     │ │
│  │  (pure Python,   │               │   (SQLAlchemy 2.0)   │ │
│  │   no ORM)        │               │   AsyncSession       │ │
│  │                  │               │                      │ │
│  │ calculations.py  │               │   health_facilities  │ │
│  │ anomaly.py       │               │   quarterly_decl.    │ │
│  │ rule_engine.py   │               │   payments           │ │
│  └──────────────────┘               │   rule_sets          │ │
│                                     └──────────┬───────────┘ │
└───────────────────────────────────────────────┼─────────────┘
                                                │
                                         PostgreSQL 15
```

## ER Diagram

```mermaid
erDiagram
    health_facilities {
        int id PK
        string name
        string type
        string region
        string district
        bool is_rural
        decimal equity_coefficient
    }

    quantity_indicators {
        int id PK
        string code UK
        string name
        decimal unit_tariff
        string service_category
    }

    quality_checklist_items {
        int id PK
        string code UK
        string description
        string service_area
        decimal max_points
        string applies_to_facility_type
    }

    rule_sets {
        int id PK
        string name
        decimal quality_threshold
        string quality_multiplier_mode
        json abatement_brackets
        decimal equity_min
        decimal equity_max
        decimal payment_floor
        decimal bonus_above_quality
        date effective_from
        date effective_to
    }

    users {
        int id PK
        string email UK
        string hashed_password
        string role
        bool is_active
    }

    quarterly_declarations {
        int id PK
        int facility_id FK
        int year
        int quarter
        string status
        datetime submitted_at
        datetime verified_at
    }

    quantity_declarations {
        int id PK
        int declaration_id FK
        int indicator_id FK
        decimal declared_quantity
        decimal verified_quantity
        decimal discrepancy_rate
    }

    quality_evaluations {
        int id PK
        int declaration_id FK
        int item_id FK
        decimal score_obtained
        decimal max_score
        string evaluator_notes
    }

    payments {
        int id PK
        int declaration_id FK
        decimal quantity_subtotal
        decimal quality_score_pct
        decimal equity_multiplier
        decimal gross_amount
        decimal abatement_pct
        string abatement_reason
        decimal net_amount
        bool fraud_flag
        datetime paid_at
    }

    verification_audits {
        int id PK
        int declaration_id FK
        string audit_type
        int patients_sampled
        int patients_confirmed
        bool anomaly_flag
    }

    health_facilities ||--o{ quarterly_declarations : "has"
    quarterly_declarations ||--o{ quantity_declarations : "contains"
    quarterly_declarations ||--o{ quality_evaluations : "contains"
    quarterly_declarations ||--o| payments : "produces"
    quarterly_declarations ||--o{ verification_audits : "subject to"
    quantity_indicators ||--o{ quantity_declarations : "referenced by"
    quality_checklist_items ||--o{ quality_evaluations : "referenced by"
```

## Quarterly Cycle Sequence Diagram

```mermaid
sequenceDiagram
    participant F as Facility User
    participant API as FastAPI
    participant ACV as Verifier (ACV)
    participant Audit as Auditor
    participant DB as PostgreSQL

    F->>API: POST /declarations/ (facility, year, quarter)
    API->>DB: INSERT quarterly_declaration (status=draft)

    F->>API: POST /declarations/{id}/quantity (declared quantities)
    API->>DB: INSERT quantity_declarations
    Note over API: discrepancy_rate computed & persisted

    ACV->>API: POST /declarations/{id}/quality (checklist scores)
    API->>DB: INSERT quality_evaluations

    ACV->>API: POST /declarations/{id}/verify
    API->>DB: UPDATE status=verified, verified_at=now()

    ACV->>API: GET /declarations/{id}/payment
    API->>DB: SELECT rule_sets (active on declaration date)
    API->>API: compute_quantity_subtotal()
    API->>API: compute_quality_score()
    API->>API: compute_payment()
    API->>API: apply_abatement()
    API->>DB: INSERT payments (all components persisted)
    API-->>ACV: PaymentBreakdown (190,125 MRU)

    Audit->>API: GET /declarations/{id}/anomalies
    API->>DB: SELECT last 4 quarters (facility history)
    API->>DB: SELECT peer facilities (same type+region)
    API->>API: detect_anomalies() → RiskScore
    API-->>Audit: AnomalyResult (risk_score=low, flags=[])

    Audit->>API: POST /declarations/{id}/audit (community verification)
    API->>DB: INSERT verification_audits
```

## Key Design Decisions

### 1. Engine Isolation
`app/engine/` has **zero imports from `app/models/`**. It operates on plain Python dataclasses (`QuantityLine`, `QualityLine`). This makes the engine:
- Testable without a database
- Reusable as a standalone library
- Safe from ORM coupling

### 2. Decimal Arithmetic
All monetary values use `decimal.Decimal` with `Context(prec=10, rounding=ROUND_HALF_UP)`. PostgreSQL columns use `Numeric(14,2)`. Float is never used in financial computation.

### 3. Persisted Computations
`discrepancy_rate`, all payment components, and quality scores are **persisted at compute time**. The API never recomputes a displayed payment. This satisfies the PBF audit trail requirement.

### 4. RuleSet Versioning
The `rule_sets` table stores `effective_from`/`effective_to` dates. Historical recomputations automatically use the rules that were active at declaration time. This supports multi-year programme management.

### 5. Service Layer
`Routers → Services → Engine/DB`. Routers are thin HTTP adapters (≤ 20 lines each). Services contain orchestration logic. The engine is pure math.
