"""
Script a executer une fois apres deploiement pour indiquer a Telegram
ou envoyer les updates (URL publique Railway + secret).

Usage :
    python definir_webhook.py https://votre-app.up.railway.app
"""

import os
import sys

import httpx
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
TELEGRAM_WEBHOOK_SECRET = os.environ["TELEGRAM_WEBHOOK_SECRET"]

if len(sys.argv) != 2:
    print("Usage: python definir_webhook.py https://votre-app.up.railway.app")
    sys.exit(1)

base_url = sys.argv[1].rstrip("/")
webhook_url = f"{base_url}/webhook/{TELEGRAM_WEBHOOK_SECRET}"

reponse = httpx.post(
    f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/setWebhook",
    json={"url": webhook_url},
)
print(reponse.json())
