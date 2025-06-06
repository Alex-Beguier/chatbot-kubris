import os
from datetime import datetime, date

from flask import Flask, request, jsonify
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Initialisation de l'application Flask
app = Flask(__name__)

# --- Configuration ---
SHEET_ID = os.environ.get("588026607")
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
# Nom exact de l'onglet de votre planning
SHEET_NAME = 'Equipe_KUBRIS 2025'

# Définition de la couleur "bleu d'astreinte"
# Correspond à la couleur bleu/gris clair (#d9e2f3) de votre planning
TARGET_BLUE_COLOR = {'red': 0.851, 'green': 0.886, 'blue': 0.953}

def is_color_close(color1, color2, tolerance=0.1):
    """Vérifie si deux couleurs sont similaires."""
    if not color1 or not color2:
        return False
    # L'API ne retourne pas toujours alpha, on l'ignore.
    return all(abs(color1.get(c, 0) - color2.get(c, 0)) < tolerance for c in ['red', 'green', 'blue'])

def parse_french_date(date_str):
    """Parse une date au format 'jj-Mois.-AAAA' (ex: '06-janv.-2025')."""
    month_map = {
        'janv.': '01', 'févr.': '02', 'mars': '03', 'avr.': '04', 'mai': '05', 'juin': '06',
        'juil.': '07', 'août': '08', 'sept.': '09', 'oct.': '10', 'nov.': '11', 'déc.': '12'
    }
    for month_fr, month_num in month_map.items():
        if month_fr in date_str:
            # Reconstitue une date au format 'jj-mm-AAAA'
            date_str_num = date_str.replace(month_fr, month_num).split(' ')[-1]
            return datetime.strptime(date_str_num, '%d-%m-%Y').date()
    return None

def get_on_call_engineer():
    """
    Se connecte au Google Sheet, trouve la ligne pour la date actuelle,
    puis cherche la cellule surlignée en bleu pour identifier l'ingénieur d'astreinte.
    """
    if not SHEET_ID:
        return "Erreur de configuration : la variable d'environnement SHEET_ID est manquante."

    try:
        creds = service_account.Credentials.from_service_account_info({}, scopes=SCOPES)
        service = build('sheets', 'v4', credentials=creds)
        
        # Requête pour récupérer les valeurs ET le formatage (couleurs)
        request = service.spreadsheets().get(
            spreadsheetId=SHEET_ID,
            ranges=[f'{SHEET_NAME}'],
            includeGridData=True
        )
        response = request.execute()
        
        # Accède aux données de la première feuille (onglet)
        grid_data = response['sheets'][0]['data'][0]
        rows_data = grid_data.get('rowData', [])
        
        # La ligne 2 (index 1) contient les noms des ingénieurs (en-têtes)
        if len(rows_data) < 2 or not rows_data[1].get('values'):
             return "Le planning est vide ou les en-têtes (ligne 2) sont manquants."
        header_row = [cell.get('formattedValue', '') for cell in rows_data[1].get('values', [])]

        today = date.today()
        # On parcourt les lignes de données (en sautant les 3 premières lignes d'en-tête)
        for row_data in rows_data[3:]:
            cells = row_data.get('values', [])
            # La date est dans la colonne B (index 1)
            if not cells or len(cells) < 2 or not cells[1].get('formattedValue'):
                continue
            
            date_str = cells[1].get('formattedValue')
            current_row_date = parse_french_date(date_str)

            if current_row_date and current_row_date == today:
                # C'est la bonne journée, cherchons la cellule bleue
                for col_index, cell_data in enumerate(cells):
                    bg_color = cell_data.get('effectiveFormat', {}).get('backgroundColor')
                    
                    if bg_color and all(k in bg_color for k in ['red', 'green', 'blue']):
                        if is_color_close(bg_color, TARGET_BLUE_COLOR):
                            # La colonne de l'ingénieur correspond à l'index de la cellule
                            if col_index < len(header_row):
                                engineer_name = header_row[col_index]
                                return f"Aujourd'hui, la personne d'astreinte est : **{engineer_name}**."
                
                return f"J'ai trouvé la date du jour ({today.strftime('%d/%m/%Y')}), mais aucune astreinte (cellule bleue) n'est définie."

        return f"Je n'ai pas trouvé la date d'aujourd'hui ({today.strftime('%d/%m/%Y')}) dans le planning."

    except Exception as e:
        print(f"Une erreur est survenue: {e}")
        return "Désolé, une erreur technique m'empêche de consulter le planning."

@app.route('/', methods=['POST'])
def handle_chat_event():
    """Point d'entrée principal qui reçoit les événements de Google Chat."""
    event_data = request.get_json()

    if event_data and event_data['type'] == 'MESSAGE':
        response_text = get_on_call_engineer()
        return jsonify({'text': response_text})

    return jsonify({})

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

