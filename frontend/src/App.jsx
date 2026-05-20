import { Routes, Route, Navigate } from 'react-router-dom'
import LoginPage from './pages/LoginPage'
import FacilitiesPage from './pages/FacilitiesPage'
import DeclarationPage from './pages/DeclarationPage'
import NavBar from './components/NavBar'

function PrivateRoute({ children }) {
  return localStorage.getItem('token') ? children : <Navigate to="/login" replace />
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/" element={<PrivateRoute><NavBar /><FacilitiesPage /></PrivateRoute>} />
      <Route path="/declaration/:id" element={<PrivateRoute><NavBar /><DeclarationPage /></PrivateRoute>} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
