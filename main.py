# Fichier : main.py
# -----------------------------------------------------------------------------
# Ce fichier contient une application web Flask qui agit comme le backend
# pour notre chatbot Google Chat.

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

    if not request_json:
        # Si la requête n'est pas un JSON valide, on renvoie une erreur.
        return {"text": "Erreur: requête invalide."}

    event_type = request_json['type']
    response_data = {}

    # Cas 1: L'utilisateur envoie un message ou une commande slash
    if event_type == 'MESSAGE':
        message = request_json.get('message', {})
        command = ""
        
        if message.get('slashCommand'):
            # Méthode préférée : utiliser les commandes slash
            command = message['slashCommand']['commandName'].lower()
        else:
            # Alternative : lire le texte du message
            command = message.get('text', '').lower().strip()
        
        if 'incident' in command:
            response_data = create_incident_form_card()
        elif 'mep' in command:
            response_data = create_mep_form_card()
        else:
            response_data = {"text": "Bonjour ! Utilisez `/incident` ou `/mep` pour démarrer."}

    # Cas 2: L'utilisateur clique sur un bouton dans une carte interactive
    elif event_type == 'CARD_CLICKED':
        action = request_json['common']['invokedFunction']
        form_values = request_json.get('common', {}).get('formInputs', {})

        if action == 'generateIncidentMessage':
            # Extraction des valeurs du formulaire d'incident
            cluster = form_values.get('cluster', {}).get('stringInputs', {}).get('value', ['N/A'])[0]
            start_date = form_values.get('startDate', {}).get('stringInputs', {}).get('value', ['N/A'])[0]
            status = form_values.get('status', {}).get('stringInputs', {}).get('value', ['N/A'])[0]
            services = form_values.get('services', {}).get('stringInputs', {}).get('value', ['N/A'])[0]

            final_message = (
                f"🚨 [{cluster}] Incident 🚨\n"
                f"🗓️ Depuis {start_date}\n"
                f"{status}\n"
                f"💥 Les services tels que {services} sont actuellement impactés."
            )
            
            # Réponse pour poster un nouveau message public
            response_data = {
                "actionResponse": {"type": "NEW_MESSAGE", "message": {"text": final_message}}
            }
        
        elif action == 'generateMepMessage':
            # Extraction des valeurs du formulaire de MEP
            component = form_values.get('component', {}).get('stringInputs', {}).get('value', ['N/A'])[0]
            date = form_values.get('date', {}).get('stringInputs', {}).get('value', ['N/A'])[0]
            target = form_values.get('target', {}).get('stringInputs', {}).get('value', ['N/A'])[0]
            impact = form_values.get('impact', {}).get('stringInputs', {}).get('value', ['Sans impact'])[0]
            mep_number = form_values.get('mepNumber', {}).get('stringInputs', {}).get('value', ['N/A'])[0]
            
            final_message = (
                f"ℹ️ [{component}] Mise à jour de l’OS sous-jacent (Production)\n"
                f"📅 Le {date}\n"
                f"🎯 {target}\n"
                f"💥 {impact}\n"
                f"🏷️{mep_number}"
            )
            response_data = {
                "actionResponse": {"type": "NEW_MESSAGE", "message": {"text": final_message}}
            }

    # Flask convertit automatiquement le dictionnaire en une réponse JSON
    return response_data

def create_incident_form_card():
    """Construit et retourne la carte interactive pour un incident."""
    return {
        "cardsV2": [{"cardId": "incidentForm", "card": {"header": {"title": "Déclarer un nouvel incident"}, "sections": [{"widgets": [{"textInput": {"label": "Cluster / Application", "name": "cluster"}}, {"textInput": {"label": "Date et heure de début", "name": "startDate", "value": "Mardi 03/06/2025 13h00"}}, {"textInput": {"label": "Description de la situation", "name": "status", "value": "L'origine du problème a été identifiée et est en cours de correction"}}, {"textInput": {"label": "Services impactés (séparés par /)", "name": "services", "value": "ArgoCD / Octoperf / SonarKube"}}, {"buttonList": {"buttons": [{"text": "Générer le message", "onClick": {"action": {"function": "generateIncidentMessage"}}}]}}]}}]}]
    }

def create_mep_form_card():
    """Construit et retourne la carte interactive pour une MEP."""
    return {
        "cardsV2": [{"cardId": "mepForm", "card": {"header": {"title": "Annoncer une Mise en Production"}, "sections": [{"widgets": [{"textInput": {"label": "Composant principal", "name": "component", "value": "VAULT"}}, {"textInput": {"label": "Date et créneau", "name": "date", "value": "10/06 12h-14h"}}, {"textInput": {"label": "Cible", "name": "target", "value": "Vault Production"}}, {"textInput": {"label": "Impact", "name": "impact", "value": "Sans impact, sauf en cas de retour arrière"}}, {"textInput": {"label": "Numéro de MEP", "name": "mepNumber", "value": "MEP0000866105"}}, {"buttonList": {"buttons": [{"text": "Générer le message", "onClick": {"action": {"function": "generateMepMessage"}}}]}}]}}]}]
    }

if __name__ == "__main__":
    # Cette partie est utile pour tester le serveur localement.
    # Cloud Run utilisera Gunicorn et ignorera cette section.
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))