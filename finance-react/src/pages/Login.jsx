import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext.jsx'

export default function Login() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState(null)
  const [busy, setBusy] = useState(false)

  const onSubmit = async (e) => {
    e.preventDefault()
    setError(null)
    setBusy(true)
    try {
      const ok = await login(username.trim(), password)
      if (ok) navigate('/')
      else setError('Geçersiz kullanıcı adı veya şifre.')
    } catch {
      setError('Giriş sırasında bir hata oluştu.')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="panel" style={{ maxWidth: 460, margin: '0 auto' }}>
      <h2 className="panel-title">Giriş Yap</h2>
      {error && <div className="alert danger">{error}</div>}

      <form onSubmit={onSubmit}>
        <div className="form-row">
          <label htmlFor="u">Kullanıcı Adı</label>
          <input id="u" type="text" required value={username}
                 onChange={e => setUsername(e.target.value)} autoComplete="username" />
        </div>
        <div className="form-row">
          <label htmlFor="p">Şifre</label>
          <input id="p" type="password" required value={password}
                 onChange={e => setPassword(e.target.value)} autoComplete="current-password" />
        </div>
        <button type="submit" className="btn primary" disabled={busy}>
          {busy ? 'Giriş yapılıyor…' : 'Giriş Yap'}
        </button>
      </form>

      <p style={{ marginTop: 16, fontSize: '0.9rem' }}>
        Hesabınız yok mu? <Link to="/register">Kayıt olun</Link>
      </p>
    </div>
  )
}
