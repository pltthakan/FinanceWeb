# Python temel imajı
FROM python:3.9-slim

# Çalışma dizinini /app olarak ayarla
WORKDIR /app

# Sistem bağımlılıklarını yükle
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    && rm -rf /var/lib/apt/lists/*

# requirements.txt dosyasını kopyala ve bağımlılıkları yükle
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Uygulama dosyalarını kopyala
COPY . .

# Container içinde dinlenecek port
EXPOSE 8000

# Uygulamayı Waitress ile başlat
CMD ["python", "run.py"]
