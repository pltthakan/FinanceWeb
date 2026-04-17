import { useMemo, useState } from 'react'
import { useLiveData } from '../context/LiveDataContext.jsx'

export default function Converter() {
  const { data, loading } = useLiveData()
  const rates = data?.exchange_rates || {}
  const currencies = useMemo(() => Object.keys(rates), [rates])

  const [amount, setAmount] = useState('1')
  const [from, setFrom] = useState('USD')
  const [to, setTo] = useState('EUR')

  const result = useMemo(() => {
    const a = parseFloat(amount)
    if (!Number.isFinite(a)) return null
    const rFrom = rates[from]
    const rTo = rates[to]
    if (!rFrom || !rTo) return null
    // Tüm kurlar TRY bazında. a (from) -> TRY -> (to)
    const inTRY = a * rFrom
    const out = inTRY / rTo
    return Math.round(out * 10000) / 10000
  }, [amount, from, to, rates])

  if (loading && !data) {
    return <div className="panel"><h2 className="panel-title">Döviz Dönüştürücü</h2><p>Kurlar yükleniyor…</p></div>
  }

  return (
    <div className="panel" style={{ maxWidth: 560, margin: '0 auto' }}>
      <h2 className="panel-title">Döviz Dönüştürücü</h2>

      <div className="form-row">
        <label htmlFor="amount">Miktar</label>
        <input
          id="amount"
          type="number"
          step="0.01"
          value={amount}
          onChange={e => setAmount(e.target.value)}
        />
      </div>

      <div className="form-row">
        <label htmlFor="from">Kaynak Para Birimi</label>
        <select id="from" value={from} onChange={e => setFrom(e.target.value)}>
          {currencies.map(c => <option key={c} value={c}>{c}</option>)}
        </select>
      </div>

      <div className="form-row">
        <label htmlFor="to">Hedef Para Birimi</label>
        <select id="to" value={to} onChange={e => setTo(e.target.value)}>
          {currencies.map(c => <option key={c} value={c}>{c}</option>)}
        </select>
      </div>

      {result !== null && (
        <div className="alert info" style={{ margin: 0 }}>
          <strong>{amount} {from}</strong> ≈ <strong>{result.toLocaleString('tr-TR')} {to}</strong>
        </div>
      )}

      <p style={{ fontSize: '0.8rem', color: 'var(--muted)', marginTop: 12 }}>
        Tüm çapraz kurlar TRY üzerinden hesaplanır. Veriler 60 saniyede bir güncellenir.
      </p>
    </div>
  )
}
