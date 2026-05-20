import { Link, useNavigate } from 'react-router-dom'

export default function NavBar() {
  const navigate = useNavigate()
  const email = localStorage.getItem('email') || 'utilisateur'

  function logout() {
    localStorage.removeItem('token')
    localStorage.removeItem('email')
    navigate('/login')
  }

  return (
    <nav className="navbar">
      <h1>🏥 FBP Engine</h1>
      <div style={{ display: 'flex', alignItems: 'center', gap: 20, fontSize: 13 }}>
        <Link to="/">Structures</Link>
        <span style={{ color: 'rgba(255,255,255,.6)' }}>{email}</span>
        <button
          onClick={logout}
          style={{ background: 'rgba(255,255,255,.15)', color: '#fff', border: 'none', borderRadius: 6, padding: '5px 12px', cursor: 'pointer', fontSize: 12 }}
        >
          Déconnexion
        </button>
      </div>
    </nav>
  )
}
