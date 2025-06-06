import os
import json
from flask import Flask, request

# Initialise l'application web Flask
app = Flask(__name__)

@app.route('/', methods=['POST'])
def handle_chat_event():
    """
    Point d'entrée principal qui reçoit et traite les requêtes (webhooks)
    de l'API Google Chat.
    """
    request_json = request.get_json(silent=True)

    # Si la requête est invalide, on ne fait rien pour l'instant.
    if not request_json:
        return {}

    response_data = {}
    
    # On vérifie si un message a été reçu
    if request_json['type'] == 'MESSAGE':
        message = request_json.get('message', {})
        command = ""
        
        # On regarde si une commande slash a été utilisée
        if message.get('slashCommand'):
            command = message['slashCommand']['commandName'].lower()
        else:
            # Sinon on lit le texte du message
            command = message.get('text', '').lower().strip()
        
        # Si la commande est /incident, on renvoie un simple texte
        if 'incident' in command:
            response_data = {"text": "Test de la commande /incident reçu !"}
        
        # Si la commande est /mep, on renvoie un simple texte
        elif 'mep' in command:
            response_data = {"text": "Test de la commande /mep reçu !"}
        
        # Pour tout autre message, on renvoie un message par défaut
        else:
            response_data = {"text": "Le bot de test est en ligne."}

    # Pour les clics sur les cartes (non utilisé dans cette version), on ne fait rien.
    elif request_json['type'] == 'CARD_CLICKED':
        response_data = {"text": "Clic détecté, mais les cartes sont désactivées dans cette version."}

    # Flask convertit automatiquement le dictionnaire en une réponse JSON
    return response_data


if __name__ == "__main__":
    # Cette partie est utile pour tester le serveur localement.
    # Cloud Run utilisera Gunicorn et ignorera cette section.
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
