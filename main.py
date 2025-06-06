from flask import Flask, request, jsonify
import json
from datetime import datetime
import logging
from google.auth import default
from google.auth.transport.requests import AuthorizedSession
import os

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_app():
    """Fonction de création de l'application Flask"""
    app = Flask(__name__)
    
    # Configuration des salons Google Chat
    # Format des IDs :
    # - Dans l'URL du salon : https://chat.google.com/space/AAAAxxxxxx
    # - ID à utiliser : space/AAAAxxxxxx
    app.config['AVAILABLE_SPACES'] = {
        "prod": "AAAAOA17Cos",      # Sans le préfixe space/
        "urgent": "AAAAOA17Cos"     # Sans le préfixe space/
    }
    
    def get_google_chat_session():
        """Crée une session authentifiée pour l'API Google Chat en utilisant les credentials Cloud Run"""
        try:
            credentials, project = default()
            credentials.refresh_token = None
            return AuthorizedSession(credentials)
        except Exception as e:
            logger.error(f"Erreur d'authentification Google: {str(e)}")
            return None

    def send_message_to_space(space_id, message):
        """Envoie un message dans un salon Google Chat spécifique"""
        try:
            session = get_google_chat_session()
            if not session:
                raise Exception("Impossible d'établir une session authentifiée avec Google Chat")

            # Construction de l'URL complète
            base_url = "https://chat.googleapis.com/v1"
            # Si space_id commence déjà par 'space/', on l'utilise tel quel
            if not space_id.startswith('space/'):
                space_id = f"space/{space_id}"
            
            url = f"{base_url}/{space_id}/messages"
            
            logger.info(f"Envoi du message vers l'espace: {space_id}")
            logger.info(f"URL de l'API: {url}")
            
            payload = {
                "text": message,
                "space": space_id
            }
            
            logger.info(f"Payload: {json.dumps(payload, indent=2)}")
            
            response = session.post(url, json=payload)
            
            logger.info(f"Statut de la réponse: {response.status_code}")
            logger.info(f"Réponse: {response.text}")
            
            if response.status_code != 200:
                raise Exception(f"Erreur lors de l'envoi du message: {response.text}")
            
            return response.json()
        except Exception as e:
            logger.error(f"Erreur dans send_message_to_space: {str(e)}")
            raise

    def create_chat_response(text, thread_key=None, add_publish_option=True):
        """Crée une réponse formatée pour Google Chat avec option de republication"""
        if add_publish_option:
            response = {
                "cardsV2": [{
                    "cardId": "message_card",
                    "card": {
                        "sections": [
                            {
                                "header": "Message",
                                "collapsible": False,
                                "uncollapsibleWidgetsCount": 1,
                                "widgets": [
                                    {
                                        "textParagraph": {
                                            "text": text
                                        }
                                    }
                                ]
                            },
                            {
                                "header": "Actions",
                                "collapsible": False,
                                "widgets": [
                                    {
                                        "buttonList": {
                                            "buttons": [
                                                {
                                                    "text": "Publier en Production",
                                                    "onClick": {
                                                        "action": {
                                                            "function": "publish_message",
                                                            "parameters": [
                                                                {
                                                                    "key": "target_space",
                                                                    "value": "prod"
                                                                },
                                                                {
                                                                    "key": "message",
                                                                    "value": text
                                                                }
                                                            ]
                                                        }
                                                    }
                                                },
                                                {
                                                    "text": "Publier en Urgent",
                                                    "onClick": {
                                                        "action": {
                                                            "function": "publish_message",
                                                            "parameters": [
                                                                {
                                                                    "key": "target_space",
                                                                    "value": "urgent"
                                                                },
                                                                {
                                                                    "key": "message",
                                                                    "value": text
                                                                }
                                                            ]
                                                        }
                                                    }
                                                }
                                            ]
                                        }
                                    }
                                ]
                            }
                        ]
                    }
                }]
            }
        else:
            response = {"text": text}

        if thread_key:
            response["thread"] = {"name": thread_key}
        
        return response

    @app.route('/', methods=['POST'])
    def handle_chat_event():
        """Gestionnaire principal pour les événements Google Chat"""
        try:
            event = request.get_json()
            
            if not event:
                return jsonify({"text": "Erreur: Aucune donnée reçue"})
            
            logger.info(f"Événement reçu: {json.dumps(event, indent=2)}")
            
            # Extraire le message et les informations de thread
            message_text = event.get('message', {}).get('text', '').strip()
            thread_name = event.get('message', {}).get('thread', {}).get('name')
            
            help_text = (
                "🤖 **Commandes disponibles:**\n\n"
                "**📋 Incidents:**\n"
                "• `/incident detection` - Signaler un incident\n"
                "• `/incident investigation` - Mise à jour investigation\n"
                "• `/incident resolution` - Signaler la résolution\n\n"
                "**🚀 Mises en production:**\n"
                "• `/mep planned` - Annoncer une MEP planifiée\n"
                "• `/mep started` - Signaler le début du déploiement\n"
                "• `/mep completed` - Signaler la fin du déploiement\n\n"
                "💡 *Tapez une commande pour obtenir le message correspondant.*"
            )
            return jsonify(create_chat_response(help_text, thread_name))
                
        except Exception as e:
            logger.error(f"Erreur dans handle_chat_event: {str(e)}")
            return jsonify({"text": f"❌ Erreur: {str(e)}"})

    @app.route('/publish', methods=['POST'])
    def publish_message():
        """Gère la republication d'un message dans un autre salon"""
        try:
            data = request.get_json()
            target_space = data.get('target_space')
            message = data.get('message')
            
            logger.info(f"Tentative de publication dans l'espace: {target_space}")
            logger.info(f"Message à publier: {message}")
            
            if not target_space or not message:
                return jsonify({"text": "❌ Erreur: Paramètres manquants"})
            
            space_id = app.config['AVAILABLE_SPACES'].get(target_space)
            if not space_id:
                return jsonify({"text": "❌ Erreur: Salon non reconnu"})
            
            logger.info(f"ID du salon cible: {space_id}")
            
            # Envoi du message dans le salon cible
            result = send_message_to_space(space_id, message)
            
            return jsonify({
                "text": f"✅ Message publié avec succès dans le salon {target_space}"
            })
            
        except Exception as e:
            logger.error(f"Erreur lors de la publication: {str(e)}")
            return jsonify({"text": f"❌ Erreur lors de la publication: {str(e)}"})

    @app.route('/health', methods=['GET'])
    def health_check():
        """Endpoint de santé pour Cloud Run"""
        return jsonify({
            "status": "healthy",
            "timestamp": datetime.now().strftime("%d/%m/%Y à %H:%M")
        })

    return app

# Création de l'instance de l'application
app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

