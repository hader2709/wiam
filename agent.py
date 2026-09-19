"""
Logique de l'agent : appelle Claude avec les outils definis dans outils.py,
en utilisant instructions.md comme comportement (prompt systeme).
"""

import os
from pathlib import Path

import anthropic

from outils import TOOL_FUNCTIONS, TOOL_SCHEMAS

ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]
CLAUDE_MODEL = os.environ.get("CLAUDE_MODEL", "claude-sonnet-5")

_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

INSTRUCTIONS_PATH = Path(__file__).parent / "instructions.md"

# Historique de conversation par utilisateur Telegram (en memoire).
# Redemarre a chaque redeploiement : suffisant pour un agent simple.
_conversations: dict[int, list[dict]] = {}

MAX_TOURS_OUTILS = 5


def _lire_instructions() -> str:
    return INSTRUCTIONS_PATH.read_text(encoding="utf-8")


def repondre(chat_id: int, texte_utilisateur: str) -> str:
    """Traite un message utilisateur et renvoie la reponse texte de l'agent."""
    historique = _conversations.setdefault(chat_id, [])
    historique.append({"role": "user", "content": texte_utilisateur})

    for _ in range(MAX_TOURS_OUTILS):
        reponse = _client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=1024,
            system=_lire_instructions(),
            tools=TOOL_SCHEMAS,
            messages=historique,
        )

        historique.append({"role": "assistant", "content": reponse.content})

        if reponse.stop_reason != "tool_use":
            texte = "".join(
                bloc.text for bloc in reponse.content if bloc.type == "text"
            )
            return texte or "..."

        resultats_outils = []
        for bloc in reponse.content:
            if bloc.type != "tool_use":
                continue
            fonction = TOOL_FUNCTIONS.get(bloc.name)
            if fonction is None:
                resultat = f"Outil inconnu : {bloc.name}"
            else:
                try:
                    resultat = fonction(**bloc.input)
                except Exception as exc:
                    resultat = f"Erreur lors de l'execution de l'outil : {exc}"
            resultats_outils.append({
                "type": "tool_result",
                "tool_use_id": bloc.id,
                "content": str(resultat),
            })

        historique.append({"role": "user", "content": resultats_outils})

    return "Desole, je n'ai pas reussi a traiter votre demande."
