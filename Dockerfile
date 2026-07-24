FROM python:3.12-slim

# Installer les dépendances système pour matplotlib (libfreetype6, libpng)
RUN apt-get update && apt-get install -y \
    libfreetype6-dev \
    libpng-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Définir le répertoire de travail
WORKDIR /app

# Copier les fichiers de dépendances
COPY requirements.txt .

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Copier le reste du code
COPY . .

# Exposer le port
EXPOSE 10000

# Commande de démarrage
CMD ["gunicorn", "cimetiere_backend.wsgi:application", "--bind", "0.0.0.0:10000"]