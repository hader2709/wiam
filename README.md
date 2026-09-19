# Agent Telegram

Agent Telegram base sur Claude, reponses par webhook (pas de polling).

## Structure

- `main.py` — serveur FastAPI, recoit les updates Telegram via webhook.
- `agent.py` — appelle Claude (Anthropic) avec les outils, gere la boucle tool-use.
- `outils.py` — une fonction Python par capacite de l'agent (ex: envoi d'email).
- `instructions.md` — comportement / prompt systeme de l'agent, modifiable sans toucher au code.
- `.env` — cles secretes (jamais commit, voir `.env.example`).

## Installation locale

```bash
pip install -r requirements.txt
cp .env.example .env
```

Remplissez `.env` avec :
- `TELEGRAM_BOT_TOKEN` (obtenu via @BotFather sur Telegram)
- `TELEGRAM_WEBHOOK_SECRET` (chaine aleatoire de votre choix)
- `ANTHROPIC_API_KEY`
- `RESEND_API_KEY`, `NOTIFY_EMAIL_FROM`, `NOTIFY_EMAIL_TO`
- `GOOGLE_SERVICE_ACCOUNT_JSON`, `GOOGLE_SHEET_ID` (voir section Google Sheets ci-dessous)

```bash
uvicorn main:app --reload
```

En local, Telegram ne peut pas atteindre `localhost` : utilisez un tunnel
(ex: `ngrok http 8000`) puis `python definir_webhook.py https://xxxx.ngrok.app`
pour tester avant deploiement.

## Deploiement sur Render

1. Poussez ce dossier sur votre repo GitHub (deja fait si vous suivez ce README a jour).
2. Sur [render.com](https://render.com), "New +" -> "Web Service" -> connectez le repo GitHub.
3. Render detecte `render.yaml` (Blueprint) : build `pip install -r requirements.txt`,
   start `uvicorn main:app --host 0.0.0.0 --port $PORT`.
4. Dans l'onglet "Environment" du service Render, renseignez les variables
   marquees `sync: false` dans `render.yaml` (jamais le fichier `.env` lui-meme) :
   `TELEGRAM_BOT_TOKEN`, `TELEGRAM_WEBHOOK_SECRET`, `ANTHROPIC_API_KEY`,
   `RESEND_API_KEY`, `NOTIFY_EMAIL_FROM`, `NOTIFY_EMAIL_TO`,
   `GOOGLE_SERVICE_ACCOUNT_JSON`, `GOOGLE_SHEET_ID`.
5. Une fois deploye, recuperez l'URL publique Render puis, en local :
   ```bash
   python definir_webhook.py https://votre-app.onrender.com
   ```
   Cela indique a Telegram d'envoyer les messages sur
   `https://votre-app.onrender.com/webhook/<TELEGRAM_WEBHOOK_SECRET>`.

Note : le plan gratuit Render met le service en veille apres inactivite ; le
premier message apres une periode d'inactivite peut mettre quelques secondes
de plus a repondre le temps que le service redemarre.

## Google Sheets

Cet agent utilise un **compte de service Google** (pas d'OAuth interactif,
adapte a un serveur webhook) :

1. Sur [console.cloud.google.com](https://console.cloud.google.com), activez
   l'API "Google Sheets API", puis creez un compte de service
   (Credentials -> Create Credentials -> Service Account).
2. Generez une cle JSON pour ce compte (onglet "Keys" -> "Add Key" -> JSON).
3. Copiez le contenu du fichier JSON tel quel (sur une seule ligne) dans
   `GOOGLE_SERVICE_ACCOUNT_JSON`.
4. Partagez votre Google Sheet (bouton "Partager") avec l'adresse
   `client_email` presente dans ce JSON, en acces Editeur.
5. Renseignez `GOOGLE_SHEET_ID` avec l'identifiant de la feuille (dans son URL :
   `https://docs.google.com/spreadsheets/d/<ID>/edit`).

Capacites disponibles : ajouter une ligne, lire toutes les lignes, mettre a
jour une ligne selon une colonne/valeur de reference (voir `outils.py`).

## Ajouter une nouvelle capacite

1. Ecrire une fonction dans `outils.py`.
2. Ajouter sa description dans `TOOL_SCHEMAS`.
3. L'ajouter dans le dict `TOOL_FUNCTIONS`.

Aucune autre modification necessaire — `agent.py` et `main.py` restent inchanges.

## Changer le comportement / metier de l'agent

Modifiez uniquement `instructions.md`. C'est le prompt systeme envoye a Claude
a chaque message.

## Limite connue

L'historique de conversation est garde en memoire (par `chat_id`) et est donc
perdu a chaque redemarrage/redeploiement du service. Suffisant pour un agent
simple ; pour de la persistance, ajouter une base de donnees (ex: Redis,
Postgres) dans `agent.py`.
