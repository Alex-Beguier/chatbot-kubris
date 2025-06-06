FROM python:3.9-slim

# 2. Définir une variable d'environnement pour que Python affiche les logs immédiatement.
ENV PYTHONUNBUFFERED True

# 3. Définir le répertoire de travail à l'intérieur du conteneur.
WORKDIR /app

# 4. Copier le fichier des dépendances et les installer.
# Ceci est fait en premier pour profiter du cache Docker si le code change mais pas les dépendances.
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# 5. Copier le reste du code de l'application dans le répertoire de travail.
COPY . .

# 6. Exposer le port que Gunicorn utilisera.
EXPOSE 8080

# 7. Définir la commande pour lancer notre application avec le serveur Gunicorn.
# C'est la commande que Cloud Run exécutera au démarrage du conteneur.
# On utilise maintenant 1 seul worker pour plus de stabilité sur les petites instances.
CMD ["gunicorn", "--workers", "1", "--bind", "0.0.0.0:8080", "main:app"]
