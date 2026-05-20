import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import {
  getDeclaration,
  getIndicators,
  getChecklist,
  submitQuantity,
  submitQuality,
  verifyDeclaration,
  getPayment,
  getAnomalies,
} from '../api'

const STEPS = [
  { key: 'info', label: '1. Déclaration' },
  { key: 'quantity', label: '2. Quantités' },
  { key: 'quality', label: '3. Qualité' },
  { key: 'verify', label: '4. Vérification' },
  { key: 'payment', label: '5. Paiement' },
  { key: 'anomalies', label: '6. Anomalies' },
]

const STATUS_STEP = {
  draft: 0,
  declared: 2,
  verified: 3,
  paid: 4,
  rejected: 0,
}

function StepBar({ active }) {
  return (
    <div className="steps">
      {STEPS.map((s, i) => {
        const idx = STEPS.findIndex((x) => x.key === active)
        const cls = i < idx ? 'step done' : i === idx ? 'step active' : 'step'
        return <div key={s.key} className={cls}>{i < idx ? '✓ ' : ''}{s.label}</div>
      })}
    </div>
  )
}

/* ─── Step 1: declaration header ─── */
function InfoStep({ declaration, onNext }) {
  return (
    <div className="card">
      <div className="card-title">Informations de la déclaration</div>
      <table style={{ width: 'auto' }}>
        <tbody>
          <tr><td style={{ color: 'var(--gray-600)', paddingRight: 32 }}>Identifiant</td><td>#{declaration.id}</td></tr>
          <tr><td style={{ color: 'var(--gray-600)' }}>Structure ID</td><td>{declaration.facility_id}</td></tr>
          <tr><td style={{ color: 'var(--gray-600)' }}>Période</td><td>Q{declaration.quarter} / {declaration.year}</td></tr>
          <tr><td style={{ color: 'var(--gray-600)' }}>Statut</td><td><span className={`badge badge-${declaration.status}`}>{declaration.status}</span></td></tr>
          {declaration.submitted_at && <tr><td style={{ color: 'var(--gray-600)' }}>Soumise le</td><td>{new Date(declaration.submitted_at).toLocaleString('fr-FR')}</td></tr>}
          {declaration.verified_at && <tr><td style={{ color: 'var(--gray-600)' }}>Vérifiée le</td><td>{new Date(declaration.verified_at).toLocaleString('fr-FR')}</td></tr>}
        </tbody>
      </table>
      <button className="btn btn-primary" style={{ marginTop: 20 }} onClick={onNext}>
        Saisir les quantités →
      </button>
    </div>
  )
}

/* ─── Step 2: quantity submission ─── */
function QuantityStep({ declarationId, onDone }) {
  const [indicators, setIndicators] = useState([])
  const [rows, setRows] = useState({})
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    getIndicators(30)
      .then((r) => {
        setIndicators(r.data)
        const init = {}
        r.data.forEach((ind) => {
          init[ind.id] = { declared: '', verified: '' }
        })
        setRows(init)
      })
      .catch(() => setError('Impossible de charger les indicateurs'))
      .finally(() => setLoading(false))
  }, [])

  function setVal(id, field, val) {
    setRows((prev) => ({ ...prev, [id]: { ...prev[id], [field]: val } }))
  }

  async function handleSubmit() {
    const items = indicators
      .filter((ind) => rows[ind.id]?.declared !== '' && rows[ind.id]?.verified !== '')
      .map((ind) => ({
        indicator_id: ind.id,
        declared_quantity: Number(rows[ind.id].declared),
        verified_quantity: Number(rows[ind.id].verified),
      }))

    if (items.length === 0) {
      setError('Veuillez saisir au moins une ligne de quantité')
      return
    }

    setSaving(true)
    setError('')
    try {
      await submitQuantity(declarationId, items)
      onDone()
    } catch (err) {
      setError(err.response?.data?.detail || 'Erreur lors de la soumission des quantités')
    } finally {
      setSaving(false)
    }
  }

  if (loading) return <div style={{ textAlign: 'center', padding: 40 }}><span className="spinner" /></div>

  return (
    <div className="card">
      <div className="card-title">Saisie des quantités</div>
      {error && <div className="alert alert-error">{error}</div>}
      <p style={{ color: 'var(--gray-600)', fontSize: 13, marginBottom: 16 }}>
        Laissez vide les lignes sans activité ce trimestre.
      </p>
      <div className="table-wrap" style={{ marginBottom: 20 }}>
        <table>
          <thead>
            <tr>
              <th>Code</th>
              <th>Indicateur</th>
              <th>Catégorie</th>
              <th>Tarif (MRU)</th>
              <th>Déclaré</th>
              <th>Vérifié</th>
            </tr>
          </thead>
          <tbody>
            {indicators.map((ind) => (
              <tr key={ind.id}>
                <td><code>{ind.code}</code></td>
                <td>{ind.name}</td>
                <td><span className="badge badge-declared">{ind.service_category}</span></td>
                <td>×{ind.unit_tariff}</td>
                <td>
                  <input
                    type="number"
                    min="0"
                    className="form-input"
                    style={{ width: 90 }}
                    value={rows[ind.id]?.declared ?? ''}
                    onChange={(e) => setVal(ind.id, 'declared', e.target.value)}
                    placeholder="0"
                  />
                </td>
                <td>
                  <input
                    type="number"
                    min="0"
                    className="form-input"
                    style={{ width: 90 }}
                    value={rows[ind.id]?.verified ?? ''}
                    onChange={(e) => setVal(ind.id, 'verified', e.target.value)}
                    placeholder="0"
                  />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div style={{ display: 'flex', gap: 12 }}>
        <button className="btn btn-success" onClick={handleSubmit} disabled={saving}>
          {saving ? <span className="spinner" /> : 'Soumettre les quantités →'}
        </button>
      </div>
    </div>
  )
}

/* ─── Step 3: quality submission ─── */
function QualityStep({ declarationId, onDone }) {
  const [items, setItems] = useState([])
  const [scores, setScores] = useState({})
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    getChecklist(20)
      .then((r) => {
        setItems(r.data)
        const init = {}
        r.data.forEach((it) => { init[it.id] = '' })
        setScores(init)
      })
      .catch(() => setError('Impossible de charger la grille qualité'))
      .finally(() => setLoading(false))
  }, [])

  async function handleSubmit() {
    const payload = items
      .filter((it) => scores[it.id] !== '')
      .map((it) => ({
        item_id: it.id,
        score_obtained: Number(scores[it.id]),
        max_score: Number(it.max_points),
        evaluator_notes: null,
      }))

    if (payload.length === 0) {
      setError('Veuillez noter au moins un critère')
      return
    }

    setSaving(true)
    setError('')
    try {
      await submitQuality(declarationId, payload)
      onDone()
    } catch (err) {
      setError(err.response?.data?.detail || 'Erreur lors de la soumission')
    } finally {
      setSaving(false)
    }
  }

  if (loading) return <div style={{ textAlign: 'center', padding: 40 }}><span className="spinner" /></div>

  return (
    <div className="card">
      <div className="card-title">Évaluation qualité</div>
      {error && <div className="alert alert-error">{error}</div>}
      <p style={{ color: 'var(--gray-600)', fontSize: 13, marginBottom: 16 }}>
        Affichage des 20 premiers critères. Laissez vide pour ignorer.
      </p>
      <div className="table-wrap" style={{ marginBottom: 20 }}>
        <table>
          <thead>
            <tr>
              <th>Code</th>
              <th>Critère</th>
              <th>Domaine</th>
              <th>Max pts</th>
              <th>Score obtenu</th>
            </tr>
          </thead>
          <tbody>
            {items.map((it) => (
              <tr key={it.id}>
                <td><code>{it.code}</code></td>
                <td style={{ maxWidth: 280 }}>{it.description}</td>
                <td><span className="badge badge-declared">{it.service_area}</span></td>
                <td>{it.max_points}</td>
                <td>
                  <input
                    type="number"
                    min="0"
                    max={it.max_points}
                    className="form-input"
                    style={{ width: 90 }}
                    value={scores[it.id] ?? ''}
                    onChange={(e) => setScores((prev) => ({ ...prev, [it.id]: e.target.value }))}
                    placeholder={`/${it.max_points}`}
                  />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <button className="btn btn-success" onClick={handleSubmit} disabled={saving}>
        {saving ? <span className="spinner" /> : 'Soumettre la qualité →'}
      </button>
    </div>
  )
}

/* ─── Step 4: verify ─── */
function VerifyStep({ declarationId, status, onDone }) {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  async function handleVerify() {
    setLoading(true)
    setError('')
    try {
      await verifyDeclaration(declarationId)
      onDone()
    } catch (err) {
      setError(err.response?.data?.detail || 'Erreur lors de la vérification')
    } finally {
      setLoading(false)
    }
  }

  if (status === 'verified' || status === 'paid') {
    return (
      <div className="card">
        <div className="alert alert-success">Déclaration déjà vérifiée.</div>
        <button className="btn btn-primary" onClick={onDone}>Voir le paiement →</button>
      </div>
    )
  }

  return (
    <div className="card">
      <div className="card-title">Vérification</div>
      {error && <div className="alert alert-error">{error}</div>}
      <p style={{ color: 'var(--gray-600)', fontSize: 13, marginBottom: 20 }}>
        La vérification valide les quantités déclarées. Statut actuel : <span className={`badge badge-${status}`}>{status}</span>
      </p>
      <button className="btn btn-success" onClick={handleVerify} disabled={loading}>
        {loading ? <span className="spinner" /> : 'Vérifier la déclaration →'}
      </button>
    </div>
  )
}

/* ─── Step 5: payment ─── */
function PaymentStep({ declarationId, onNext }) {
  const [payment, setPayment] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  async function load() {
    setLoading(true)
    setError('')
    try {
      const r = await getPayment(declarationId)
      setPayment(r.data)
    } catch (err) {
      setError(err.response?.data?.detail || 'Erreur lors du calcul du paiement')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [declarationId])

  if (loading) return <div style={{ textAlign: 'center', padding: 40 }}><span className="spinner" /></div>
  if (error) return <div className="card"><div className="alert alert-error">{error}</div><button className="btn btn-outline" onClick={load}>Réessayer</button></div>
  if (!payment) return null

  const fmt = (n) => new Intl.NumberFormat('fr-MR', { style: 'currency', currency: 'MRU', maximumFractionDigits: 2 }).format(n)

  return (
    <div className="card">
      <div className="card-title">Détail du paiement</div>
      {payment.fraud_flag && (
        <div className="alert alert-error" style={{ marginBottom: 16 }}>
          Alerte fraude — taux d'écart &gt;10%. Paiement bloqué.
        </div>
      )}
      <div className="grid-2" style={{ marginBottom: 24 }}>
        <div>
          <div className="stat-label">Sous-total quantité</div>
          <div className="stat-value">{fmt(payment.quantity_subtotal)}</div>
        </div>
        <div>
          <div className="stat-label">Score qualité</div>
          <div className="stat-value">{(Number(payment.quality_score_pct) * 100).toFixed(1)} %</div>
        </div>
        <div>
          <div className="stat-label">Coeff. équité</div>
          <div className="stat-value">×{payment.equity_multiplier}</div>
        </div>
        <div>
          <div className="stat-label">Montant brut</div>
          <div className="stat-value">{fmt(payment.gross_amount)}</div>
        </div>
      </div>
      {Number(payment.abatement_pct) > 0 && (
        <div className="alert alert-error" style={{ marginBottom: 16 }}>
          Abattement {(Number(payment.abatement_pct) * 100).toFixed(0)}% — {payment.abatement_reason}
        </div>
      )}
      <div style={{ background: 'var(--gray-50)', borderRadius: 8, padding: '20px 24px', border: '2px solid var(--blue)' }}>
        <div className="stat-label">Montant net à verser</div>
        <div className="stat-value" style={{ fontSize: 36 }}>{fmt(payment.net_amount)}</div>
      </div>
      <button className="btn btn-primary" style={{ marginTop: 20 }} onClick={onNext}>
        Analyse des anomalies →
      </button>
    </div>
  )
}

/* ─── Step 6: anomalies ─── */
function AnomaliesStep({ declarationId }) {
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  async function load() {
    setLoading(true)
    setError('')
    try {
      const r = await getAnomalies(declarationId)
      setResult(r.data)
    } catch (err) {
      setError(err.response?.data?.detail || 'Erreur lors de l\'analyse')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [declarationId])

  if (loading) return <div style={{ textAlign: 'center', padding: 40 }}><span className="spinner" /></div>
  if (error) return <div className="card"><div className="alert alert-error">{error}</div><button className="btn btn-outline" onClick={load}>Réessayer</button></div>
  if (!result) return null

  const riskColor = { low: 'verified', medium: 'draft', high: 'rejected' }

  return (
    <div className="card">
      <div className="card-title">Détection d'anomalies</div>
      <div style={{ display: 'flex', alignItems: 'center', gap: 16, marginBottom: 24 }}>
        <div>
          <div className="stat-label">Niveau de risque</div>
          <span className={`badge badge-${riskColor[result.risk_score]}`} style={{ fontSize: 16, padding: '6px 14px', marginTop: 6 }}>
            {result.risk_score.toUpperCase()}
          </span>
        </div>
        <div>
          <div className="stat-label">Signalements</div>
          <div className="stat-value">{result.total_flags}</div>
        </div>
      </div>

      {result.flags.length === 0 ? (
        <div className="alert alert-success">Aucune anomalie détectée.</div>
      ) : (
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Règle</th>
                <th>Indicateur</th>
                <th>Détail</th>
              </tr>
            </thead>
            <tbody>
              {result.flags.map((flag, i) => (
                <tr key={i}>
                  <td><span className="badge badge-rejected">{flag.rule}</span></td>
                  <td>{flag.indicator ?? '—'}</td>
                  <td style={{ fontSize: 12 }}>{flag.details}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}

/* ─── Main page ─── */
export default function DeclarationPage() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [declaration, setDeclaration] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [step, setStep] = useState('info')

  useEffect(() => {
    getDeclaration(id)
      .then((r) => {
        setDeclaration(r.data)
        const statusStep = STATUS_STEP[r.data.status] ?? 0
        setStep(STEPS[statusStep].key)
      })
      .catch(() => setError('Déclaration introuvable'))
      .finally(() => setLoading(false))
  }, [id])

  function refreshDeclaration() {
    return getDeclaration(id).then((r) => setDeclaration(r.data))
  }

  if (loading) return <div className="page" style={{ textAlign: 'center', paddingTop: 80 }}><span className="spinner" /></div>
  if (error) return <div className="page"><div className="alert alert-error">{error}</div></div>

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <h2>Déclaration #{declaration.id}</h2>
          <div style={{ fontSize: 13, color: 'var(--gray-400)', marginTop: 2 }}>
            Structure #{declaration.facility_id} — Q{declaration.quarter}/{declaration.year}
          </div>
        </div>
        <button className="btn btn-outline btn-sm" onClick={() => navigate('/')}>
          ← Retour
        </button>
      </div>

      <StepBar active={step} />

      {step === 'info' && (
        <InfoStep declaration={declaration} onNext={() => setStep('quantity')} />
      )}
      {step === 'quantity' && (
        <QuantityStep
          declarationId={Number(id)}
          onDone={async () => {
            await refreshDeclaration()
            setStep('quality')
          }}
        />
      )}
      {step === 'quality' && (
        <QualityStep
          declarationId={Number(id)}
          onDone={async () => {
            await refreshDeclaration()
            setStep('verify')
          }}
        />
      )}
      {step === 'verify' && (
        <VerifyStep
          declarationId={Number(id)}
          status={declaration.status}
          onDone={async () => {
            await refreshDeclaration()
            setStep('payment')
          }}
        />
      )}
      {step === 'payment' && (
        <PaymentStep declarationId={Number(id)} onNext={() => setStep('anomalies')} />
      )}
      {step === 'anomalies' && (
        <AnomaliesStep declarationId={Number(id)} />
      )}

      {/* Step navigation tabs */}
      <div style={{ display: 'flex', gap: 8, marginTop: 24, flexWrap: 'wrap' }}>
        {STEPS.map((s) => (
          <button
            key={s.key}
            className={step === s.key ? 'btn btn-primary btn-sm' : 'btn btn-outline btn-sm'}
            onClick={() => setStep(s.key)}
          >
            {s.label}
          </button>
        ))}
      </div>
    </div>
  )
}
