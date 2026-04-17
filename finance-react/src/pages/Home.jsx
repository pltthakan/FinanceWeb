import { Link } from 'react-router-dom'
import { useLiveData } from '../context/LiveDataContext.jsx'

export default function Home() {
  const { data, loading, error, lastUpdated } = useLiveData()

  if (loading && !data) {
    return (
      <div className="panel">
        <h2 className="panel-title">Ana Sayfa</h2>
        <p>Veriler yükleniyor…</p>
      </div>
    )
  }

  if (error && !data) {
    return (
      <div className="panel">
        <div className="alert danger">
          Veri alınamadı. Sunucunun çalıştığından emin ol.
        </div>
      </div>
    )
  }

  const {
    exchange_rates = {},
    bitcoin_price,
    bitcoin_details = {},
    other_crypto = {},
    asset_prices = {},
    market_news = []
  } = data || {}

  return (
    <>
      <section className="panel">
        <h2 className="panel-title">Döviz Kurları (TRY)</h2>
        {Object.keys(exchange_rates).length ? (
          <table className="table">
            <thead>
              <tr><th>Para Birimi</th><th>TL Karşılığı</th></tr>
            </thead>
            <tbody>
              {Object.entries(exchange_rates).map(([cur, rate]) => (
                <tr key={cur}>
                  <td><strong>{cur}</strong></td>
                  <td>{fmt(rate)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : <p className="muted">Döviz kurları alınamadı.</p>}
      </section>

      <section className="panel">
        <h2 className="panel-title">Bitcoin Bilgileri</h2>
        {bitcoin_price ? (
          <div className="grid cols-2">
            <div className="data-card">
              <span className="label">Fiyat</span>
              <span className="value">{fmt(bitcoin_price)} TRY</span>
            </div>
            <div className="data-card">
              <span className="label">Market Cap</span>
              <span className="value">{fmt(bitcoin_details.market_cap_try)} TRY</span>
            </div>
            <div className="data-card">
              <span className="label">24 Saatlik Hacim</span>
              <span className="value">{fmt(bitcoin_details.volume_24h_try)} TRY</span>
            </div>
            <div className="data-card">
              <span className="label">24 Saatlik Değişim</span>
              <span className="value">
                <ChangeBadge pct={bitcoin_details.price_change_percentage_24h} />
              </span>
            </div>
          </div>
        ) : <p className="muted">Bitcoin fiyatı alınamadı.</p>}
      </section>

      <section className="panel">
        <h2 className="panel-title">Diğer Kripto Paralar</h2>
        {Object.keys(other_crypto).length ? (
          <div className="grid cols-3">
            {Object.entries(other_crypto).map(([name, d]) => (
              <div className="data-card" key={name}>
                <span className="label">{capitalize(name)}</span>
                <span className="value">{fmt(d.price_try)} TRY</span>
                <span className="sub">
                  <ChangeBadge pct={d.price_change_percentage_24h} />
                </span>
                <span className="sub">
                  Hacim: {fmt(d.volume_24h_try)} TRY
                </span>
              </div>
            ))}
          </div>
        ) : <p className="muted">Diğer kripto verileri alınamadı.</p>}
      </section>

      <section className="panel">
        <h2 className="panel-title">Diğer Varlıklar</h2>
        <div className="grid cols-2">
          <AssetRow label="Gram Altın" value={asset_prices.gram_altin} href="/assets/GramAltin" unit="TRY" />
          <AssetRow label="Ons Altın"  value={asset_prices.ons_altin}  href="/assets/OnsAltin"  unit="TRY" />
          <AssetRow label="Gümüş"      value={asset_prices.gumus}      href="/assets/Gumus"     unit="TRY" />
          <AssetRow label="BIST 100"   value={asset_prices.bist100}    href="/assets/BIST100"   unit=""    />
        </div>
      </section>

      <section className="panel">
        <h2 className="panel-title">Piyasa Haberleri</h2>
        {market_news?.length ? (
          <div className="grid cols-2">
            {market_news.slice(0, 8).map((a, i) => (
              <a key={i} className="news-card" href={a.url} target="_blank" rel="noreferrer">
                <h3>{a.title}</h3>
                {a.description && <p>{a.description}</p>}
              </a>
            ))}
          </div>
        ) : <p className="muted">Haber verileri alınamadı.</p>}
      </section>

      {lastUpdated && (
        <p style={{ textAlign: 'center', color: 'var(--muted)', fontSize: '0.85rem', marginTop: 12 }}>
          Son güncelleme: {lastUpdated.toLocaleTimeString('tr-TR')}
        </p>
      )}
    </>
  )
}

function AssetRow({ label, value, href, unit }) {
  return (
    <Link to={href} className="data-card" style={{ textDecoration: 'none' }}>
      <span className="label">{label}</span>
      <span className="value">{fmt(value)} {unit}</span>
    </Link>
  )
}

function ChangeBadge({ pct }) {
  if (pct === null || pct === undefined || pct === 'N/A') {
    return <span className="badge flat">N/A</span>
  }
  const n = Number(pct)
  if (!Number.isFinite(n)) return <span className="badge flat">N/A</span>
  const cls = n > 0 ? 'up' : n < 0 ? 'down' : 'flat'
  return <span className={`badge ${cls}`}>{n.toFixed(2)}%</span>
}

function fmt(n) {
  if (n === null || n === undefined || n === 'N/A') return 'N/A'
  const x = Number(n)
  if (!Number.isFinite(x)) return 'N/A'
  return x.toLocaleString('tr-TR', { maximumFractionDigits: 2 })
}

function capitalize(s) { return s.charAt(0).toUpperCase() + s.slice(1) }
