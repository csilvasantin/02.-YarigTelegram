"""Actas del Consejo — persistencia de consultas y decisiones."""

from __future__ import annotations

import json
import logging
import os
import time
from datetime import datetime, timezone
from typing import Optional

logger = logging.getLogger(__name__)

ACTAS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
ACTAS_FILE = os.path.join(ACTAS_DIR, "actas.json")


def _ensure_dir():
    os.makedirs(ACTAS_DIR, exist_ok=True)


def _load_actas() -> list[dict]:
    if not os.path.exists(ACTAS_FILE):
        return []
    try:
        with open(ACTAS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        logger.warning(f"Error loading actas: {e}")
        return []


def _save_actas(actas: list[dict]):
    _ensure_dir()
    with open(ACTAS_FILE, "w", encoding="utf-8") as f:
        json.dump(actas, f, ensure_ascii=False, indent=2)


def save_acta(
    target: str,
    task: str,
    responses: list[dict],
    llm_mode: bool = False,
) -> int:
    """Guarda un acta y devuelve su numero."""
    actas = _load_actas()
    acta_num = len(actas) + 1
    acta = {
        "num": acta_num,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "target": target,
        "task": task,
        "llm_mode": llm_mode,
        "responses": responses,
    }
    actas.append(acta)
    _save_actas(actas)
    return acta_num


def get_acta(num: int) -> Optional[dict]:
    """Devuelve un acta por su numero."""
    actas = _load_actas()
    if 1 <= num <= len(actas):
        return actas[num - 1]
    return None


def get_recent_actas(limit: int = 10) -> list[dict]:
    """Devuelve las ultimas N actas (mas reciente primero)."""
    actas = _load_actas()
    return list(reversed(actas[-limit:]))


def get_actas_count() -> int:
    return len(_load_actas())


def get_context_for_llm(limit: int = 3) -> str:
    """Genera un resumen de las ultimas actas para inyectar como contexto LLM."""
    actas = _load_actas()
    if not actas:
        return ""

    recent = actas[-limit:]
    lines = ["Decisiones recientes del consejo:"]
    for a in recent:
        ts = a["timestamp"][:10]
        target = a["target"]
        task = a["task"]
        roles = [r["role"] for r in a["responses"]]
        lines.append(f"- [{ts}] Consulta a {target}: \"{task}\" (respondieron: {', '.join(roles)})")

    return "\n".join(lines)


def format_acta_detail(acta: dict) -> str:
    """Formatea un acta completa para mostrar en Telegram."""

    def esc(text: str) -> str:
        for ch in ("_", "*", "`", "["):
            text = text.replace(ch, f"\\{ch}")
        return text

    ts = acta["timestamp"][:16].replace("T", " ")
    mode = "LLM" if acta.get("llm_mode") else "Templates"
    lines = [
        f"📜 *Acta #{acta['num']}*",
        f"📅 {ts} UTC",
        f"👥 Target: {esc(acta['target'])}",
        f"📋 Tarea: {esc(acta['task'])}",
        f"🤖 Modo: {mode}",
        f"{'─' * 30}",
    ]
    for r in acta["responses"]:
        lines.append(f"\n{r.get('emoji', '•')} *{r['role']} — {esc(r['name'])}*")
        lines.append(esc(r["response"]))

    return "\n".join(lines)


def format_actas_list(actas: list[dict]) -> str:
    """Formatea la lista resumida de actas."""

    def esc(text: str) -> str:
        for ch in ("_", "*", "`", "["):
            text = text.replace(ch, f"\\{ch}")
        return text

    if not actas:
        return "📜 No hay actas registradas."

    lines = [f"📜 *Actas del Consejo* ({get_actas_count()} total)\n"]
    for a in actas:
        ts = a["timestamp"][:10]
        task_short = esc(a["task"][:40])
        if len(a["task"]) > 40:
            task_short += "..."
        n_resp = len(a["responses"])
        lines.append(f"*#{a['num']}* [{ts}] {task_short} ({n_resp} voces)")

    lines.append(f"\n_Usa_ /acta <n> _para ver el detalle._")
    return "\n".join(lines)
