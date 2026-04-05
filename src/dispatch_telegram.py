"""Dispatch de tareas a bots individuales via Telegram API."""

from __future__ import annotations

import logging
import os

import aiohttp

logger = logging.getLogger(__name__)

# Mapeo rol -> env key del token del bot individual
BOT_TOKEN_MAP = {
    "CEO": "BOT_TOKEN_CEO",
    "CFO": "BOT_TOKEN_CFO",
    "COO": "BOT_TOKEN_COO",
    "CTO": "BOT_TOKEN_CTO",
    "CCO": "BOT_TOKEN_CCO",
    "CSO": "BOT_TOKEN_CSO",
    "CXO": "BOT_TOKEN_CXO",
    "CDO": "BOT_TOKEN_CDO",
}

TELEGRAM_API = "https://api.telegram.org"


def get_bot_token(role: str) -> str:
    """Devuelve el token del bot individual de un consejero."""
    env_key = BOT_TOKEN_MAP.get(role.upper(), "")
    return os.getenv(env_key, "") if env_key else ""


async def get_bot_info(token: str) -> dict | None:
    """Obtiene info del bot (username, id) via getMe."""
    if not token:
        return None
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{TELEGRAM_API}/bot{token}/getMe") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data.get("result")
    except Exception as e:
        logger.warning(f"getMe error: {e}")
    return None


async def send_message_as_bot(token: str, chat_id: int, text: str, parse_mode: str = "Markdown") -> bool:
    """Envia un mensaje como un bot individual a un chat."""
    if not token:
        return False
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{TELEGRAM_API}/bot{token}/sendMessage",
                json={
                    "chat_id": chat_id,
                    "text": text,
                    "parse_mode": parse_mode,
                },
            ) as resp:
                if resp.status == 200:
                    return True
                body = await resp.text()
                logger.warning(f"sendMessage error: {resp.status} {body[:200]}")
                return False
    except Exception as e:
        logger.warning(f"sendMessage exception: {e}")
        return False


async def notify_consejero_bots(
    roles: list[str],
    task: str,
    chat_id: int,
    responses: dict[str, str] | None = None,
) -> list[str]:
    """
    Notifica a los bots individuales de los consejeros sobre una tarea.
    Si responses se proporciona, envia la respuesta de cada uno.
    Devuelve lista de roles notificados con exito.
    """
    notified = []
    for role in roles:
        token = get_bot_token(role)
        if not token:
            continue

        if responses and role in responses:
            text = f"📋 *Tarea asignada al consejo:*\n{task}\n\n💬 *Mi respuesta:*\n{responses[role]}"
        else:
            text = f"📋 *Nueva tarea asignada al consejo:*\n{task}"

        success = await send_message_as_bot(token, chat_id, text)
        if success:
            notified.append(role)

    return notified
