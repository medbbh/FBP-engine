# API Reference

## Interactive Documentation

Start the server and navigate to the Swagger UI:

```bash
make up
# Open http://localhost:8000/docs
```

Or ReDoc: `http://localhost:8000/redoc`

---

## Authentication

All endpoints require a JWT Bearer token except `GET /health`.

### Get a Token

```http
POST /auth/token
Content-Type: application/x-www-form-urlencoded

username=admin@fbp.mr&password=your_password
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

Use in subsequent requests:
```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Roles

| Role | Permissions |
|------|-------------|
| `facility_user` | Create declarations, submit quantity/quality, view own reports |
| `verifier` | Mark verified, view all declarations, compute payment |
| `auditor` | Record audits, run anomaly detection, view all reports |
| `admin` | All of the above + create facilities, national reports |

---

## Endpoints

### Facilities

**Create facility** (admin only)
```http
POST /facilities/
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "CSB Boutilimit",
  "type": "CSB",
  "region": "Trarza",
  "district": "Boutilimit",
  "is_rural": true,
  "equity_coefficient": "1.30"
}
```

Response `201`:
```json
{"id": 21, "name": "CSB Boutilimit", "type": "CSB", "region": "Trarza", "district": "Boutilimit", "is_rural": true, "equity_coefficient": "1.30"}
```

---

### Declarations

**Create quarterly declaration**
```http
POST /declarations/
{"facility_id": 5, "year": 2024, "quarter": 1}
```

Response `201`:
```json
{"id": 1, "facility_id": 5, "year": 2024, "quarter": 1, "status": "draft", "submitted_at": null, "verified_at": null, "created_at": "2024-01-15T09:00:00Z"}
```

---

**Submit quantity data**
```http
POST /declarations/1/quantity
[
  {"indicator_id": 1, "declared_quantity": "95", "verified_quantity": "92"},
  {"indicator_id": 3, "declared_quantity": "38", "verified_quantity": "38"},
  {"indicator_id": 7, "declared_quantity": "110", "verified_quantity": "110"}
]
```

Response `200`: list of `QuantityRead` with `discrepancy_rate` computed.

---

**Submit quality checklist**
```http
POST /declarations/1/quality
[
  {"item_id": 1, "score_obtained": "1.0", "max_score": "1.0"},
  {"item_id": 2, "score_obtained": "0.5", "max_score": "1.0", "evaluator_notes": "Poubelle manquante"}
]
```

---

**Verify declaration** (verifier/admin)
```http
POST /declarations/1/verify
```

Response `200`: `DeclarationRead` with `status: "verified"`, `verified_at` set.

---

**Get payment breakdown** (verifier/auditor/admin)
```http
GET /declarations/1/payment
```

Response `200`:
```json
{
  "id": 1,
  "declaration_id": 1,
  "quantity_subtotal": "162500.00",
  "quality_score_pct": "0.9000",
  "equity_multiplier": "1.30",
  "gross_amount": "190125.00",
  "abatement_pct": "0.0000",
  "abatement_reason": null,
  "net_amount": "190125.00",
  "fraud_flag": false,
  "paid_at": null,
  "computed_at": "2024-04-10T14:23:00Z"
}
```

---

**Record counter-verification audit** (auditor/admin)
```http
POST /declarations/1/audit
{
  "audit_type": "community",
  "patients_sampled": 30,
  "patients_confirmed": 29,
  "anomaly_flag": false,
  "notes": "1 patient not found — likely relocated"
}
```

---

**Run anomaly detection** (verifier/auditor/admin)
```http
GET /declarations/1/anomalies
```

Response `200`:
```json
{
  "risk_score": "low",
  "flags": [],
  "total_flags": 0
}
```

---

### Reports

**Facility quarterly report** (all roles)
```http
GET /reports/facility/5
```

Returns list of `{facility, declaration, payment}` dicts for all quarters.

**National aggregation** (admin only)
```http
GET /reports/national/2024/1
```

Returns `{year, quarter, regions: {region_name: {facilities, total_net_amount, declarations[]}}}`.

---

### Import

**Upload quantity CSV** (facility_user/admin)
```http
POST /import/quantity/1
Content-Type: multipart/form-data
file: declarations_q1.csv
```

CSV format:
```csv
indicator_id,declared_quantity,verified_quantity
1,95,92
3,38,38
7,110,110
```

Excel format (`.xlsx`): same column headers, first row = header.

---

## Error Responses

| Code | Meaning |
|------|---------|
| `401` | Missing or invalid JWT |
| `403` | Role not authorized |
| `404` | Resource not found |
| `409` | Duplicate (declaration already exists for this facility+quarter) |
| `422` | Validation error or business rule violation |
