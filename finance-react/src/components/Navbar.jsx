import { useState } from 'react'
import { NavLink, Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext.jsx'

export default function Navbar() {
  const [open, setOpen] = useState(false)
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const close = () => setOpen(false)

  const onLogout = async () => {
    await logout()
    close()
    navigate('/')
  }

  return (
    <nav className="nav-bar">
      <div className="nav-bar-inner">
        <Link to="/" className="nav-brand" onClick={close}>
          Döviz &amp; Bitcoin Takip
        </Link>

        <button
          className="nav-toggle"
          aria-expanded={open}
          aria-label="Menüyü aç/kapat"
          onClick={() => setOpen(o => !o)}
        >
          ☰
        </button>

        <ul className={`nav-links ${open ? 'open' : ''}`}>
          <li><NavLink end to="/"          onClick={close} className={navCls}>Ana Sayfa</NavLink></li>
          <li><NavLink    to="/converter"  onClick={close} className={navCls}>Dönüştürücü</NavLink></li>
          <li><NavLink    to="/analysis"   onClick={close} className={navCls}>Analiz</NavLink></li>
          <li><NavLink    to="/news"       onClick={close} className={navCls}>Haberler</NavLink></li>
          <li><NavLink    to="/about"      onClick={close} className={navCls}>Hakkında</NavLink></li>
          <li><NavLink    to="/comments"   onClick={close} className={navCls}>Yorumlar</NavLink></li>

          {user ? (
            <>
              <li>
                <NavLink
                  to={`/profile/${user.username}`}
                  onClick={close}
                  className={navCls}
                >
                  Profil
                </NavLink>
              </li>
              <li>
                <button className="nav-link" onClick={onLogout} style={{ border: 'none', background: 'transparent', cursor: 'pointer' }}>
                  Çıkış
                </button>
              </li>
            </>
          ) : (
            <>
              <li><NavLink to="/login"    onClick={close} className={navCls}>Giriş</NavLink></li>
              <li><NavLink to="/register" onClick={close} className={navCls}>Kayıt Ol</NavLink></li>
            </>
          )}
        </ul>
      </div>
    </nav>
  )
}

function navCls({ isActive }) {
  return `nav-link ${isActive ? 'active' : ''}`
}
