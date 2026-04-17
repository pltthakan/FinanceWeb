<<<<<<< HEAD
FROM python:3.9-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /app/instance /app/logs

EXPOSE 8000

CMD ["python", "run.py"]
=======
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
>>>>>>> 1d546081434adb9efc9533d04b916628b6944a42
