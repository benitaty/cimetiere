FROM python:3.12-slim

# Installer les dépendances système
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 10000

CMD ["gunicorn", "cimetiere_backend.wsgi:application", "--bind", "0.0.0.0:10000"]