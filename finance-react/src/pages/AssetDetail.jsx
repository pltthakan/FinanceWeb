import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { Line } from 'react-chartjs-2'
import {
  Chart as ChartJS,
  CategoryScale, LinearScale, PointElement, LineElement,
  Title, Tooltip, Legend, Filler
} from 'chart.js'
import { fetchAssetChart } from '../api.js'

ChartJS.register(
  CategoryScale, LinearScale, PointElement, LineElement,
  Title, Tooltip, Legend, Filler
)

const TIMEFRAMES = [
  { k: '1d',  label: '1G' },
  { k: '5d',  label: '5G' },
  { k: '1mo', label: '1A' },
  { k: '1y',  label: '1Y' },
  { k: '5y',  label: '5Y' },
  { k: 'max', label: 'Max' }
]

const LABELS = {
  USD: 'USD/TRY', EUR: 'EUR/TRY', GBP: 'GBP/TRY',
  GramAltin: 'Gram Altın', OnsAltin: 'Ons Altın', Gumus: 'Gümüş',
  BIST100: 'BIST 100',
  BTCUSD: 'BTC/USD', ETHUSD: 'ETH/USD', XRPUSD: 'XRP/USD'
}

export default function AssetDetail() {
  const { assetName } = useParams()
  const title = LABELS[assetName] || assetName

  const [tf, setTf] = useState('1d')
  const [chart, setChart] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    let cancelled = false
    ;(async () => {
      setLoading(true)
      setError(null)
      try {
        const res = await fetchAssetChart(assetName, tf)
        if (cancelled) return
        setChart(res)
      } catch (e) {
        if (!cancelled) setError('Grafik verisi alınamadı.')
      } finally {
        if (!cancelled) setLoading(false)
      }
    })()
    return () => { cancelled = true }
  }, [assetName, tf])

  const last = chart?.prices?.[chart.prices.length - 1]
  const first = chart?.prices?.[0]
  const delta = (typeof last === 'number' && typeof first === 'number' && first !== 0)
    ? ((last - first) / first) * 100
    : null

  return (
    <div className="panel">
      <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 16 }}>
        <h2 className="panel-title" style={{ margin: 0 }}>{title}</h2>
        <Link to="/" className="btn outline small" style={{ marginLeft: 'auto' }}>← Ana Sayfa</Link>
      </div>

      <div className="timeframe-group">
        {TIMEFRAMES.map(t => (
          <button
            key={t.k}
            className={`timeframe-btn ${tf === t.k ? 'active' : ''}`}
            onClick={() => setTf(t.k)}
          >
            {t.label}
          </button>
        ))}
      </div>

      {loading && <p>Grafik yükleniyor…</p>}
      {error && <div className="alert danger">{error}</div>}

      {chart && !loading && !error && (
        <>
          {last !== undefined && (
            <div style={{ marginBottom: 12, display: 'flex', alignItems: 'baseline', gap: 12 }}>
              <span style={{ fontSize: '1.8rem', fontWeight: 700 }}>
                {Number(last).toLocaleString('tr-TR', { maximumFractionDigits: 4 })}
              </span>
              {delta !== null && (
                <span className={`badge ${delta > 0 ? 'up' : delta < 0 ? 'down' : 'flat'}`}>
                  {delta > 0 ? '▲' : delta < 0 ? '▼' : '•'} {delta.toFixed(2)}%
                </span>
              )}
            </div>
          )}
          <div style={{ height: 380 }}>
            <Line
              data={{
                labels: chart.labels,
                datasets: [{
                  label: title,
                  data: chart.prices,
                  borderColor: 'rgba(37,117,252,1)',
                  backgroundColor: 'rgba(37,117,252,0.12)',
                  borderWidth: 2,
                  pointRadius: 0,
                  fill: true,
                  tension: 0.2
                }]
              }}
              options={{
                responsive: true,
                maintainAspectRatio: false,
                interaction: { mode: 'index', intersect: false },
                scales: {
                  x: { ticks: { maxTicksLimit: 8, maxRotation: 0 } }
                },
                plugins: { legend: { display: false } }
              }}
            />
          </div>
        </>
      )}
    </div>
  )
}
