import { Link } from 'react-router-dom'

export default function NotFound() {
  return (
    <div className="panel" style={{ textAlign: 'center' }}>
      <h2 className="panel-title" style={{ justifyContent: 'center' }}>Sayfa Bulunamadı</h2>
      <p style={{ fontSize: '1.2rem' }}>404 — Aradığınız sayfa mevcut değil.</p>
      <Link to="/" className="btn primary" style={{ marginTop: 12 }}>Ana Sayfaya Dön</Link>
    </div>
  )
}
