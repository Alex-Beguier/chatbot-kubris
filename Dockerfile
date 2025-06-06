# Utiliser une image Python officielle et légère
FROM python:3.9-slim

# Définir le répertoire de travail dans le conteneur
WORKDIR /app

# Copier le fichier des dépendances
COPY requirements.txt .

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Copier le reste du code de l'application
COPY . .

# Définir la commande pour lancer l'application avec Gunicorn (serveur de production)
# Cloud Run injecte automatiquement la variable d'environnement PORT
CMD ["gunicorn", "--bind", "0.0.0.0:$PORT", "main:app"]