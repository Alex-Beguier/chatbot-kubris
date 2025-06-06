"""Configuration des templates de messages"""

# Vous pouvez modifier ces templates selon vos besoins
CUSTOM_TEMPLATES = {
    "incident": {
        "detection": {
            "title": "Incident détecté",
            "emoji": "🚨",
            "priority": "high",
            "template": "📢 **INCIDENT DÉTECTÉ**\n\n⚠️ Nous avons détecté un incident sur nos services.\n\n🔍 **Statut**: Investigation en cours\n⏰ **Heure de détection**: {timestamp}\n👥 **Équipes mobilisées**: Équipe technique\n\n📊 Nous vous tiendrons informés de l'évolution de la situation."
        },
        "investigation": {
            "title": "Investigation en cours",
            "emoji": "🔍",
            "priority": "medium",
            "template": "🔍 **MISE À JOUR - INVESTIGATION**\n\n📋 **Statut**: Investigation en cours\n⏰ **Dernière mise à jour**: {timestamp}\n\n🛠️ **Actions en cours**:\n• Analyse des logs système\n• Identification de la cause racine\n• Mobilisation des équipes techniques\n\n⏳ Prochaine mise à jour prévue dans 30 minutes."
        },
        "resolution": {
            "title": "Incident résolu",
            "emoji": "✅",
            "priority": "low",
            "template": "✅ **INCIDENT RÉSOLU**\n\n🎉 L'incident a été résolu avec succès.\n\n📊 **Résumé**:\n• ⏰ Début: {start_time}\n• ⏰ Fin: {timestamp}\n• 🛠️ Cause: [À compléter]\n• 🔧 Solution: [À compléter]\n\n📈 Tous les services sont maintenant opérationnels.\n\n📋 Un rapport post-mortem sera publié dans les 48h."
        }
    },
    "mep": {
        "planned": {
            "title": "MEP planifiée",
            "emoji": "📅",
            "priority": "medium",
            "template": "📅 **MISE EN PRODUCTION PLANIFIÉE**\n\n🚀 Une nouvelle version sera déployée.\n\n📋 **Détails**:\n• ⏰ **Date prévue**: {deployment_date}\n• ⏳ **Durée estimée**: 30 minutes\n• 🎯 **Impact**: Interruption de service possible\n\n✨ **Nouveautés**:\n• [À compléter - nouvelles fonctionnalités]\n• [À compléter - corrections de bugs]\n\n🔔 Nous vous préviendrons du début et de la fin de la maintenance."
        },
        "started": {
            "title": "Déploiement en cours",
            "emoji": "🚀",
            "priority": "high",
            "template": "🚀 **DÉPLOIEMENT EN COURS**\n\n⚙️ La mise en production a commencé.\n\n📊 **Statut**:\n• ⏰ **Début**: {timestamp}\n• 🎯 **Progression**: Déploiement en cours\n• ⏳ **Fin estimée**: {end_time}\n\n⚠️ Les services peuvent être temporairement indisponibles.\n\n📱 Suivez cette conversation pour les mises à jour."
        },
        "completed": {
            "title": "Déploiement terminé",
            "emoji": "✅",
            "priority": "low",
            "template": "✅ **DÉPLOIEMENT TERMINÉ**\n\n🎉 La mise en production s'est déroulée avec succès !\n\n📊 **Résumé**:\n• ⏰ **Début**: {start_time}\n• ⏰ **Fin**: {timestamp}\n• ✅ **Statut**: Succès\n\n🌟 **Nouveautés disponibles**:\n• [À compléter - nouvelles fonctionnalités]\n\n📈 Tous les services sont opérationnels."
        }
    }
}

# Configuration générale
APP_CONFIG = {
    "timezone": "Europe/Paris",
    "date_format": "%d/%m/%Y à %H:%M",
    "log_level": "INFO",
    "max_message_length": 4000
}

