from flask import Flask, request, jsonify
import functions_framework
from datetime import datetime

# Templates de communication
TEMPLATES = {
    "incident": {
        "detection": {
            "title": "🚨 Incident Détecté",
            "text": """🚨 **INCIDENT DÉTECTÉ**

⚠️ Un incident a été détecté sur nos services.

📊 **Statut**: Investigation en cours
⏰ **Heure de détection**: {timestamp}
👥 **Équipes mobilisées**: Équipe technique

📱 Nous vous tiendrons informés de l'évolution de la situation."""
        },
        "investigation": {
            "title": "🔍 Investigation en Cours",
            "text": """🔍 **MISE À JOUR - INVESTIGATION**

📋 **Statut**: Investigation en cours
⏰ **Dernière mise à jour**: {timestamp}

🛠️ **Actions en cours**:
• Analyse des logs système
• Identification de la cause racine
• Mobilisation des équipes techniques

⏳ Une mise à jour sera fournie dans les 30 minutes."""
        },
        "resolution": {
            "title": "✅ Incident Résolu",
            "text": """✅ **INCIDENT RÉSOLU**

🎉 L'incident a été résolu avec succès.

📊 **Résumé**:
• ⏰ Début: {start_time}
• ⏰ Fin: {timestamp}
• 🛠️ Cause: {cause}
• 🔧 Solution: {solution}

📈 Tous les services sont maintenant opérationnels.
📋 Un rapport détaillé sera publié dans les prochaines 48h."""
        }
    },
    "mep": {
        "planned": {
            "title": "📅 MEP Planifiée",
            "text": """📅 **MISE EN PRODUCTION PLANIFIÉE**

🚀 Une nouvelle version sera déployée prochainement.

📋 **Détails**:
• ⏰ **Date prévue**: {planned_date}
• ⏳ **Durée estimée**: {estimated_duration}
• 🎯 **Impact**: {impact}

✨ **Nouveautés**:
{changes}

🔔 Vous serez informés du début et de la fin de l'opération."""
        },
        "started": {
            "title": "🚀 MEP en Cours",
            "text": """🚀 **DÉPLOIEMENT EN COURS**

⚙️ La mise en production a débuté.

📊 **Statut**:
• ⏰ **Début**: {timestamp}
• 🎯 **Progression**: En cours
• ⏳ **Fin estimée**: {estimated_end}

⚠️ Certains services peuvent être temporairement perturbés.
📱 Vous serez notifiés à la fin de l'opération."""
        },
        "completed": {
            "title": "✅ MEP Terminée",
            "text": """✅ **DÉPLOIEMENT TERMINÉ**

🎉 La mise en production s'est déroulée avec succès !

📊 **Résumé**:
• ⏰ **Début**: {start_time}
• ⏰ **Fin**: {timestamp}
• ✅ **Statut**: Succès

🌟 **Nouveautés déployées**:
{changes}

📈 Tous les services sont pleinement opérationnels."""
        }
    }
}

def get_timestamp():
    """Retourne l'horodatage au format français"""
    return datetime.now().strftime("%d/%m/%Y à %H:%M")

def create_card_response(title, text):
    """Crée une réponse formatée pour Google Chat avec bouton de copie"""
    return {
        "cardsV2": [
            {
                "cardId": "unique-card-id",
                "card": {
                    "header": {
                        "title": title,
                        "imageUrl": None,
                        "imageType": "CIRCLE"
                    },
                    "sections": [
                        {
                            "widgets": [
                                {
                                    "textParagraph": {
                                        "text": text
                                    }
                                }
                            ]
                        },
                        {
                            "widgets": [
                                {
                                    "decoratedText": {
                                        "text": text,
                                        "button": {
                                            "text": "📋 Copier",
                                            "onClick": {
                                                "action": {
                                                    "actionMethodName": "copyToClipboard"
                                                }
                                            }
                                        }
                                    }
                                }
                            ]
                        }
                    ]
                }
            }
        ]
    }

@functions_framework.http
def handle_chat_webhook(request):
    """Point d'entrée principal pour les webhooks Google Chat"""
    if request.method != 'POST':
        return 'Méthode non autorisée', 405

    data = request.get_json()
    if not data:
        return 'Requête invalide', 400

    message = data.get('message', {})
    text = message.get('text', '').lower().strip()
    
    # Gestion des commandes
    if text.startswith('/incident'):
        parts = text.split()
        if len(parts) < 2:
            # Afficher l'aide pour la commande incident
            help_text = """🚨 **Commandes Incident disponibles:**

• `/incident detection` - Signaler un nouvel incident
• `/incident investigation` - Mise à jour de l'investigation
• `/incident resolution` - Marquer l'incident comme résolu

Exemple: `/incident detection`"""
            return jsonify(create_card_response("Aide - Commandes Incident", help_text))

        command = parts[1]
        if command in TEMPLATES['incident']:
            template = TEMPLATES['incident'][command]
            formatted_text = template['text'].format(
                timestamp=get_timestamp(),
                start_time=get_timestamp(),
                cause="[À compléter]",
                solution="[À compléter]"
            )
            return jsonify(create_card_response(template['title'], formatted_text))

    elif text.startswith('/mep'):
        parts = text.split()
        if len(parts) < 2:
            # Afficher l'aide pour la commande MEP
            help_text = """🚀 **Commandes MEP disponibles:**

• `/mep planned` - Annoncer une MEP planifiée
• `/mep started` - Signaler le début du déploiement
• `/mep completed` - Marquer la MEP comme terminée

Exemple: `/mep planned`"""
            return jsonify(create_card_response("Aide - Commandes MEP", help_text))

        command = parts[1]
        if command in TEMPLATES['mep']:
            template = TEMPLATES['mep'][command]
            formatted_text = template['text'].format(
                timestamp=get_timestamp(),
                planned_date="[Date à définir]",
                estimated_duration="30 minutes",
                impact="Impact minimal attendu",
                changes="• [Nouvelles fonctionnalités à lister]\n• [Corrections à lister]",
                estimated_end=get_timestamp(),
                start_time=get_timestamp()
            )
            return jsonify(create_card_response(template['title'], formatted_text))

    # Message d'aide par défaut
    help_text = """🤖 **Bot de Communication**

**Commandes disponibles:**

🚨 **Incidents:**
• `/incident detection` - Signaler un incident
• `/incident investigation` - Mise à jour investigation
• `/incident resolution` - Marquer comme résolu

🚀 **MEP:**
• `/mep planned` - Annoncer une MEP
• `/mep started` - Début du déploiement
• `/mep completed` - Fin du déploiement

Tapez une commande pour obtenir le template correspondant."""

    return jsonify(create_card_response("Aide - Commandes Disponibles", help_text)) 