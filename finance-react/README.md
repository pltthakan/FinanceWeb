# Finance React — SPA ön yüz

Mevcut **Flask + Jinja** projesinin React'e çevrilmiş sayfa hâli.
Backend neredeyse dokunulmadan API olarak kullanılır; ön yüz **Vite + React + React Router** ile SPA olarak çalışır.

## Neden?

Eski Jinja versiyonunda her link tıklamasında tüm sayfa yeniden yükleniyor ve üst bar verileri her seferinde tekrar çekiliyordu. Bu sürümde:

1. **SPA** — sayfa geçişleri anlık; `React Router` tarayıcı `history` API'si ile çalışır, backend'e istek yok.
2. **Tek merkezi veri** — `LiveDataContext` `/api/data`'yı 60 saniyede bir bir kez çağırır. Top bar ve ana sayfa aynı kaynakla beslenir. Sayfa değiştirmek tekrar fetch tetiklemez.
3. **Yeni top bar** — tek yatay ticker, eşit genişlikli chip'ler, fiat ve kripto arasında dikey ayraç, dar ekranda yumuşak yatay kaydırma. Eski `flex-wrap` kaldırıldı.
4. **Sekme arka planda pasif** — `document.hidden` olduğunda polling askıya alınır.

## Çalıştırma

### 1. Backend (Flask) — olduğu gibi

```bash
# Projenin ana dizininde (FinanceWeb-main)
pip install -r requirements.txt
python run.py
# Varsayılan: http://localhost:5000
```

### 2. Backend'e iki küçük JSON endpoint ekle

Yorumlar ve Profil sayfaları JSON ile çalışır. `backend-patch/json_api.py` dosyasını şöyle ekle:

```bash
cp finance-react/backend-patch/json_api.py /path/to/FinanceWeb-main/app/routes/json_api.py
```

Sonra `app/__init__.py` içindeki import satırına `json_api`'yi ekle:

```python
# Eski:
from app.routes import main, auth, comments, profile
# Yeni:
from app.routes import main, auth, comments, profile, json_api
```

Flask sunucusunu yeniden başlat. Üç yeni endpoint gelecek:
- `GET /api/comments` — tüm yorum ağacı
- `GET /api/profile/<username>` — profil + yorum + takip listeleri
- `GET /api/me` — giriş yapmış kullanıcı

### 3. Frontend (React)

```bash
cd finance-react
npm install
npm run dev
# Vite: http://localhost:5173
```

Vite, `/api/*`, `/login`, `/logout`, `/follow`, `/asset/*` gibi yolları Flask'a (`:5000`) proxy'ler. Bu sayede **çerez tabanlı oturum** doğal çalışır, CORS ayarı gerekmez.

### 4. Prod build

```bash
npm run build
# dist/ klasörü çıkar. Flask'ın içine static olarak da sunulabilir
# veya Nginx gibi bir reverse proxy ile Flask önüne konulabilir.
```

## Dosya yapısı

```
finance-react/
├── package.json
├── vite.config.js          ← Flask'a proxy
├── index.html              ← Poppins + particles.js CDN
├── backend-patch/
│   └── json_api.py         ← Flask tarafına eklenecek
└── src/
    ├── main.jsx            ← root + providers
    ├── App.jsx             ← router
    ├── api.js              ← fetch helper'ları
    ├── index.css           ← tüm stil (yeni top bar dahil)
    ├── context/
    │   ├── LiveDataContext.jsx   ← 60 sn poll, visibilitychange desteği
    │   └── AuthContext.jsx       ← oturum aynası + /api/me senk.
    ├── components/
    │   ├── Layout.jsx
    │   ├── LiveRateBar.jsx       ← yeni top bar (eşit chip'li ticker)
    │   ├── Navbar.jsx
    │   └── ParticlesBackground.jsx
    └── pages/
        ├── Home.jsx
        ├── Converter.jsx         ← client-side, TRY üzerinden çapraz
        ├── Analysis.jsx          ← Chart.js + istemci tarafı RSI
        ├── News.jsx
        ├── About.jsx
        ├── Comments.jsx          ← /api/comments
        ├── Profile.jsx           ← /api/profile/:username
        ├── Login.jsx
        ├── Register.jsx
        ├── AssetDetail.jsx       ← /asset/:name/chart/:timeframe
        └── NotFound.jsx
```

## Top bar davranışı

| Senaryo | Davranış |
|---|---|
| Normal ekran (≥ 1100 px) | 10 chip tek satırda eşit genişlik alır, kenardan kenara |
| Orta ekran | chip'ler eşit genişlikte kalır; min 132 px'de sığamayınca yatay kaydırma devreye girer |
| Mobil | Parmakla kaydırılabilen şerit; scroll-snap ile chip'e yapışır |
| Fiyat değişimi | Chip 900 ms yumuşak yeşil (artış) veya kırmızı (düşüş) halo ile parlar |
| Chip tıklaması | İlgili varlık detay sayfası açılır (SPA geçişi, reload yok) |

## Performans notları

- `/api/data` 60 sn'de bir (tab aktifken); sekme arka plandaysa durur.
- Home, News, Converter aynı `LiveDataContext`'ten besleniyor — sayfa değişimi bedava.
- Analysis ve AssetDetail ilk mount'ta bir kez tarihsel veri çeker; timeframe değiştirince yeniden.
- Poppins font ve particles.js CDN'lerden preconnect + preload ile gelir.

## Bilinen sınırlamalar

- Flask tarafı flash mesajları (server-side flash) SPA'da görünmez — form sayfalarında hata mesajları istemci tarafından üretilir.
- Profil resmi yüklemek için yeni bir endpoint yok; mevcut profil resmi varsa `/static/profile_images/<dosya>` üzerinden görüntülenir.
- Alarm (bitcoin alarmı) özelliği şu an UI'da yok — ihtiyaç olursa Home'a küçük bir panel eklenebilir.
