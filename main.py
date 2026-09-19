"""
Point d'entree FastAPI : recoit les updates Telegram par webhook
(pas de polling / boucle d'attente) et fait repondre l'agent.
"""

import os

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, Request

load_dotenv()

from agent import repondre  # noqa: E402  (doit venir apres load_dotenv)

TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
TELEGRAM_WEBHOOK_SECRET = os.environ["TELEGRAM_WEBHOOK_SECRET"]
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"

app = FastAPI()


@app.get("/")
def health():
    return {"status": "ok"}


@app.post(f"/webhook/{TELEGRAM_WEBHOOK_SECRET}")
async def webhook(request: Request):
    update = await request.json()

    message = update.get("message")
    if not message or "text" not in message:
        return {"ok": True}

    chat_id = message["chat"]["id"]
    texte = message["text"]

    reponse = repondre(chat_id, texte)

    async with httpx.AsyncClient() as client:
        await client.post(
            f"{TELEGRAM_API_URL}/sendMessage",
            json={"chat_id": chat_id, "text": reponse},
        )

    return {"ok": True}
