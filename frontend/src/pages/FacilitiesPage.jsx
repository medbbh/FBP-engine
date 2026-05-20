import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { getFacilities, createDeclaration } from '../api'

function StatusBadge({ s }) {
  return <span className={`badge badge-${s}`}>{s}</span>
}

export default function FacilitiesPage() {
  const [facilities, setFacilities] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [creating, setCreating] = useState(null) // facility id being acted on
  const [form, setForm] = useState({ year: 2024, quarter: 1 })
  const [showForm, setShowForm] = useState(null) // facility id for which form is shown
  const navigate = useNavigate()

  useEffect(() => {
    getFacilities()
      .then((r) => setFacilities(r.data.items))
      .catch(() => setError('Impossible de charger les structures. Le backend est-il démarré?'))
      .finally(() => setLoading(false))
  }, [])

  async function startDeclaration(facilityId) {
    setCreating(facilityId)
    try {
      const res = await createDeclaration({ facility_id: facilityId, year: form.year, quarter: form.quarter })
      navigate(`/declaration/${res.data.id}`)
    } catch (err) {
      alert(err.response?.data?.detail || 'Erreur lors de la création de la déclaration')
    } finally {
      setCreating(null)
      setShowForm(null)
    }
  }

  if (loading) return <div className="page" style={{ textAlign: 'center', paddingTop: 80, color: 'var(--gray-400)' }}><span className="spinner" /></div>

  return (
    <div className="page">
      <div className="page-header">
        <h2>Structures de santé</h2>
        <span style={{ fontSize: 13, color: 'var(--gray-400)' }}>{facilities.length} structures</span>
      </div>

      {error && <div className="alert alert-error">{error}</div>}

      <div className="grid-3" style={{ marginBottom: 24 }}>
        <div className="card" style={{ padding: '20px 24px' }}>
          <div className="stat-value">{facilities.length}</div>
          <div className="stat-label">Structures</div>
        </div>
        <div className="card" style={{ padding: '20px 24px' }}>
          <div className="stat-value">{facilities.filter(f => f.is_rural).length}</div>
          <div className="stat-label">Rurales</div>
        </div>
        <div className="card" style={{ padding: '20px 24px' }}>
          <div className="stat-value">{[...new Set(facilities.map(f => f.region))].length}</div>
          <div className="stat-label">Régions</div>
        </div>
      </div>

      <div className="card">
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Structure</th>
                <th>Type</th>
                <th>Région</th>
                <th>District</th>
                <th>Rural</th>
                <th>Coefficient équité</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {facilities.map((f) => (
                <>
                  <tr key={f.id}>
                    <td style={{ fontWeight: 600 }}>{f.name}</td>
                    <td><span className="badge badge-declared">{f.type}</span></td>
                    <td>{f.region}</td>
                    <td>{f.district}</td>
                    <td>{f.is_rural ? '✓' : '—'}</td>
                    <td>×{f.equity_coefficient}</td>
                    <td>
                      <button
                        className="btn btn-primary btn-sm"
                        onClick={() => setShowForm(showForm === f.id ? null : f.id)}
                      >
                        Nouvelle déclaration
                      </button>
                    </td>
                  </tr>
                  {showForm === f.id && (
                    <tr key={`form-${f.id}`}>
                      <td colSpan={7} style={{ background: 'var(--gray-50)', padding: '16px 20px' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
                          <div>
                            <label className="form-label">Année</label>
                            <input
                              className="form-input"
                              type="number"
                              style={{ width: 100 }}
                              value={form.year}
                              onChange={(e) => setForm({ ...form, year: +e.target.value })}
                            />
                          </div>
                          <div>
                            <label className="form-label">Trimestre</label>
                            <select
                              className="form-select"
                              style={{ width: 90 }}
                              value={form.quarter}
                              onChange={(e) => setForm({ ...form, quarter: +e.target.value })}
                            >
                              <option value={1}>Q1</option>
                              <option value={2}>Q2</option>
                              <option value={3}>Q3</option>
                              <option value={4}>Q4</option>
                            </select>
                          </div>
                          <button
                            className="btn btn-success"
                            style={{ marginTop: 18 }}
                            onClick={() => startDeclaration(f.id)}
                            disabled={creating === f.id}
                          >
                            {creating === f.id ? <span className="spinner" /> : 'Créer →'}
                          </button>
                          <button
                            className="btn btn-outline"
                            style={{ marginTop: 18 }}
                            onClick={() => setShowForm(null)}
                          >
                            Annuler
                          </button>
                        </div>
                      </td>
                    </tr>
                  )}
                </>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
