import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuth } from './auth/useAuth'
import Login from './pages/Login'
import Signup from './pages/Signup'
import ShopApp from './ShopApp'
import CheckoutReturn from './pages/CheckoutReturn'
import type { JSX } from 'react'

function RequireAuth({ children }: { children: JSX.Element }) {
  const { session, loading } = useAuth()
  if (loading) return <div style={{ padding: 16 }}>Cargando…</div>
  if (!session) return <Navigate to="/login" replace />
  return children
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login/>} />
      <Route path="/signup" element={<Signup/>} />
      <Route path="/checkout/return" element={<CheckoutReturn />} />
      <Route path="/" element={
        <RequireAuth>
          <ShopApp/>
        </RequireAuth>
      } />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
