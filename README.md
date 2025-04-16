

---

# Döviz Takip Uygulaması 

## İçindekiler

1. [Giriş](#giriş)
2. [Projenin Amacı ve Kapsamı](#projenin-amacı-ve-kapsamı)
3. [Mimari ve Sistem Tasarımı](#mimari-ve-sistem-tasarımı)
4. [Kullanılan Teknolojiler](#kullanılan-teknolojiler)
5. [Kurulum ve Çalıştırma](#kurulum-ve-çalıştırma)
   - [Gereksinimler](#gereksinimler)
   - [Adım Adım Kurulum](#adım-adım-kurulum)
   - [Ortam Değişkenleri ve Konfigürasyon](#ortam-değişkenleri-ve-konfigürasyon)
6. [Dosya Yapısı ve Modüller](#dosya-yapısı-ve-modüller)
   - [Ana Uygulama (app/)](#ana-uygulama-app)
   - [Statik Dosyalar (static/)](#statik-dosyalar-static)
   - [Şablonlar (templates/)](#şablonlar-templates)
   - [API Entegrasyonu (api.py)](#api-entegrasyonu-apipy)
   - [Test Klasörü (tests/)](#test-klasörü-tests)
7. [Kullanım Senaryoları ve Özellikler](#kullanım-senaryoları-ve-özellikler)
8. [API Entegrasyonu Detayları](#api-entegrasyonu-detayları)
   - [Dış Veri Kaynağı (ExchangeRate API)](#dış-veri-kaynağı-exchangerate-api)
   - [Veri İşleme ve Hata Yönetimi](#veri-işleme-ve-hata-yönetimi)
9. [Kullanıcı Arayüzü ve İş Akışları](#kullanıcı-arayüzü-ve-iş-akışları)
   - [Ana Sayfa ve Veri Görselleştirme](#ana-sayfa-ve-veri-görselleştirme)
   - [Alarm ve Bildirim Sistemi](#alarm-ve-bildirim-sistemi)
   - [Kullanıcı Etkileşimleri](#kullanıcı-etkileşimleri)
10. [Test Stratejileri ve Süreçleri](#test-stratejileri-ve-süreçleri)
11. [Dağıtım ve Yayına Alma](#dağıtım-ve-yayına-alma)
12. [Sorun Giderme ve Destek](#sorun-giderme-ve-destek)
13. [Katkıda Bulunanlar ve İletişim](#katkıda-bulunanlar-ve-iletişim)
14. [Gelecek Planları ve Geliştirme Yol Haritası](#gelecek-planları-ve-geliştirme-yol-haritası)
15. [Lisans](#lisans)
16. [Ek Bilgiler ve Kaynaklar](#ek-bilgiler-ve-kaynaklar)

---

## Giriş

**Döviz Takip Uygulaması**, güncel döviz kurlarını takip etmek, geçmiş verileri analiz etmek ve belirli kurlar için alarm ve bildirim mekanizmaları sunmak üzere tasarlanmış bir web uygulamasıdır. Bu dökümantasyon, projenin iç işleyişine dair tüm detayları açıklamakta, kurulumu, kullanımını ve geliştirilebilecek noktaları kapsamaktadır.

---

## Projenin Amacı ve Kapsamı

### Amaç
- **Güncel Bilgi:** Kullanıcılara en güncel döviz kurlarını sunmak.
- **Alarm Sistemi:** Kullanıcı tarafından belirlenen eşik değerlerin aşılması durumunda bildirim sağlamak.
- **Veri Analizi:** Geçmiş döviz verilerinin grafiksel görselleştirmesiyle trend analizi yapabilmek.
- **Kullanıcı Deneyimi:** Kullanıcı dostu arayüz ve akıcı etkileşimlerle yüksek kullanılabilirlik sağlamak.

### Kapsam
- **Veri Kaynağı:** Dış API (ExchangeRate API veya benzeri) aracılığıyla gerçek zamanlı veri çekimi.
- **Kullanıcı Arayüzü:** Basit ama etkili bir web arayüzü.
- **Sunucu Tarafı İşlemleri:** Python/Flask tabanlı backend sistemi.
- **Veri Depolama:** SQLite veya alternatif veritabanı çözümleri.
- **Bildirim Mekanizması:** Alarm ve bildirim sistemleri.

---

## Mimari ve Sistem Tasarımı

### Genel Mimari
Proje, MVC (Model-View-Controller) mimarisine benzer şekilde katmanlı bir yapıda organize edilmiştir:

- **Model:** Veri tabanındaki bilgilerin yönetimi ve saklanması (örneğin, kullanıcı tercihleri, geçmiş kurlar).
- **View (Görünüm):** HTML, CSS, JavaScript ve Jinja2 şablonlarıyla oluşturulan kullanıcı arayüzü.
- **Controller:** Flask tabanlı uygulama mantığı, URL yönlendirmeleri, API istekleri ve veri işleme işlemleri.

### Bileşenler
- **API Entegrasyonu:** Gerçek zamanlı verilerin çekilmesi için harici API çağrıları.
- **Alarm Mekanizması:** Belirlenen koşullara göre tetiklenen alarm sistemi.
- **Veri İşleme:** API’den çekilen verilerin işlenmesi ve kullanıcıya sunulmadan önce filtrelenmesi.
- **Testler:** Her bileşenin hatasız çalışmasını sağlayan birim ve entegrasyon testleri.

---

## Kullanılan Teknolojiler

- **Frontend:**
  - HTML5, CSS3, JavaScript
  - İleri düzeyde stil yönetimi için Bootstrap veya TailwindCSS
- **Backend:**
  - Python 3.x
  - Flask Framework
- **Templating:**
  - Jinja2
- **Veritabanı:**
  - SQLite (hafif ve başlangıç için ideal)
  - Alternatif olarak PostgreSQL/MySQL
- **API:**
  - ExchangeRate API (veya benzeri servisler)
- **Test Araçları:**
  - pytest (birim ve entegrasyon testleri)
- **Diğer Araçlar:**
  - Git (versiyon kontrol)
  - Docker (isteğe bağlı, konteynerleştirme için)

---

## Kurulum ve Çalıştırma

### Gereksinimler

- Python 3.8 veya daha üst sürüm
- Git
- [Pipenv veya virtualenv](https://packaging.python.org/en/latest/guides/tool-recommendations/) (tercihe bağlı)

### Adım Adım Kurulum

1. **Depoyu Klonlayın:**

   ```bash
   git clone https://github.com/kullanici/doviz_takip.git
   cd doviz_takip
   ```

2. **Sanal Ortam Oluşturun:**

   Tercihe bağlı olarak:

   - **virtualenv Kullanarak:**
     ```bash
     python -m venv env
     source env/bin/activate  # Unix/MacOS
     env\Scripts\activate     # Windows
     ```

   - **Pipenv Kullanarak:**
     ```bash
     pipenv shell
     ```

3. **Gerekli Paketleri Yükleyin:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Ortam Değişkenleri ve Konfigürasyon:**

   Projede, hassas bilgileri saklamak için `.env` dosyası kullanılması önerilir. Örneğin:

   ```dotenv
   FLASK_APP=app/routes.py
   FLASK_ENV=development
   API_KEY=your_exchange_rate_api_key
   SECRET_KEY=your_secret_key
   ```

   Uygulama, bu dosyadaki bilgileri yükleyerek çalışır. `.env` dosyasını oluşturmayı unutmayın.

5. **Uygulamayı Başlatın:**

   ```bash
   flask run
   ```

   Sunucu, varsayılan olarak `http://127.0.0.1:5000` adresinde çalışacaktır.

---

## Dosya Yapısı ve Modüller

### Ana Dosya Yapısı

```
doviz_takip/
├── app/
│   ├── __init__.py      # Uygulamanın başlatılması ve Flask instance'ının oluşturulması
│   ├── routes.py        # URL yönlendirme ve isteklere cevap veren controller
│   ├── api.py           # Dış API çağrılarının yapıldığı modül
│   ├── models.py        # Veri modelleri ve veritabanı işlemleri
│   ├── utils.py         # Yardımcı fonksiyonlar (ör. hata işleme, loglama)
│   ├── static/          # CSS, JavaScript, resimler vs.
│   └── templates/       # Jinja2 şablon dosyaları (HTML)
├── tests/
│   ├── test_routes.py   # Routes için birim testler
│   ├── test_api.py      # API çağrıları için testler
│   └── test_models.py   # Veri modeli testleri
├── .env               # Ortam değişkenleri (örnek dosya: .env.example)
├── requirements.txt   # Python kütüphanelerinin listesi
├── Dockerfile         # (Opsiyonel) Uygulama konteynerleştirmesi için
├── README.md          # Bu dokümantasyon dosyası
└── LICENSE
```

### Modüllerin Açıklaması

- **app/\_\_init\_\_.py:**  
  - Flask uygulamasını yapılandırır.
  - Veritabanı bağlantısını ve diğer global ayarları başlatır.
  
- **app/routes.py:**  
  - Kullanıcı isteklerine cevap veren URL tanımlamaları.
  - Veri çekme, işleme ve şablon render etme işlemleri burada yönetilir.
  
- **app/api.py:**  
  - ExchangeRate API ya da benzeri servislerden veri çekmek için gerekli fonksiyonları içerir.
  - API çağrılarında hata yönetimi ve zaman aşımları burada ele alınır.
  
- **app/models.py:**  
  - Veri tabanı modelleri (ORM kullanılıyorsa; örneğin SQLAlchemy ile) bulunur.
  - Döviz verileri, kullanıcı tercihleri ve alarm ayarları gibi veriler burada saklanır.
  
- **app/utils.py:**  
  - Loglama, hata yönetimi, ve diğer yardımcı işlevsellik.
  
- **tests/**  
  - Her birim modül için kapsamlı testler yer alır.
  - Uygulamanın sağlam çalıştığından emin olmak için düzenli çalıştırılmalıdır.

---

## Kullanım Senaryoları ve Özellikler

### 1. Ana Sayfa
- **Gösterim:**  
  - Anlık döviz kurlarının listelendiği dinamik bir ekran.
  - Kullanıcılar, güncel verileri, grafik ve tablolar aracılığıyla izleyebilir.
  
- **Özellikler:**  
  - Otomatik güncelleme: Belirli aralıklarla arka planda API çağrıları yapılarak veriler yenilenir.
  - Veri sıralama: Artan/azalan sıralama seçenekleri sunulur.

### 2. Alarm Kurma ve Bildirim
- **Kurulum:**  
  - Kullanıcı, takip etmek istediği döviz çiftleri için eşik değer belirler.
  - Belirlenen eşik değerlerin aşılması durumunda sistem alarm tetikler.
  
- **Bildirimler:**  
  - E-posta veya push bildirim seçenekleri (sistem yapılandırmasına göre) entegre edilebilir.
  - Arayüz üzerinden aktif/alarm listesi yönetimi sağlanır.

### 3. Grafiksel Veri Görselleştirme
- **Analiz Araçları:**  
  - Geçmiş verilerin çizgi grafik, bar grafik gibi görsel analizleri.
  - Tarih aralığı seçimi ve detaylı inceleme imkanı.
  
- **Etkileşim:**  
  - Grafiklere yakınlaştırma, veri noktalarını detaylı görüntüleme.

### 4. Kullanıcı ve Ayar Yönetimi
- **Kullanıcı Girişi:**  
  - Gerekirse, kullanıcı hesap yönetimi eklenerek kişiselleştirilmiş ayarlar yapılabilir.
  
- **Ayarlar Paneli:**  
  - Alarm kurulumları, tercih edilen para birimleri ve bildirim ayarları yönetilebilir.

---

## API Entegrasyonu Detayları

### Dış Veri Kaynağı (ExchangeRate API)
- **Amaç:**  
  - Güncel döviz kurlarının alınması.
- **Çalışma Prensibi:**  
  - API anahtarının kullanılmasıyla düzenli aralıklarla veri çekilir.
  - JSON formatında yanıt alınır, daha sonra veri modellerine göre işlenir.
  
- **Kod Örneği:**

  ```python
  import requests
  import os

  API_KEY = os.getenv("API_KEY")
  BASE_URL = "https://api.exchangerate-api.com/v4/latest/USD"

  def get_exchange_rates():
      try:
          response = requests.get(BASE_URL, params={"apikey": API_KEY}, timeout=5)
          response.raise_for_status()
          data = response.json()
          return data.get('rates', {})
      except requests.RequestException as e:
          # Hata loglanabilir veya kullanıcıya uygun mesaj gösterilebilir
          print(f"API isteğinde hata oluştu: {e}")
          return {}
  ```

### Veri İşleme ve Hata Yönetimi
- **İş Akışı:**  
  - API’den dönen veriler, `get_exchange_rates()` fonksiyonu ile çekilir.
  - JSON verisi ayrıştırılır ve uygulama içindeki veri modellerine aktarılır.
  - Hata durumunda loglama ve yeniden deneme mekanizmaları devreye girer.
  
- **Hata Yönetimi:**  
  - Timeout, bağlantı kopukluğu ve beklenmeyen veri formatı durumlarında uygun hata mesajları üretilir.
  - Kullanıcının uygulamayı kesintisiz kullanabilmesi için fallback mekanizmaları devreye alınır.

---

## Kullanıcı Arayüzü ve İş Akışları

### Ana Sayfa ve Veri Görselleştirme
- **Şablonlar:**  
  - Ana sayfa için `templates/index.html` şablonu kullanılır.
  - Jinja2 sözdizimi ile dinamik içerik yerleştirilir.
  
- **İş Akışı:**  
  - Kullanıcı ana sayfaya geldiğinde, backend `routes.py` içerisindeki ilgili fonksiyon çağrılır.
  - API’den çekilen veriler HTML içerisinde dinamik olarak sunulur.
  - Grafikler için JavaScript kütüphaneleri (örneğin, Chart.js) entegre edilebilir.

### Alarm ve Bildirim Sistemi
- **Alarm Kurulumu:**  
  - Kullanıcı, belirlediği eşik değerleri ayarlayabilmek üzere özel bir form doldurur.
  - Form verileri, backend üzerinde işlenir ve kullanıcıya ait alarm kayıtları veritabanına eklenir.
  
- **Bildirim:**  
  - Alarm koşulları tetiklenirse, backend tetikleyici fonksiyonlarla bildirim gönderir.
  - Bildirim yöntemleri: E-posta, sistem içi uyarı veya mobil bildirim entegrasyonu.

### Kullanıcı Etkileşimleri
- **Dinamik Formlar:**  
  - Döviz çiftleri ekleme, alarm düzenleme ve filtreleme seçenekleri form tabanlı olarak sağlanır.
  - JavaScript ile sayfa dinamikleştirilir ve AJAX çağrıları yapılabilir.

---

## Test Stratejileri ve Süreçleri

### Test Kapsamı
- **Birim Testler:**  
  - Her modül (API, modeller, yardımcı fonksiyonlar) için ayrı ayrı testler.
  - Örnek: `tests/test_api.py` dosyasında API çağrılarının doğru çalıştığı kontrol edilir.
  
- **Entegrasyon Testleri:**  
  - Farklı bileşenlerin birlikte çalışma testi.
  
- **Kullanıcı Kabul Testleri (UAT):**  
  - Son kullanıcı senaryolarının doğrulanması için testler.

### Test Araçları
- **pytest:**  
  - Test komutları ile tüm testler çalıştırılır:
    ```bash
    pytest
    ```
- **Coverage:**  
  - Test kapsamını ölçmek için kullanılabilir.

---

## Dağıtım ve Yayına Alma

### Yerel ve Üretim Ortamları
- **Yerel Ortam:**  
  - Geliştirme esnasında `FLASK_ENV=development` ile hata ayıklama detaylı tutulur.
  
- **Üretim Ortamı:**  
  - `FLASK_ENV=production` ayarı, performans iyileştirmeleri ve hata yönetimi için kullanılır.
  - Gunicorn, uWSGI veya benzeri bir WSGI server ile deploy edilebilir.

### Docker ile Konteynerleştirme (Opsiyonel)
- **Dockerfile:**  
  - Uygulamanın containerize edilmesi için Dockerfile hazırlanabilir.
- **Docker Compose:**  
  - Veri tabanı ve uygulamanın beraber çalışması için docker-compose.yml dosyası oluşturulabilir.

Örnek Dockerfile:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV FLASK_APP=app/routes.py
ENV FLASK_ENV=production

EXPOSE 5000

CMD ["flask", "run", "--host=0.0.0.0"]
```

---

## Sorun Giderme ve Destek

### Yaygın Sorunlar
- **API Bağlantı Hataları:**  
  - API anahtarının doğruluğunu kontrol edin.
  - İnternet bağlantısını ve API hizmetinin durumunu kontrol edin.
  
- **Veritabanı Bağlantısı:**  
  - Veritabanı dosyasının veya bağlantı ayarlarının doğru yapılandırıldığından emin olun.
  
- **Ortam Değişkenleri:**  
  - `.env` dosyasındaki değişkenlerin doğru tanımlandığını kontrol edin.
  
- **Sunucu Hataları:**  
  - Flask log dosyalarını inceleyerek hangi hataların tetiklendiğini belirleyin.

### Destek ve İletişim
- **GitHub Issues:**  
  - Projenin GitHub deposunda issue açarak veya tartışma bölümünde soru sorabilirsiniz.
- **E-posta:**  
  - Destek için [destek@ornekdomain.com] adresine yazabilirsiniz (örnek, kendi e-posta adresinle güncelle).

---

## Katkıda Bulunanlar ve İletişim

- **Proje Sahibi:**  
  - [Adınız veya Takma Adınız] – [iletişim@ornekdomain.com]
- **Katkıda Bulunanlar:**  
  - [Katkıda bulunan kişi 1 (GitHub profili veya iletişim bilgileri)]
  - [Katkıda bulunan kişi 2 (GitHub profili veya iletişim bilgileri)]

Proje ile ilgili öneri, hata bildirimi veya katkıda bulunmak isteyenler GitHub üzerinden pull request gönderebilir veya direkt iletişim kurabilir.

---

## Gelecek Planları ve Geliştirme Yol Haritası

### Kısa Vadeli Hedefler
- Kullanıcı doğrulama ve oturum yönetimi eklenmesi.
- Gelişmiş grafik ve veri görselleştirme entegrasyonu (örneğin, Chart.js veya D3.js).
- Mobil cihazlar için responsive tasarım iyileştirmeleri.

### Uzun Vadeli Hedefler
- Gerçek zamanlı güncellemeler için WebSocket entegrasyonu.
- Çoklu dil desteği ve uluslararasılaştırma (i18n).
- Üçüncü parti ödeme entegrasyonları veya premium özellikler.
- Ek güvenlik önlemleri (örneğin, rate limiting, CSRF korumaları).

Geliştirme planları, kullanıcı geri bildirimleri ve proje geliştiricilerinin toplantıları sonucunda güncellenecektir.

---

## Ek Bilgiler ve Kaynaklar

- **Resmi Flask Dokümantasyonu:** [Flask Documentation](https://flask.palletsprojects.com)
- **Python Requests Kütüphanesi:** [Requests Documentation](https://docs.python-requests.org)
- **Jinja2 Şablon Motoru:** [Jinja2 Documentation](https://jinja.palletsprojects.com)
- **API Servisleri:**  
  - [ExchangeRate API](https://www.exchangerate-api.com) (veya kullandığınız servisin dökümantasyonu)
  
---




