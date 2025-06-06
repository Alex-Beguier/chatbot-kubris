from flask import Flask, request, jsonify, make_response
import json
from datetime import datetime
import logging
import os
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Templates de communication prédéfinis
COMMUNICATION_TEMPLATES = {
    "incident": {
        "title": "🚨 Communication d'incident",
        "messages": {
            "detection": "📢 **INCIDENT DÉTECTÉ**\n\n⚠️ Nous avons détecté un incident sur nos services.\n\n🔍 **Statut**: Investigation en cours\n⏰ **Heure de détection**: {timestamp}\n👥 **Équipes mobilisées**: Équipe technique\n\n📊 Nous vous tiendrons informés de l'évolution de la situation.",
            
            "investigation": "🔍 **MISE À JOUR - INVESTIGATION**\n\n📋 **Statut**: Investigation en cours\n⏰ **Dernière mise à jour**: {timestamp}\n\n🛠️ **Actions en cours**:\n• Analyse des logs système\n• Identification de la cause racine\n• Mobilisation des équipes techniques\n\n⏳ Prochaine mise à jour prévue dans 30 minutes.",
            
            "resolution": "✅ **INCIDENT RÉSOLU**\n\n🎉 L'incident a été résolu avec succès.\n\n📊 **Résumé**:\n• ⏰ Début: {start_time}\n• ⏰ Fin: {timestamp}\n• 🛠️ Cause: [À compléter]\n• 🔧 Solution: [À compléter]\n\n📈 Tous les services sont maintenant opérationnels.\n\n📋 Un rapport post-mortem sera publié dans les 48h."
        }
    },
    
    "mep": {
        "title": "🚀 Communication de mise en production",
        "messages": {
            "planned": "📅 **MISE EN PRODUCTION PLANIFIÉE**\n\n🚀 Une nouvelle version sera déployée.\n\n📋 **Détails**:\n• ⏰ **Date prévue**: {deployment_date}\n• ⏳ **Durée estimée**: 30 minutes\n• 🎯 **Impact**: Interruption de service possible\n\n✨ **Nouveautés**:\n• [À compléter - nouvelles fonctionnalités]\n• [À compléter - corrections de bugs]\n\n🔔 Nous vous préviendrons du début et de la fin de la maintenance.",
            
            "started": "🚀 **DÉPLOIEMENT EN COURS**\n\n⚙️ La mise en production a commencé.\n\n📊 **Statut**:\n• ⏰ **Début**: {timestamp}\n• 🎯 **Progression**: Déploiement en cours\n• ⏳ **Fin estimée**: {end_time}\n\n⚠️ Les services peuvent être temporairement indisponibles.\n\n📱 Suivez cette conversation pour les mises à jour.",
            
            "completed": "✅ **DÉPLOIEMENT TERMINÉ**\n\n🎉 La mise en production s'est déroulée avec succès !\n\n📊 **Résumé**:\n• ⏰ **Début**: {start_time}\n• ⏰ **Fin**: {timestamp}\n• ✅ **Statut**: Succès\n\n🌟 **Nouveautés disponibles**:\n• [À compléter - nouvelles fonctionnalités]\n\n📈 Tous les services sont opérationnels."
        }
    }
}

# Création de l'application Flask
app = Flask(__name__)

# Configuration de l'API Google Chat
SCOPES = ['https://www.googleapis.com/auth/chat.bot']
SERVICE_ACCOUNT_FILE = os.getenv('GOOGLE_APPLICATION_CREDENTIALS', 'service-account.json')

def get_timestamp():
    """Retourne un timestamp formaté"""
    return datetime.now().strftime("%d/%m/%Y à %H:%M")

def format_message(template, **kwargs):
    """Formate un message avec les variables fournies"""
    default_vars = {
        'timestamp': get_timestamp(),
        'start_time': get_timestamp(),
        'end_time': get_timestamp(),
        'deployment_date': get_timestamp()
    }
    default_vars.update(kwargs)
    return template.format(**default_vars)

def create_chat_response(text, thread_key=None, add_copy_option=True):
    """Crée une réponse formatée pour Google Chat avec options de copie et publication"""
    if add_copy_option:
        # Récupérer l'identifiant du salon à partir du thread_key
        space = thread_key.split('/threads/')[0] if thread_key else None
        
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
                                            },
                                            {
                                                "text": "📢 Publier le message",
                                                "onClick": {
                                                    "action": {
                                                        "function": "publish_message",
                                                        "parameters": [
                                                            {
                                                                "key": "text",
                                                                "value": text
                                                            },
                                                            {
                                                                "key": "space",
                                                                "value": space
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

def handle_incident_command(message_text, thread_name):
    """Traite les commandes d'incident"""
    parts = message_text.split()
    
    if len(parts) < 2:
        help_text = (
            "📋 **Commandes incident disponibles:**\n\n"
            "• `/incident detection` - Signaler un incident détecté\n"
            "• `/incident investigation` - Mise à jour de l'investigation\n"
            "• `/incident resolution` - Signaler la résolution de l'incident"
        )
        return create_chat_response(help_text, thread_name)
    
    subcommand = parts[1].lower()
    templates = COMMUNICATION_TEMPLATES["incident"]["messages"]
    
    if subcommand in templates:
        message = format_message(templates[subcommand])
        return create_chat_response(message, thread_name)
    else:
        return create_chat_response(
            f"❌ Sous-commande '{subcommand}' non reconnue. "
            "Utilisez: detection, investigation, ou resolution", 
            thread_name
        )

def handle_mep_command(message_text, thread_name):
    """Traite les commandes de mise en production"""
    parts = message_text.split()
    
    if len(parts) < 2:
        help_text = (
            "🚀 **Commandes MEP disponibles:**\n\n"
            "• `/mep planned` - Annoncer une MEP planifiée\n"
            "• `/mep started` - Signaler le début du déploiement\n"
            "• `/mep completed` - Signaler la fin du déploiement"
        )
        return create_chat_response(help_text, thread_name)
    
    subcommand = parts[1].lower()
    templates = COMMUNICATION_TEMPLATES["mep"]["messages"]
    
    if subcommand in templates:
        message = format_message(templates[subcommand])
        return create_chat_response(message, thread_name)
    else:
        return create_chat_response(
            f"❌ Sous-commande '{subcommand}' non reconnue. "
            "Utilisez: planned, started, ou completed", 
            thread_name
        )

def get_chat_service():
    """Initialise le service Google Chat"""
    try:
        credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        service = build('chat', 'v1', credentials=credentials)
        return service
    except Exception as e:
        logger.error(f"Erreur lors de l'initialisation du service Chat: {str(e)}")
        return None

@app.route('/', methods=['POST'])
def handle_chat_event():
    """Gestionnaire principal pour les événements Google Chat"""
    try:
        event = request.get_json()
        
        if not event:
            response = create_chat_response("Erreur: Aucune donnée reçue", None, False)
            return make_response(jsonify(response), 200)
        
        logger.info(f"Événement reçu: {json.dumps(event, indent=2)}")
        
        # Extraire le message et les informations de thread
        message_text = event.get('message', {}).get('text', '').strip()
        thread_name = event.get('message', {}).get('thread', {}).get('name')
        
        # Traiter les commandes slash
        if message_text.startswith('/incident'):
            response = handle_incident_command(message_text, thread_name)
        elif message_text.startswith('/mep'):
            response = handle_mep_command(message_text, thread_name)
        else:
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
            response = create_chat_response(help_text, thread_name)
        
        return make_response(jsonify(response), 200)
            
    except Exception as e:
        logger.error(f"Erreur dans handle_chat_event: {str(e)}")
        error_response = create_chat_response(f"❌ Erreur: {str(e)}", None, False)
        return make_response(jsonify(error_response), 200)

@app.route('/copy', methods=['POST'])
def copy_to_clipboard():
    """Retourne le texte à copier"""
    try:
        data = request.get_json()
        text = data.get('text')
        
        if not text:
            response = create_chat_response("❌ Erreur: Texte manquant", None, False)
            return make_response(jsonify(response), 200)
        
        response = create_chat_response("✅ Message copié ! Vous pouvez maintenant le coller dans le salon de votre choix.", None, False)
        return make_response(jsonify(response), 200)
        
    except Exception as e:
        logger.error(f"Erreur lors de la copie: {str(e)}")
        error_response = create_chat_response(f"❌ Erreur: {str(e)}", None, False)
        return make_response(jsonify(error_response), 200)

@app.route('/publish', methods=['POST'])
def publish_message():
    """Publie le message dans le salon"""
    try:
        data = request.get_json()
        text = data.get('text')
        space = data.get('space')  # L'identifiant du salon où publier
        
        if not text:
            response = create_chat_response("❌ Erreur: Texte manquant", None, False)
            return make_response(jsonify(response), 200)
            
        if not space:
            response = create_chat_response("❌ Erreur: Identifiant du salon manquant", None, False)
            return make_response(jsonify(response), 200)
        
        # Initialiser le service Google Chat
        chat_service = get_chat_service()
        if not chat_service:
            response = create_chat_response("❌ Erreur: Impossible de se connecter à l'API Google Chat", None, False)
            return make_response(jsonify(response), 200)
        
        try:
            # Créer le message à publier
            message = {'text': text}
            
            # Publier le message dans le salon
            result = chat_service.spaces().messages().create(
                parent=space,
                body=message
            ).execute()
            
            response = create_chat_response("✅ Message publié avec succès !", None, False)
            return make_response(jsonify(response), 200)
            
        except Exception as e:
            logger.error(f"Erreur lors de la publication du message: {str(e)}")
            response = create_chat_response(f"❌ Erreur lors de la publication: {str(e)}", None, False)
            return make_response(jsonify(response), 200)
        
    except Exception as e:
        logger.error(f"Erreur lors de la publication: {str(e)}")
        error_response = create_chat_response(f"❌ Erreur: {str(e)}", None, False)
        return make_response(jsonify(error_response), 200)

@app.route('/health', methods=['GET'])
def health_check():
    """Endpoint de santé pour Cloud Run"""
    return make_response(jsonify({
        "status": "healthy",
        "timestamp": get_timestamp()
    }), 200)

# Ne garder que la partie de développement
if __name__ == '__main__':
    # Configuration de développement uniquement
    app.debug = True
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

