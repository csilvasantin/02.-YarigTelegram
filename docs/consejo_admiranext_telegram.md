# Integracion Telegram con Consejo AdmiraNext

Version documentada: `v.2026.13.04.10`

Esta integracion permite operar el Consejo AdmiraNext desde Telegram en dos modos complementarios:

- enviar misiones a la web/equipos del Consejo
- consultar directamente al LLM gratuito del Consejo y recibir la respuesta en Telegram

Web publica del Consejo:

`https://csilvasantin.github.io/ConsejoAdmiraNextGame/council-scumm.html?tight=v2`

## Comandos Telegram

| Comando | Uso |
|---------|-----|
| `/consejoweb <mision>` | Envia una mision a la web/equipos del Consejo AdmiraNext |
| `/consejoweb codex :: <mision>` | Envia la mision solo a Codex |
| `/consejoweb claude :: <mision>` | Envia la mision solo a Claude |
| `/consejo_web <mision>` | Alias de `/consejoweb` |
| `/admiranext <mision>` | Alias de `/consejoweb` |
| `/consejoia <pregunta>` | Consulta al Consejo IA con Llama 3.3 gratuito |
| `/consejoia coetaneos :: <pregunta>` | Consulta al Consejo coetaneo |
| `/consejo_ia <pregunta>` | Alias de `/consejoia` |
| `/consejollm <pregunta>` | Alias de `/consejoia` |

## Diferencia entre `/consejoweb` y `/consejoia`

`/consejoweb` lanza una mision operativa a la web/equipos del Consejo. Usa el servidor local del juego:

`CONSEJO_GAME_API_URL=http://127.0.0.1:9125`

Endpoint:

`POST /api/teamwork/send-all`

Payload:

```json
{
  "prompt": "texto de la mision",
  "target": "all | codex | claude | terminal"
}
```

`/consejoia` consulta el LLM del Consejo y devuelve respuestas en Telegram. Usa el API del Consejo:

`CONSEJO_WEB_LLM_API_URL=http://127.0.0.1:8420`

Endpoint:

`POST /api/council/ask`

Payload enviado por Telegram:

```json
{
  "message": "texto de la pregunta",
  "generation": "leyendas",
  "context": [],
  "llm": "llama-70b"
}
```

## Modelo LLM por defecto

Telegram debe usar siempre el modelo gratuito:

`CONSEJO_WEB_LLM_MODEL=llama-70b`

En el Consejo AdmiraNext, esa clave corresponde a:

- nombre: `Llama 3.3 70B`
- proveedor: `groq`
- modelo: `llama-3.3-70b-versatile`
- coste: gratuito

La opcion de pago `claude-sonnet` existe en el API del Consejo, pero Telegram no la usa por defecto. Para mantener coste cero, no cambiar `CONSEJO_WEB_LLM_MODEL` salvo decision explicita.

## Variables de entorno

Estas variables viven en `.env` local y no se suben al repositorio:

```bash
TELEGRAM_BOT_TOKEN=...
YARIG_EMAIL=...
YARIG_PASSWORD=...
CONSEJO_GAME_API_URL=http://127.0.0.1:9125
CONSEJO_WEB_LLM_API_URL=http://127.0.0.1:8420
CONSEJO_WEB_LLM_TOKEN=...
CONSEJO_WEB_LLM_MODEL=llama-70b
```

`CONSEJO_WEB_LLM_TOKEN` se envia como cabecera:

`X-Council-Token`

## Servicios locales necesarios

Para que `/consejoweb` funcione:

```bash
cd /Users/csilvasantin/Claude/repos/ConsejoAdmiraNextGame
PORT=9125 npm start
```

Para que `/consejoia` funcione:

```bash
cd /Users/csilvasantin/Claude/repos/ConsejoAdmiraNextGame
python3 council-api.py
```

El API del Consejo se verifica con:

```bash
curl -s http://127.0.0.1:8420/api/council/health
curl -s http://127.0.0.1:8420/api/council/models
```

## Comportamiento en Telegram

Las respuestas del Consejo se envian como texto seguro:

- los mensajes largos se trocean en bloques de 3800 caracteres
- si Telegram rechaza Markdown, el bot reintenta en texto plano
- `/consejoia` responde en texto plano para evitar fallos por caracteres generados por IA

## Prueba operativa realizada

Consulta real ejecutada contra el Consejo IA:

`Prueba Telegram Llama 3.3: confirma en una frase que estas usando el modelo gratuito.`

Resultado:

- `ok=True`
- modelo usado: `llama-70b`
- respuesta racional recibida
- respuesta creativa recibida

El endpoint `/api/council/models` confirmo:

- `llama-70b`
- `Llama 3.3 70B`
- `free=true`
- `available=true`

## Repositorios relacionados

- Yarig.Telegram: `https://github.com/csilvasantin/02.-YarigTelegram`
- Consejo AdmiraNext Game: `https://github.com/csilvasantin/ConsejoAdmiraNextGame`
- Web publica: `https://csilvasantin.github.io/ConsejoAdmiraNextGame/council-scumm.html?tight=v2`

## Criterio de uso

Usar `/consejoia` cuando se quiera una respuesta del Consejo en Telegram.

Usar `/consejoweb` cuando se quiera mandar una mision a la sala/equipos del Consejo.

