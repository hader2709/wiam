"""
Outils disponibles pour l'agent : une fonction Python par capacite.

Pour ajouter une nouvelle capacite :
1. Ecrire une nouvelle fonction ici.
2. Ajouter sa description dans TOOL_SCHEMAS (format tool-use Anthropic).
3. L'ajouter au dict TOOL_FUNCTIONS.
Rien d'autre a modifier dans main.py ou agent.py.
"""

import os

import resend

RESEND_API_KEY = os.environ["RESEND_API_KEY"]
NOTIFY_EMAIL_FROM = os.environ["NOTIFY_EMAIL_FROM"]
NOTIFY_EMAIL_TO = os.environ["NOTIFY_EMAIL_TO"]

resend.api_key = RESEND_API_KEY


def envoyer_notification(sujet: str, message: str) -> str:
    """Envoie un email de notification a l'adresse fixe configuree dans .env."""
    resend.Emails.send({
        "from": NOTIFY_EMAIL_FROM,
        "to": NOTIFY_EMAIL_TO,
        "subject": sujet,
        "text": message,
    })
    return f"Notification envoyee a {NOTIFY_EMAIL_TO}."


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
]

TOOL_FUNCTIONS = {
    "envoyer_notification": envoyer_notification,
}
