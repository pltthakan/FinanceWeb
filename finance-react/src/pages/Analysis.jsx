import { useEffect, useState } from 'react'
import { Line } from 'react-chartjs-2'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js'
import { fetchHistorical } from '../api.js'

ChartJS.register(
  CategoryScale, LinearScale, PointElement, LineElement,
  Title, Tooltip, Legend, Filler
)

const CRYPTOS = ['bitcoin', 'ethereum', 'ripple', 'litecoin']

export default function Analysis() {
  const [history, setHistory] = useState({})
  const [loading, setLoading] = useState(true)
  const [error, setError]     = useState(null)

  useEffect(() => {
    let cancelled = false
    ;(async () => {
      try {
        const entries = await Promise.all(
          CRYPTOS.map(async c => [c, await fetchHistorical(c, 30)])
        )
        if (cancelled) return
        setHistory(Object.fromEntries(entries))
      } catch (e) {
        if (!cancelled) setError(e)
      } finally {
        if (!cancelled) setLoading(false)
      }
    })()
    return () => { cancelled = true }
  }, [])

  if (loading) {
    return <div className="panel"><h2 className="panel-title">Analiz</h2><p>Grafik verileri yükleniyor…</p></div>
  }
  if (error) {
    return <div className="panel"><div className="alert danger">Tarihsel veriler alınamadı.</div></div>
  }

  const btc = history.bitcoin || []
  const rsiValues = computeRSI(btc.map(p => p.price), 14)

  return (
    <>
      <div className="panel">
        <h2 className="panel-title">Kripto Fiyat Analizi — Son 30 Gün</h2>
        <div className="grid cols-2">
          {CRYPTOS.map(c => (
            <CryptoChart key={c} name={c} data={history[c] || []} />
          ))}
        </div>
      </div>

      <div className="panel">
        <h2 className="panel-title">Bitcoin RSI (14)</h2>
        <div style={{ height: 320 }}>
          <Line
            data={{
              labels: btc.map(p => new Date(p.time).toLocaleDateString('tr-TR')),
              datasets: [{
                label: 'Bitcoin RSI',
                data: rsiValues,
                borderColor: 'rgba(54,162,235,1)',
                backgroundColor: 'rgba(54,162,235,0.15)',
                borderWidth: 2,
                pointRadius: 0,
                fill: true,
                tension: 0.2
              }]
            }}
            options={{
              responsive: true,
              maintainAspectRatio: false,
              scales: {
                y: { min: 0, max: 100, ticks: { stepSize: 10 } }
              },
              plugins: {
                legend: { display: true }
              }
            }}
          />
        </div>
      </div>
    </>
  )
}

function CryptoChart({ name, data }) {
  const labels = data.map(p => new Date(p.time).toLocaleDateString('tr-TR'))
  const prices = data.map(p => p.price)
  const cap = name.charAt(0).toUpperCase() + name.slice(1)

  return (
    <div style={{ height: 260 }}>
      <h3 style={{ margin: '0 0 8px', fontSize: '1rem' }}>{cap}</h3>
      <Line
        data={{
          labels,
          datasets: [{
            label: `${cap} (USD)`,
            data: prices,
            borderColor: 'rgba(255,99,132,1)',
            backgroundColor: 'rgba(255,99,132,0.15)',
            borderWidth: 2,
            pointRadius: 0,
            fill: true,
            tension: 0.25
          }]
        }}
        options={{
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { display: true } }
        }}
      />
    </div>
  )
}

// Backend'deki compute_rsi ile aynı algoritma (Wilder RSI)
function computeRSI(prices, period = 14) {
  if (prices.length < period + 1) return prices.map(() => null)
  const changes = []
  for (let i = 1; i < prices.length; i++) changes.push(prices[i] - prices[i - 1])
  const gains  = changes.map(c => Math.max(c, 0))
  const losses = changes.map(c => Math.abs(Math.min(c, 0)))
  let avgGain = gains.slice(0, period).reduce((a, b) => a + b, 0) / period
  let avgLoss = losses.slice(0, period).reduce((a, b) => a + b, 0) / period
  const rsi = Array(period).fill(null)
  rsi.push(avgLoss === 0 ? 100 : 100 - 100 / (1 + avgGain / avgLoss))
  for (let i = period; i < changes.length; i++) {
    avgGain = (avgGain * (period - 1) + gains[i])  / period
    avgLoss = (avgLoss * (period - 1) + losses[i]) / period
    rsi.push(avgLoss === 0 ? 100 : 100 - 100 / (1 + avgGain / avgLoss))
  }
  return [null, ...rsi]
}
