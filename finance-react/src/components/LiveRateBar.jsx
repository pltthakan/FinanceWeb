import { useEffect, useRef, useState } from 'react'
import { Link } from 'react-router-dom'
import { useLiveData } from '../context/LiveDataContext.jsx'

/**
 * Canlı kur şeridi:
 * - Tek yatay ticker (flex-wrap YOK)
 * - Her chip flex: 1 ile eşit genişlik alır
 * - Dar ekranlarda overflow-x ile yatay kaydırma (momentumlu)
 * - Fiat/commodity ile kripto arasında dikey ince ayraç
 * - Değer değiştiğinde chip kısa süreli yeşil/kırmızı yanıp söner
 */
export default function LiveRateBar() {
  const { liveRates, loading } = useLiveData()

  return (
    <div className="live-bar">
      <div className="live-bar-inner">
        <div className="live-bar-track" aria-label="Canlı kur şeridi">
          {loading && !liveRates && <SkeletonChips count={10} />}

          {liveRates && (
            <>
              {liveRates.fiat.map(r => <RateChip key={r.assetName} item={r} />)}
              <div className="rate-divider" aria-hidden="true" />
              {liveRates.crypto.map(r => <RateChip key={r.assetName} item={r} />)}
            </>
          )}
        </div>
      </div>
    </div>
  )
}

function RateChip({ item }) {
  const { label, assetName, value, prev, unit } = item
  const [flash, setFlash] = useState(null)  // 'up' | 'down' | null
  const prevValueRef = useRef(value)

  useEffect(() => {
    if (
      typeof value === 'number' &&
      typeof prev === 'number' &&
      value !== prev
    ) {
      setFlash(value > prev ? 'up' : 'down')
      const t = setTimeout(() => setFlash(null), 950)
      return () => clearTimeout(t)
    }
    prevValueRef.current = value
  }, [value, prev])

  const dir = directionOf(value, prev)
  const displayValue = formatNumber(value)

  return (
    <Link
      to={`/assets/${assetName}`}
      className={`rate-chip ${flash ? `flash-${flash}` : ''}`}
      title={`${label} detayı`}
    >
      <span className="chip-label">{label}</span>
      <span className="chip-value">
        {displayValue === null
          ? <span className="skeleton">&nbsp;&nbsp;&nbsp;</span>
          : <>{unit}{displayValue}</>}
        {dir && <Arrow dir={dir} />}
      </span>
    </Link>
  )
}

function Arrow({ dir }) {
  if (dir === 'up')   return <span className="chip-arrow up">▲</span>
  if (dir === 'down') return <span className="chip-arrow down">▼</span>
  return <span className="chip-arrow flat">•</span>
}

function directionOf(v, p) {
  if (typeof v !== 'number' || typeof p !== 'number') return null
  if (v > p) return 'up'
  if (v < p) return 'down'
  return 'flat'
}

function formatNumber(v) {
  if (v === null || v === undefined || v === 'N/A') return null
  const n = Number(v)
  if (!Number.isFinite(n)) return null
  // 1000'den büyük sayıları bin ayracıyla
  if (Math.abs(n) >= 1000) {
    return n.toLocaleString('tr-TR', { maximumFractionDigits: 2 })
  }
  return n.toLocaleString('tr-TR', { maximumFractionDigits: 2, minimumFractionDigits: 2 })
}

function SkeletonChips({ count }) {
  return Array.from({ length: count }).map((_, i) => (
    <div className="rate-chip" key={i}>
      <span className="chip-label"><span className="skeleton">&nbsp;&nbsp;&nbsp;</span></span>
      <span className="chip-value"><span className="skeleton">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</span></span>
    </div>
  ))
}
