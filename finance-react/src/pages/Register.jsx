import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext.jsx'

export default function Register() {
  const { register } = useAuth()
  const navigate = useNavigate()
  const [form, setForm] = useState({ username: '', email: '', password: '', confirm: '' })
  const [error, setError] = useState(null)
  const [busy, setBusy] = useState(false)

  const upd = (k) => (e) => setForm(f => ({ ...f, [k]: e.target.value }))

  const onSubmit = async (e) => {
    e.preventDefault()
    setError(null)
    if (form.password !== form.confirm) {
      setError('Şifreler eşleşmiyor.')
      return
    }
    setBusy(true)
    try {
      const ok = await register(form)
      if (ok) {
        navigate('/login', { state: { justRegistered: true } })
      } else {
        setError('Kayıt başarısız. Kullanıcı adı veya e-posta zaten alınmış olabilir.')
      }
    } catch {
      setError('Kayıt sırasında bir hata oluştu.')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="panel" style={{ maxWidth: 460, margin: '0 auto' }}>
      <h2 className="panel-title">Kayıt Ol</h2>
      {error && <div className="alert danger">{error}</div>}

      <form onSubmit={onSubmit}>
        <div className="form-row">
          <label htmlFor="u">Kullanıcı Adı</label>
          <input id="u" type="text" required value={form.username}
                 onChange={upd('username')} autoComplete="username" />
        </div>
        <div className="form-row">
          <label htmlFor="e">E-Posta</label>
          <input id="e" type="email" required value={form.email}
                 onChange={upd('email')} autoComplete="email" />
        </div>
        <div className="form-row">
          <label htmlFor="p">Şifre</label>
          <input id="p" type="password" required value={form.password}
                 onChange={upd('password')} autoComplete="new-password" />
        </div>
        <div className="form-row">
          <label htmlFor="c">Şifre (Tekrar)</label>
          <input id="c" type="password" required value={form.confirm}
                 onChange={upd('confirm')} autoComplete="new-password" />
        </div>
        <button type="submit" className="btn primary" disabled={busy}>
          {busy ? 'Kaydediliyor…' : 'Kayıt Ol'}
        </button>
      </form>

      <p style={{ marginTop: 16, fontSize: '0.9rem' }}>
        Zaten hesabın var mı? <Link to="/login">Giriş yap</Link>
      </p>
    </div>
  )
}
