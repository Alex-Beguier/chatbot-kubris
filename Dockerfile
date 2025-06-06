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

# Exposer le port
EXPOSE ${PORT}

# Commande pour démarrer l'application avec functions-framework
CMD functions-framework --target=handle_chat_webhook --port=${PORT} 