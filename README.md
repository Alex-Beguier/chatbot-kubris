# Chatbot Google Chat - Gestion d'incidents et MEP

Ce chatbot permet de générer automatiquement des communications standardisées pour les incidents et les mises en production (MEP) dans Google Chat.

## Fonctionnalités

### Commandes Incidentsa
- `/incident detection` - Génère un message d'incident détecté
- `/incident investigation` - Génère une mise à jour d'investigation
- `/incident resolution` - Génère un message de résolution d'incident

### Commandes MEP
- `/mep planned` - Génère une annonce de MEP planifiée
- `/mep started` - Génère un message de début de déploiement
- `/mep completed` - Génère un message de fin de déploiement

## Structure du projet

```
google-chat-bot/
├── main.py              # Application Flask principale
├── config.py            # Configuration et templates personnalisables
├── requirements.txt     # Dépendances Python
├── Dockerfile          # Configuration Docker
├── .dockerignore       # Fichiers à ignorer lors du build
└── README.md           # Documentation
```

## Déploiement sur Google Cloud Run

### Prérequis
- Compte Google Cloud avec facturation activée
- Google Cloud CLI installé et configuré
- Docker installé

### Étapes de déploiement

1. **Activer les APIs nécessaires :**
```bash
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
```

2. **Construire et déployer l'application :**
```bash
# Dans le répertoire du projet
gcloud run deploy google-chat-bot \
  --source . \
  --platform managed \
  --region europe-west1 \
  --allow-unauthenticated
```

3. **Récupérer l'URL du service :**
```bash
gcloud run services describe google-chat-bot --region=europe-west1 --format='value(status.url)'
```

## Configuration du bot Google Chat

1. **Créer une application Google Chat :**
   - Aller sur [Google Cloud Console](https://console.cloud.google.com/)
   - Naviguer vers "APIs & Services" > "Credentials"
   - Créer une nouvelle application Google Chat

2. **Configurer le webhook :**
   - URL du bot : `[URL_CLOUD_RUN]`
   - Activer les interactions
   - Configurer les permissions nécessaires

3. **Ajouter le bot à votre espace Google Chat**

## Test en local

```bash
# Installer les dépendances
pip install -r requirements.txt

# Lancer l'application
python main.py
```

L'application sera accessible sur `http://localhost:8080`

## Test avec curl

```bash
# Test de la commande incident
curl -X POST http://localhost:8080 \
  -H "Content-Type: application/json" \
  -d '{
    "message": {
      "text": "/incident detection",
      "thread": {"name": "spaces/test/threads/test"}
    }
  }'

# Test de la commande MEP
curl -X POST http://localhost:8080 \
  -H "Content-Type: application/json" \
  -d '{
    "message": {
      "text": "/mep planned",
      "thread": {"name": "spaces/test/threads/test"}
    }
  }'
```

## Personnalisation

Pour modifier les templates de messages, éditez le fichier `config.py`. Vous pouvez :

- Modifier les textes des messages
- Ajouter de nouveaux types de communication
- Changer les emojis et la mise en forme
- Adapter les timestamps et formats de date

## Monitoring

- Health check : `GET /health`
- Logs disponibles dans Google Cloud Console
- Métriques Cloud Run automatiquement collectées

## Sécurité

- L'application est configurée pour accepter les requêtes non authentifiées
- Pour la production, considérez l'ajout d'une authentification
- Les logs incluent les événements reçus pour le debugging

## Support

Pour toute question ou problème, consultez les logs dans Google Cloud Console ou testez localement avec les commandes curl fournies.

