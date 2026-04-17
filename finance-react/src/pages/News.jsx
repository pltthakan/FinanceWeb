import { useLiveData } from '../context/LiveDataContext.jsx'

export default function News() {
  const { data, loading } = useLiveData()
  const news = data?.market_news || []

  return (
    <div className="panel">
      <h2 className="panel-title">Piyasa Haberleri</h2>

      {loading && !data && <p>Haberler yükleniyor…</p>}

      {!loading && news.length === 0 && <p>Haber verileri alınamadı.</p>}

      {news.length > 0 && (
        <div className="grid cols-3">
          {news.map((a, i) => (
            <a
              key={i}
              className="news-card"
              href={a.url}
              target="_blank"
              rel="noreferrer"
            >
              <h3>{a.title}</h3>
              {a.description
                ? <p>{a.description}</p>
                : <p style={{ fontStyle: 'italic' }}>Açıklama mevcut değil.</p>
              }
              <span style={{ color: 'var(--brand-b)', fontSize: '0.85rem', fontWeight: 600 }}>
                Detayları gör →
              </span>
            </a>
          ))}
        </div>
      )}
    </div>
  )
}
