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

def create_app():
    """Fonction de création de l'application Flask"""
    app = Flask(__name__)

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
            return jsonify(create_chat_response(help_text, thread_name))
        
        subcommand = parts[1].lower()
        templates = COMMUNICATION_TEMPLATES["incident"]["messages"]
        
        if subcommand in templates:
            message = format_message(templates[subcommand])
            return jsonify(create_chat_response(message, thread_name))
        else:
            return jsonify(create_chat_response(
                f"❌ Sous-commande '{subcommand}' non reconnue. "
                "Utilisez: detection, investigation, ou resolution", 
                thread_name
            ))

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
            return jsonify(create_chat_response(help_text, thread_name))
        
        subcommand = parts[1].lower()
        templates = COMMUNICATION_TEMPLATES["mep"]["messages"]
        
        if subcommand in templates:
            message = format_message(templates[subcommand])
            return jsonify(create_chat_response(message, thread_name))
        else:
            return jsonify(create_chat_response(
                f"❌ Sous-commande '{subcommand}' non reconnue. "
                "Utilisez: planned, started, ou completed", 
                thread_name
            ))

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
            
            # Traiter les commandes slash
            if message_text.startswith('/incident'):
                return handle_incident_command(message_text, thread_name)
            elif message_text.startswith('/mep'):
                return handle_mep_command(message_text, thread_name)
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

