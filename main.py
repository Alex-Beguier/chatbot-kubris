from flask import Flask, request, jsonify
import json
from datetime import datetime
import logging
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

    def create_chat_response(text, thread_key=None, add_copy_option=True):
        """Crée une réponse formatée pour Google Chat avec option de copie"""
        if add_copy_option:
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
                                                    "text": "📋 Copier le message",
                                                    "onClick": {
                                                        "action": {
                                                            "function": "copy_to_clipboard",
                                                            "parameters": [
                                                                {
                                                                    "key": "text",
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

    @app.route('/copy', methods=['POST'])
    def copy_to_clipboard():
        """Retourne le texte à copier"""
        try:
            data = request.get_json()
            text = data.get('text')
            
            if not text:
                return jsonify({"text": "❌ Erreur: Texte manquant"})
            
            return jsonify({
                "text": "✅ Message copié ! Vous pouvez maintenant le coller dans le salon de votre choix."
            })
            
        except Exception as e:
            logger.error(f"Erreur lors de la copie: {str(e)}")
            return jsonify({"text": f"❌ Erreur: {str(e)}"})

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

