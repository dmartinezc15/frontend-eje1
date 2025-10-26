import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { supabase } from '../lib/supabase'

export default function Signup() {
  const nav = useNavigate()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirm, setConfirm] = useState('')
  const [loading, setLoading] = useState(false)
  const [err, setErr] = useState<string | null>(null)

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (password !== confirm) { setErr('Las contraseñas no coinciden'); return }
    setLoading(true); setErr(null)
    const { data, error } = await supabase.auth.signUp({ email, password })
    if (error) setErr(error.message)
    else {
      // Con "Confirm email" desactivado, normalmente ya hay session
      if (data.session) nav('/', { replace: true })
      else nav('/login', { replace: true }) // fallback
    }
    setLoading(false)
  }

  return (
    <main className="login-wrap">
      <form className="login-card" onSubmit={onSubmit}>
        <h2>Crear cuenta</h2>
        <input type="email" placeholder="Email" value={email} onChange={e=>setEmail(e.target.value)} required />
        <input type="password" placeholder="Contraseña" value={password} onChange={e=>setPassword(e.target.value)} required />
        <input type="password" placeholder="Confirmar contraseña" value={confirm} onChange={e=>setConfirm(e.target.value)} required />
        {err && <div className="error">{err}</div>}
        <button className="primary" disabled={loading}>{loading ? 'Creando…' : 'Crear cuenta'}</button>
        <div className="muted" style={{marginTop:8}}>
          ¿Ya tienes cuenta? <Link className="link" to="/login">Inicia sesión</Link>
        </div>
      </form>
    </main>
  )
}
