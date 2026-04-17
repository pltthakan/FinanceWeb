export default function About() {
  return (
    <div className="panel">
      <h2 className="panel-title">Hakkında</h2>
      <p>
        Bu uygulama; döviz kurlarını, kripto paraları ve diğer finansal varlıkları
        tek ekranda, canlı olarak takip etmek için geliştirilmiştir.
      </p>
      <p>
        Ön yüz <strong>React + Vite</strong> ile tek sayfa uygulaması (SPA) olarak,
        veri katmanı <strong>Flask</strong> üzerinde yfinance ile çalışır. Üst şeritteki
        kurlar 60 saniyede bir arka planda yenilenir — sayfalar arası geçişte yeniden
        çekilmez, dolayısıyla gezinme anlıktır.
      </p>
      <p style={{ color: 'var(--muted)' }}>
        Kaynak: yfinance, CryptoPanic (haberler). Sunulan veriler finansal tavsiye değildir.
      </p>
    </div>
  )
}
