# CODEX — Yarig.Telegram

## Estado (2026-04-04): COMPLETO Y FUNCIONANDO

Control de Yarig.ai desde Telegram con panel inline interactivo.
Integrado en Memorizer bot (csilvasantin/Memorizer).

## Comandos implementados (13)
- /yarig — Panel tareas con botones inline ▶️⏸✅
- /tarea, /iniciar, /pausar, /finalizar — CRUD tareas
- /fichar, /fichar salida — jornada
- /extras, /extras fin — horas extras
- /score, /equipo, /pedir, /proyectos, /historial

## Auth
- Login email+password POST /registration/login
- SSL disabled (cert incompleto yarig.ai)
- Cookie jar con CookieJar(unsafe=True) para rotación cisession

## Config (.env)
TELEGRAM_BOT_TOKEN, YARIG_EMAIL, YARIG_PASSWORD

## API map completo en docs/yarig_api_map.md (25 endpoints)

## Repos relacionados
- csilvasantin/Memorizer — bot principal que integra este módulo
- csilvasantin/Yarig.aiTheGame — juego isométrico (en desarrollo)
