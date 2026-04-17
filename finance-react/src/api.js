// Tüm çağrılar same-origin (Vite proxy sayesinde) — cookie'ler otomatik gönderilir.

const jsonHeaders = { 'Accept': 'application/json' }

export async function getJSON(url) {
  const res = await fetch(url, { credentials: 'include', headers: jsonHeaders })
  if (!res.ok) throw new Error(`GET ${url} -> ${res.status}`)
  return res.json()
}

export async function postForm(url, data) {
  const body = new URLSearchParams()
  Object.entries(data || {}).forEach(([k, v]) => {
    if (v !== undefined && v !== null) body.append(k, String(v))
  })
  const res = await fetch(url, {
    method: 'POST',
    credentials: 'include',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
      ...jsonHeaders
    },
    body,
    // Flask tarafı redirect döndürür; fetch varsayılan olarak takip eder.
    // Son url'yi kontrol ederek başarı/hata ayırt edebiliyoruz.
    redirect: 'follow'
  })
  return res
}

// Ana veri endpoint'i
export const fetchLiveData = () => getJSON('/api/data')

// Analiz sayfası: 30 gün tarihsel kripto verisi
export const fetchHistorical = (crypto, days = 30) =>
  getJSON(`/api/historical?crypto=${encodeURIComponent(crypto)}&days=${days}`)

// Varlık detay grafiği
export const fetchAssetChart = (assetName, timeframe) =>
  getJSON(`/asset/${encodeURIComponent(assetName)}/chart/${encodeURIComponent(timeframe)}`)
