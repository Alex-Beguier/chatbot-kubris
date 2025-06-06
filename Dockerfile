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

# 6. Définir la commande pour lancer notre application avec le serveur Gunicorn.
# C'est la commande que Cloud Run exécutera au démarrage du conteneur.
# On utilise la variable $PORT fournie par Cloud Run au lieu d'un port en dur.
# La forme "exec" est utilisée pour que Gunicorn soit le processus principal (PID 1).
CMD exec gunicorn --workers 1 --bind 0.0.0.0:$PORT main:app
