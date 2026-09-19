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
