FROM ubuntu:latest
LABEL authors="hatay"

ENTRYPOINT ["top", "-b"]

# Dockerfile
FROM python:3.11-slim

# sistem bağımlılıkları (gerekirse ekle)
RUN apt-get update && apt-get install -y build-essential git && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# önce requirements yükle (cache avantajı)
COPY ../requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# uygulama dosyalarını kopyala (dev sırasında volume ile üzerine yazılacak)
COPY . /app

EXPOSE 8000

# default command (compose ile override edilebilir)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]