"""
Outils disponibles pour l'agent : une fonction Python par capacite.

Pour ajouter une nouvelle capacite :
1. Ecrire une nouvelle fonction ici.
2. Ajouter sa description dans TOOL_SCHEMAS (format tool-use Anthropic).
3. L'ajouter au dict TOOL_FUNCTIONS.
Rien d'autre a modifier dans main.py ou agent.py.
"""

import json
import os

import gspread
import resend
from google.oauth2.service_account import Credentials

GOOGLE_SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
]


def _feuille_google():
    """Retourne le premier onglet de la Google Sheet configuree, ou None si absent."""
    creds_json = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")
    sheet_id = os.environ.get("GOOGLE_SHEET_ID")
    if not (creds_json and sheet_id):
        return None
    creds_info = json.loads(creds_json)
    creds = Credentials.from_service_account_info(creds_info, scopes=GOOGLE_SCOPES)
    client = gspread.authorize(creds)
    return client.open_by_key(sheet_id).sheet1


def envoyer_notification(sujet: str, message: str) -> str:
    """Envoie un email de notification a l'adresse fixe configuree dans .env."""
    api_key = os.environ.get("RESEND_API_KEY")
    email_from = os.environ.get("NOTIFY_EMAIL_FROM")
    email_to = os.environ.get("NOTIFY_EMAIL_TO")

    if not (api_key and email_from and email_to):
        return (
            "Notification impossible : RESEND_API_KEY, NOTIFY_EMAIL_FROM "
            "et/ou NOTIFY_EMAIL_TO ne sont pas configures cote serveur."
        )

    resend.api_key = api_key
    resend.Emails.send({
        "from": email_from,
        "to": email_to,
        "subject": sujet,
        "text": message,
    })
    return f"Notification envoyee a {email_to}."


def ajouter_ligne_sheet(valeurs: list) -> str:
    """Ajoute une nouvelle ligne a la fin de la Google Sheet configuree."""
    feuille = _feuille_google()
    if feuille is None:
        return (
            "Google Sheets non configure : GOOGLE_SERVICE_ACCOUNT_JSON et/ou "
            "GOOGLE_SHEET_ID sont absents cote serveur."
        )
    feuille.append_row(valeurs)
    return f"Ligne ajoutee : {valeurs}"


def lire_donnees_sheet() -> str:
    """Lit toutes les lignes de la Google Sheet configuree."""
    feuille = _feuille_google()
    if feuille is None:
        return (
            "Google Sheets non configure : GOOGLE_SERVICE_ACCOUNT_JSON et/ou "
            "GOOGLE_SHEET_ID sont absents cote serveur."
        )
    lignes = feuille.get_all_values()
    return json.dumps(lignes, ensure_ascii=False)


def mettre_a_jour_ligne_sheet(colonne_critere: str, valeur_critere: str, nouvelles_valeurs: list) -> str:
    """
    Cherche la ligne dont la colonne `colonne_critere` vaut `valeur_critere`
    (colonne identifiee par son en-tete en premiere ligne) et remplace son
    contenu par `nouvelles_valeurs`.
    """
    feuille = _feuille_google()
    if feuille is None:
        return (
            "Google Sheets non configure : GOOGLE_SERVICE_ACCOUNT_JSON et/ou "
            "GOOGLE_SHEET_ID sont absents cote serveur."
        )

    en_tetes = feuille.row_values(1)
    if colonne_critere not in en_tetes:
        return f"Colonne '{colonne_critere}' introuvable dans l'en-tete : {en_tetes}"

    index_colonne = en_tetes.index(colonne_critere)
    toutes_les_lignes = feuille.get_all_values()[1:]  # sans l'en-tete

    for position, ligne in enumerate(toutes_les_lignes, start=2):  # ligne 1 = en-tete
        if index_colonne < len(ligne) and ligne[index_colonne] == str(valeur_critere):
            feuille.update(f"A{position}", [nouvelles_valeurs])
            return f"Ligne {position} mise a jour : {nouvelles_valeurs}"

    return f"Aucune ligne trouvee ou '{colonne_critere}' = '{valeur_critere}'."


TOOL_SCHEMAS = [
    {
        "name": "envoyer_notification",
        "description": (
            "Envoie un email de notification/alerte a l'adresse fixe "
            "configuree pour cet agent. A utiliser uniquement quand "
            "l'utilisateur demande explicitement d'etre notifie ou alerte."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "sujet": {
                    "type": "string",
                    "description": "Objet court de l'email.",
                },
                "message": {
                    "type": "string",
                    "description": "Contenu du message a envoyer.",
                },
            },
            "required": ["sujet", "message"],
        },
    },
    {
        "name": "ajouter_ligne_sheet",
        "description": (
            "Ajoute une nouvelle ligne a la fin de la Google Sheet configuree "
            "pour cet agent."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "valeurs": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Valeurs de la ligne, dans l'ordre des colonnes.",
                },
            },
            "required": ["valeurs"],
        },
    },
    {
        "name": "lire_donnees_sheet",
        "description": (
            "Lit toutes les lignes (avec en-tetes) de la Google Sheet "
            "configuree pour cet agent."
        ),
        "input_schema": {
            "type": "object",
            "properties": {},
        },
    },
    {
        "name": "mettre_a_jour_ligne_sheet",
        "description": (
            "Met a jour la ligne de la Google Sheet dont une colonne "
            "(identifiee par son en-tete) correspond a une valeur donnee."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "colonne_critere": {
                    "type": "string",
                    "description": "En-tete de la colonne servant a identifier la ligne.",
                },
                "valeur_critere": {
                    "type": "string",
                    "description": "Valeur recherchee dans cette colonne.",
                },
                "nouvelles_valeurs": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Nouvelles valeurs de la ligne, dans l'ordre des colonnes.",
                },
            },
            "required": ["colonne_critere", "valeur_critere", "nouvelles_valeurs"],
        },
    },
]

TOOL_FUNCTIONS = {
    "envoyer_notification": envoyer_notification,
    "ajouter_ligne_sheet": ajouter_ligne_sheet,
    "lire_donnees_sheet": lire_donnees_sheet,
    "mettre_a_jour_ligne_sheet": mettre_a_jour_ligne_sheet,
}
