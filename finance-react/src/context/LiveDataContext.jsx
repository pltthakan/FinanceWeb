import { createContext, useContext, useEffect, useRef, useState, useCallback } from 'react'
import { fetchLiveData } from '../api'

/**
 * Tüm sayfa ve üst bar tek bir kaynaktan beslenir.
 * - İlk mount: fetch
 * - Sonra 60 saniyede bir otomatik yenileme
 * - Sayfa görünür olmadığında poll askıya alınır (sekme arka planda -> kaynak israfı yok)
 * - Sayfalar arası geçişte yeniden fetch YOK; veri context'te tutulur.
 */

const LiveDataContext = createContext(null)

const POLL_MS = 60_000

export function LiveDataProvider({ children }) {
  const [data, setData] = useState(null)
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(true)
  const [lastUpdated, setLastUpdated] = useState(null)

  // Önceki değerleri saklayalım ki top bar renk göstergesini (yeşil/kırmızı) hesaplayabilelim
  const prevRef = useRef({})
  const timerRef = useRef(null)

  const load = useCallback(async () => {
    try {
      const next = await fetchLiveData()
      setData(prev => {
        // prev'deki sayısal değerleri önceki referans olarak sakla
        if (prev) {
          const prevUsd = prev.exchange_rates?.USD || 1
          prevRef.current = {
            USD: prev.exchange_rates?.USD,
            EUR: prev.exchange_rates?.EUR,
            GBP: prev.exchange_rates?.GBP,
            GramAltin: prev.asset_prices?.gram_altin,
            OnsAltin: prev.asset_prices?.ons_altin,
            Gumus: prev.asset_prices?.gumus,
            BIST100: prev.asset_prices?.bist100,
            BTCUSD: divOrNull(prev.other_crypto?.bitcoin?.price_try, prevUsd),
            ETHUSD: divOrNull(prev.other_crypto?.ethereum?.price_try, prevUsd),
            XRPUSD: divOrNull(prev.other_crypto?.ripple?.price_try, prevUsd)
          }
        }
        return next
      })
      setError(null)
      setLastUpdated(new Date())
    } catch (e) {
      console.error('LiveData load error:', e)
      setError(e)
    } finally {
      setLoading(false)
    }
  }, [])

  // Polling scheduler — sekme gizli iken durdur, görünür olunca devam
  useEffect(() => {
    let cancelled = false

    const startPoll = () => {
      stopPoll()
      timerRef.current = setInterval(() => {
        if (!document.hidden) load()
      }, POLL_MS)
    }
    const stopPoll = () => {
      if (timerRef.current) {
        clearInterval(timerRef.current)
        timerRef.current = null
      }
    }

    // İlk yükleme
    load().then(() => { if (!cancelled) startPoll() })

    const onVisibility = () => {
      if (document.hidden) {
        stopPoll()
      } else {
        // Tekrar görünür olduğunda hemen bir fetch + polling yeniden başlar
        load()
        startPoll()
      }
    }
    document.addEventListener('visibilitychange', onVisibility)

    return () => {
      cancelled = true
      stopPoll()
      document.removeEventListener('visibilitychange', onVisibility)
    }
  }, [load])

  // Üst bar için hazır map: { USD: {value, prev}, ... }
  const liveRates = buildLiveRates(data, prevRef.current)

  const value = {
    data,
    liveRates,
    loading,
    error,
    lastUpdated,
    refresh: load
  }

  return <LiveDataContext.Provider value={value}>{children}</LiveDataContext.Provider>
}

export function useLiveData() {
  const ctx = useContext(LiveDataContext)
  if (!ctx) throw new Error('useLiveData must be used within LiveDataProvider')
  return ctx
}

// ---------- helpers ----------

function buildLiveRates(data, prev) {
  if (!data) return null
  const er = data.exchange_rates || {}
  const ap = data.asset_prices || {}
  const oc = data.other_crypto || {}
  const usd = er.USD || null

  const mk = (label, value, prevValue, assetName, unit = '') => ({
    label,
    assetName,
    value,
    prev: prevValue,
    unit
  })

  return {
    fiat: [
      mk('USD',        er.USD,         prev.USD,       'USD',       '₺'),
      mk('EUR',        er.EUR,         prev.EUR,       'EUR',       '₺'),
      mk('GBP',        er.GBP,         prev.GBP,       'GBP',       '₺'),
      mk('Gram Altın', ap.gram_altin,  prev.GramAltin, 'GramAltin', '₺'),
      mk('Ons Altın',  ap.ons_altin,   prev.OnsAltin,  'OnsAltin',  '₺'),
      mk('Gümüş',      ap.gumus,       prev.Gumus,     'Gumus',     '₺'),
      mk('BIST 100',   ap.bist100,     prev.BIST100,   'BIST100',   '')
    ],
    crypto: [
      mk('BTC/USD', divOrNull(oc.bitcoin?.price_try,  usd), prev.BTCUSD, 'BTCUSD', '$'),
      mk('ETH/USD', divOrNull(oc.ethereum?.price_try, usd), prev.ETHUSD, 'ETHUSD', '$'),
      mk('XRP/USD', divOrNull(oc.ripple?.price_try,   usd), prev.XRPUSD, 'XRPUSD', '$')
    ]
  }
}

function divOrNull(a, b) {
  if (a === null || a === undefined || b === null || b === undefined || b === 0) return null
  const n = Number(a) / Number(b)
  if (!Number.isFinite(n)) return null
  return Math.round(n * 100) / 100
}
