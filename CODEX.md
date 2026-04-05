# CODEX — Yarig.Telegram

## Estado (2026-04-05): CONSEJO DE ADMINISTRACION EN MARCHA

Control de Yarig.ai desde Telegram + Consejo de Administracion con 8 sillas IA.

## Arquitectura

```
Yarig.Telegram/
├── src/
│   ├── bot.py              # Bot principal (tareas Yarig + consejo dispatch)
│   ├── yarig.py            # Cliente async Yarig.ai API
│   ├── consejo.py          # Logica del consejo: 8 miembros, lados, parejas, LLM
│   ├── consejero_bot.py    # Bot individual por consejero (privado + grupo)
│   ├── consejeros_runner.py # Arranca los 8 bots en un solo proceso
│   ├── actas.py            # Persistencia de consultas (data/actas.json)
│   ├── dispatch_telegram.py # Notifica bots individuales tras dispatch
│   ├── config.py           # Variables de entorno
│   └── __init__.py
├── data/
│   └── actas.json          # Historial de consultas al consejo (gitignored)
├── docs/
│   └── yarig_api_map.md    # 25 endpoints Yarig.ai
└── .env                    # Tokens y credenciales (gitignored)
```

Los perfiles de los consejeros viven en el repo hermano:
```
AdmiraNext-Team/consejeros/
├── ceo.json, cfo.json, coo.json, cto.json  (operativo)
├── cco.json, cso.json, cxo.json, cdo.json  (creativo)
└── README.md
```

## Consejo de Administracion — Las 8 sillas

### Lado OPERATIVO (izquierda)
| Silla | Rol | Actual | Leyenda | Bot Telegram | Token |
|-------|-----|--------|---------|--------------|-------|
| 1 | CEO | Elon Musk | Steve Jobs | @AdmiraNext_CEO_bot | CREADO |
| 2 | CFO | Ruth Porat | Warren Buffett | @AdmiraNext_CFO_bot | CREADO |
| 3 | COO | Gwynne Shotwell | Tim Cook | @AdmiraNext_COO_bot | CREADO |
| 4 | CTO | Jensen Huang | Steve Wozniak | @AdmiraNext_CTO_bot | CREADO |

### Lado CREATIVO (derecha)
| Silla | Rol | Actual | Leyenda | Bot Telegram | Token |
|-------|-----|--------|---------|--------------|-------|
| 5 | CCO | John Lasseter | Walt Disney | @AdmiraNext_CCO_bot | CREADO |
| 6 | CSO | Ryan Reynolds | George Lucas | @AdmiraNext_CSO_bot | PENDIENTE (BotFather rate limit) |
| 7 | CXO | Carlo Ratti | Es Devlin | @AdmiraNext_CXO_bot | PENDIENTE |
| 8 | CDO | Jony Ive | Dieter Rams | @AdmiraNext_CDO_bot | PENDIENTE |

### Parejas coetaneas (cruzan la mesa)
- CEO <-> CSO (direccion + estrategia)
- CFO <-> CDO (caja + datos/metricas)
- COO <-> CXO (operaciones + experiencia)
- CTO <-> CCO (tecnologia + marca)

## Comandos del bot principal (bot.py)

### Tareas Yarig.ai (13 comandos)
- /yarig, /tarea, /iniciar, /pausar, /finalizar
- /fichar, /extras, /score, /equipo, /pedir, /proyectos, /historial, /help

### Consejo de Administracion (6 comandos)
| Comando | Que hace |
|---------|----------|
| /consejo | Muestra mesa visual + botones inline para seleccionar target |
| /consulta consejo <tarea> | Los 8 responden |
| /consulta operativo <tarea> | Solo CEO, CFO, COO, CTO |
| /consulta creativo <tarea> | Solo CCO, CSO, CXO, CDO |
| /consulta pareja:CEO <tarea> | Par coetaneo (CEO + CSO) |
| /consulta CTO <tarea> | Silla individual |
| /actas | Historial de consultas al consejo |
| /acta <n> | Detalle de un acta |

### Flujo interactivo (via botones inline)
1. /consejo -> aparece mesa con botones
2. Pulsar boton (ej: "Operativo") -> bot pide la tarea
3. Escribir tarea -> cada consejero seleccionado responde
4. Se guarda acta automaticamente

## Bots individuales de consejeros (consejero_bot.py)

Cada consejero tiene su propio bot de Telegram. En privado responde a todo. En grupo:

| Comando | Quien responde |
|---------|---------------|
| /consejo <tarea> | Todos los bots |
| /operativo <tarea> | Solo lado operativo (CEO, CFO, COO, CTO) |
| /creativo <tarea> | Solo lado creativo (CCO, CSO, CXO, CDO) |
| /pareja CEO <tarea> | Solo la pareja coetanea (CEO + CSO) |
| @AdmiraNext_CEO_bot <texto> | Solo el mencionado |

### Arranque
```bash
# Bot principal (tareas + consejo dispatch)
python -m src.bot

# 8 bots individuales de consejeros (un proceso)
python -m src.consejeros_runner
```

El runner carga perfiles de AdmiraNext-Team/consejeros/*.json y arranca solo los que tienen token configurado en .env. Los que no, se saltan.

## Modo LLM

Por defecto usa templates predefinidos por rol. Para activar respuestas via Claude:

```env
CONSEJO_USE_LLM=true
CONSEJO_LLM_API_KEY=sk-ant-...
CONSEJO_LLM_MODEL=claude-sonnet-4-20250514
```

Cuando LLM esta activo:
- System prompts incluyen contexto del consejo, pareja coetanea y actas previas
- Respuestas en paralelo via asyncio.gather()
- Fallback a templates si la API falla

## Memoria de decisiones (actas)

Cada consulta al consejo se guarda automaticamente en data/actas.json:
- Timestamp, target, tarea, respuestas, modo (template/LLM)
- /actas muestra las ultimas 10
- /acta <n> muestra detalle completo
- El contexto LLM se alimenta de las ultimas 3 actas

## Config (.env)

```env
# Bot principal
TELEGRAM_BOT_TOKEN=...
YARIG_EMAIL=...
YARIG_PASSWORD=...

# LLM (opcional)
CONSEJO_USE_LLM=false
CONSEJO_LLM_API_URL=https://api.anthropic.com/v1/messages
CONSEJO_LLM_API_KEY=
CONSEJO_LLM_MODEL=claude-sonnet-4-20250514
CONSEJO_MAX_RESPONSE_LENGTH=500

# Bots individuales (crear via @BotFather)
BOT_TOKEN_CEO=...
BOT_TOKEN_CFO=...
BOT_TOKEN_COO=...
BOT_TOKEN_CTO=...
BOT_TOKEN_CCO=...
BOT_TOKEN_CSO=  # PENDIENTE crear en BotFather
BOT_TOKEN_CXO=  # PENDIENTE crear en BotFather
BOT_TOKEN_CDO=  # PENDIENTE crear en BotFather
```

## PENDIENTE para el proximo agente

### Prioridad 1 — Completar bots
1. Crear 3 bots en @BotFather: CSO, CXO, CDO (rate limit expira ~15:00 UTC del 2026-04-06)
   - Nombres: AdmiraNext CSO, AdmiraNext CXO, AdmiraNext CDO
   - Usernames: AdmiraNext_CSO_bot, AdmiraNext_CXO_bot, AdmiraNext_CDO_bot
2. Guardar tokens en .env
3. Reiniciar consejeros_runner

### Prioridad 2 — Avatares de leyendas
Generar en Grok (grok.com/imagine) avatares pixel art de cada leyenda:
- Steve Jobs (CEO), Warren Buffett (CFO), Tim Cook (COO), Steve Wozniak (CTO), Walt Disney (CCO)
- George Lucas (CSO), Es Devlin (CXO), Dieter Rams (CDO)
Prompt tipo: "Pixel art portrait avatar of [nombre], square format, dark navy background, [rasgos], retro game character style, head and shoulders only, centered"
Asignar via BotFather -> /setuserpic -> seleccionar bot -> subir imagen

### Prioridad 3 — Grupo de Telegram
1. Crear grupo "Consejo AdmiraNext"
2. Añadir los 8 bots (o los que esten creados)
3. En BotFather: /setprivacy -> Disable para cada bot (para que lean todos los mensajes del grupo, no solo comandos)
4. Probar /operativo, /creativo, /consejo en el grupo

### Prioridad 4 — Mejoras futuras
- Votaciones: que los consejeros voten a favor/en contra con resumen
- Debate: rondas de discusion entre consejeros
- Asignacion a Yarig: crear tarea real en Yarig.ai tras consulta
- LLM activado por defecto con API key de Anthropic

## Repos relacionados
- csilvasantin/AdmiraNext-Team — perfiles consejeros + panel de equipo
- csilvasantin/Admira-Next-Dream-Team — dream team IA (claude, codex, etc.)
- csilvasantin/Memorizer — bot principal que integra Yarig
