# Yarig.Telegram

Control completo de [Yarig.ai](https://yarig.ai) desde Telegram con panel interactivo de tareas.

## Que hace

Replica toda la funcionalidad de Yarig.ai en un bot de Telegram con botones inline que emulan la interfaz web:

```
📋 Tareas del día (Yarig.ai)

1. ▶️ Agente para Yarig.ai Memorizer — Admira
2. ⏳ Inbox 01 — Admira

┌──────────────────────────────────────┐
│ ▶️ 1. Agente para Yari...   ⏸   ✅  │
│ ⏳ 2. Inbox 01               ▶️      │
│            🔄 Actualizar             │
└──────────────────────────────────────┘
```

## Ciclo de vida de tarea

```
⏳ Pendiente  →  /iniciar   →  ▶️ En curso
▶️ En curso   →  /pausar    →  ⏸ Pausada
▶️ En curso   →  /finalizar →  ✅ Completada
⏸ Pausada    →  /iniciar   →  🔄 Reanudada
```

## Comandos

### Tareas
| Comando | Descripcion |
|---------|-------------|
| `/yarig` | Panel de tareas con controles inline |
| `/tarea <desc>` | Añadir nueva tarea |
| `/iniciar [n]` | Iniciar o reanudar tarea |
| `/pausar` | Pausar tarea activa |
| `/finalizar [n]` | Completar tarea |

### Jornada
| Comando | Descripcion |
|---------|-------------|
| `/fichar` | Fichar entrada |
| `/fichar salida` | Fichar salida |
| `/extras` | Iniciar horas extras |
| `/extras fin` | Finalizar horas extras |

### Equipo
| Comando | Descripcion |
|---------|-------------|
| `/score` | Tu puntuacion |
| `/equipo` | Miembros del equipo |
| `/pedir <nombre> <tarea>` | Enviar peticion a compañero |
| `/proyectos` | Lista de proyectos |
| `/historial` | Historial de tareas |

## Setup

```bash
cp .env.example .env
# Edita .env con tus credenciales

pip install -r requirements.txt
python -m src.bot
```

## API de Yarig.ai

Documentacion completa de los 25 endpoints JSON en [docs/yarig_api_map.md](docs/yarig_api_map.md).

## Tech Stack

- Python 3.13+
- python-telegram-bot
- aiohttp (sesion con Yarig.ai)
- Yarig.ai API (session-based PHP auth)
