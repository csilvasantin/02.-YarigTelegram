"""Bot individual de consejero — cada silla del consejo es un bot de Telegram."""

from __future__ import annotations

import json
import logging
from pathlib import Path

import aiohttp
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from src.config import (
    CONSEJO_USE_LLM,
    CONSEJO_LLM_API_URL,
    CONSEJO_LLM_API_KEY,
    CONSEJO_LLM_MODEL,
    CONSEJO_MAX_RESPONSE_LENGTH,
)
from src.actas import save_acta, get_context_for_llm

logger = logging.getLogger(__name__)


# ── Perfil del consejero ───────────────────────────────────


def load_profile(profile_path: str) -> dict:
    """Carga el perfil JSON de un consejero."""
    with open(profile_path, "r", encoding="utf-8") as f:
        return json.load(f)


def _esc(text: str) -> str:
    for ch in ("_", "*", "`", "["):
        text = text.replace(ch, f"\\{ch}")
    return text


# ── Generacion de respuesta ────────────────────────────────


async def _generate_response(profile: dict, task: str) -> str:
    """Genera respuesta como este consejero — LLM o template."""
    if CONSEJO_USE_LLM and CONSEJO_LLM_API_KEY:
        return await _generate_llm(profile, task)
    return _generate_template(profile, task)


def _generate_template(profile: dict, task: str) -> str:
    """Respuesta basada en personalidad sin LLM."""
    traits = profile.get("personality_traits", [])
    trait_list = ", ".join(traits[:3]) if traits else profile["domain"]
    return (
        f"Desde mi rol como {profile['role']} ({profile['title_es']}), "
        f"analizo \"{task}\" bajo mis ejes: {trait_list}.\n\n"
        f"Mi dominio es {profile['domain'].lower()}. "
        f"Inspirado por {profile['legend']}, mi recomendacion es abordar esto "
        f"con foco en lo que realmente mueve la aguja desde {profile['side']}."
    )


async def _generate_llm(profile: dict, task: str) -> str:
    """Respuesta via Anthropic Messages API."""
    context_history = get_context_for_llm(limit=3)

    system_parts = [profile["system_prompt"]]
    if context_history:
        system_parts.append(f"\n{context_history}")
    system_parts.append(
        "\nIMPORTANTE: Responde SOLO en espanol. Maximo 2-3 parrafos cortos. "
        "Se directo, aporta tu perspectiva unica y termina con una recomendacion concreta."
    )
    system_prompt = "\n".join(system_parts)

    headers = {
        "x-api-key": CONSEJO_LLM_API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }
    payload = {
        "model": CONSEJO_LLM_MODEL,
        "max_tokens": CONSEJO_MAX_RESPONSE_LENGTH,
        "system": system_prompt,
        "messages": [{"role": "user", "content": task}],
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                CONSEJO_LLM_API_URL,
                json=payload,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=30),
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data["content"][0]["text"]
                body = await resp.text()
                logger.warning(f"LLM error for {profile['role']}: {resp.status} {body[:200]}")
                return _generate_template(profile, task)
    except Exception as e:
        logger.warning(f"LLM exception for {profile['role']}: {e}")
        return _generate_template(profile, task)


# ── Handlers ───────────────────────────────────────────────


def make_handlers(profile: dict):
    """Crea los handlers para un bot de consejero."""

    async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
        welcome = profile.get("welcome", f"Soy {profile['name']}, {profile['title_es']}.")
        text = (
            f"{profile['emoji']} *{profile['role']} — {_esc(profile['name'])}*\n"
            f"_{_esc(profile['title_es'])} | Leyenda: {_esc(profile['legend'])}_\n"
            f"_Lado {profile['side']} | Pareja: {profile['pair']}_\n\n"
            f"{_esc(welcome)}"
        )
        await update.message.reply_text(text, parse_mode="Markdown")

    async def cmd_perfil(update: Update, context: ContextTypes.DEFAULT_TYPE):
        traits = "\n".join(f"  • {t}" for t in profile.get("personality_traits", []))
        text = (
            f"{profile['emoji']} *{profile['role']} — {_esc(profile['name'])}*\n"
            f"_{_esc(profile['title_es'])}_\n\n"
            f"*Lado:* {profile['side']}\n"
            f"*Pareja coetanea:* {profile['pair']}\n"
            f"*Dominio:* {_esc(profile['domain'])}\n"
            f"*Leyenda:* {_esc(profile['legend'])}\n\n"
            f"*Rasgos:*\n{traits}"
        )
        await update.message.reply_text(text, parse_mode="Markdown")

    async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Responde a cualquier mensaje como este consejero."""
        task = update.message.text.strip()
        if not task:
            return

        await update.message.reply_text(
            f"{profile['emoji']} Procesando como {profile['role']}..."
        )

        response = await _generate_response(profile, task)

        # Guardar acta
        save_acta(
            target=profile["role"],
            task=task,
            responses=[{
                "role": profile["role"],
                "name": profile["name"],
                "side": profile["side"],
                "emoji": profile["emoji"],
                "response": response,
            }],
            llm_mode=CONSEJO_USE_LLM and bool(CONSEJO_LLM_API_KEY),
        )

        formatted = (
            f"{profile['emoji']} *{profile['role']} — {_esc(profile['name'])}*\n"
            f"_{_esc(profile['title_es'])} | Leyenda: {_esc(profile['legend'])}_\n\n"
            f"{_esc(response)}"
        )
        await update.message.reply_text(formatted, parse_mode="Markdown")

    return [
        CommandHandler("start", cmd_start),
        CommandHandler("help", cmd_start),
        CommandHandler("perfil", cmd_perfil),
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message),
    ]


# ── Crear aplicacion ──────────────────────────────────────


def create_consejero_app(token: str, profile: dict) -> Application:
    """Crea una Application de Telegram para un consejero."""
    app = Application.builder().token(token).build()
    for handler in make_handlers(profile):
        app.add_handler(handler)
    logger.info(f"Consejero {profile['role']} ({profile['name']}) ready")
    return app
