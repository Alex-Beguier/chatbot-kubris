# Utiliser l'image officielle Python
FROM python:3.11-slim

# Définir le répertoire de travail
WORKDIR /app

# Copier les fichiers requirements
COPY requirements.txt .

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code de l'application
COPY . .

# Variable d'environnement pour le port
ENV PORT=8080

# Commande pour démarrer l'application
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 wsgi:app

