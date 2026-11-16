# Sistema de agentes · Grupo 3 · Implementa y entrega tu sistema de agentes

Curso 2 · Sesión 3. Un **coordinador** al que se le escribe por **Telegram** (o por API) y **cuatro agentes especialistas**,
uno por integrante, que se comunican por **A2A**. Todo está desplegado en **Heroku** (una app por agente y una para el
coordinador), con HTTPS, claves y secretos fuera del repositorio.

## Integrantes y aportes

| Integrante | Agente | Carpeta | Aporte |
|---|---|---|---|
| Gerardo Herrera | Agente Gerardo Herrera | `agentes/gerardo/` | Definió su agente (perfil, skills, apuntes, blueprint) en el taller A2A. Arquitectura de software y sistemas con agentes de IA. |
| Diego Vasquez | Agente Diego Vasquez | `agentes/diego/` | Definió su agente (ingeniería de datos en Azure) y armó la integración, el coordinador, el despliegue y la entrega de este repositorio. |
| Jaime Vidal | Agente Jaime Vidal | `agentes/jaime/` | Definió su agente (operaciones en alimentos, calidad e inventarios). |
| Henry Ambicho | Agente Henry Ambicho | `agentes/henry/` | Definió su agente (tecnología móvil y full-stack). |

Los perfiles, skills, apuntes y blueprints vienen del **Taller A2A** (cada carpeta tiene su `blueprint.md`). Aquí cada
agente se convirtió en un servicio A2A propio con clave, ficha pública y despliegue independiente.

## Direcciones públicas

| Agente | Dueño | Ficha pública (sin clave) | Swagger |
|---|---|---|---|
| Gerardo Herrera | Gerardo | https://g3-a2a-gerardo-106ec27110d5.herokuapp.com/.well-known/agent-card.json | `/docs` |
| Diego Vasquez | Diego | https://g3-a2a-diego-835311cf3a46.herokuapp.com/.well-known/agent-card.json | `/docs` |
| Jaime Vidal | Jaime | https://g3-a2a-jaime-247f1f25d28a.herokuapp.com/.well-known/agent-card.json | `/docs` |
| Henry Ambicho | Henry | https://g3-a2a-henry-3278a379eb91.herokuapp.com/.well-known/agent-card.json | `/docs` |

- **Coordinador:** https://g3-a2a-coordinador-22655cb5eaa9.herokuapp.com (Swagger en `/docs`)
- **Canal:** Telegram, bot **@Grupo3_agentes_a2a_bot**

Las claves de prueba (de cada agente, del coordinador) se entregan **por una vía privada** al equipo docente; nunca están
en el repositorio. En los comandos de abajo se escriben como `<CLAVE_...>`.

### Prueba directa a un agente (sin pasar por el coordinador)

```bash
curl -X POST https://g3-a2a-diego-835311cf3a46.herokuapp.com/ \
  -H "X-API-Key: <CLAVE_DIEGO>" -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"message/send","params":{"message":{"kind":"message","role":"user","contextId":"prueba-1","messageId":"m1","parts":[{"kind":"text","text":"¿Cómo ordeno datos en la nube?"}]}}}'
```

Cambia la URL y la clave para Gerardo, Jaime o Henry. Sin la cabecera `X-API-Key` (o con una incorrecta) responde **401**.

### Prueba del coordinador por API

```bash
curl -X POST https://g3-a2a-coordinador-22655cb5eaa9.herokuapp.com/chat \
  -H "X-API-Key: <CLAVE_COORDINADOR>" -H "Content-Type: application/json" \
  -d '{"mensaje":"hola","conversacion_id":"demo-1"}'
```

La respuesta incluye `saltos`: qué decidió el supervisor y a qué agente llamó. También se puede usar **Swagger** (`/docs`
→ *Authorize* → pegar la clave).

## Cómo funciona

```
Telegram ──► Coordinador (FastAPI) ──A2A message/send──► Agente Gerardo | Diego | Jaime | Henry
              /telegram (secreto)      supervisor LangGraph      cada uno con su ficha, su skill,
              /chat (X-API-Key)        + MemorySaver             su herramienta de apuntes y su clave
```

- **Agentes** (`agentes/<nombre>/`): FastAPI con `GET /.well-known/agent-card.json` (público), `GET /salud` (público) y
  `POST /` JSON-RPC `message/send` (**exige clave**). Memoria por `contextId`. Herramienta `consultar_mis_apuntes` (datos
  reales del dueño, no respuestas inventadas). Rechazan con amabilidad lo que no es su tema.
- **Coordinador** (`coordinador/`): al arrancar lee las fichas de `URLS_AGENTES`; el supervisor elige un agente o responde
  «ninguno»; entrega **la respuesta del agente tal cual** (cifras, unidades y supuestos no se reescriben) indicando quién
  respondió; memoria por conversación con `MemorySaver` (un hilo por chat de Telegram o `conversacion_id`).
- **Seguridad:** `/chat` y cada agente exigen clave en el servidor; `/telegram` exige el secreto del webhook; las claves
  se comparan en tiempo constante; sin clave configurada el servicio **rechaza todo**. Secretos solo en variables de
  entorno de Heroku y en `.env` locales (ignorados por git).
- **Fallar bien:** si un agente no responde (caído, lento o con error), el coordinador avisa que *esa parte no está
  disponible* y los demás siguen respondiendo. Fotos, stickers y audios reciben «no puedo leer ese tipo de mensaje». Un
  intento de «ignora tus instrucciones» se rechaza y sigue siendo el coordinador.

## Limitaciones conocidas (leer antes de probar)

1. **Gemini en capa gratuita: 15 solicitudes por minuto.** Cada mensaje consume entre 2 y 4 llamadas al modelo
   (supervisor + agente + herramienta de apuntes). Si se supera la cuota el sistema responde con un error explícito
   («el proveedor del modelo falló» o «esa parte no está disponible»); **nunca** simula una respuesta. Los agentes y el
   supervisor reintentan hasta 5 veces con espera, y aun así, ráfagas de mensajes pueden fallar. **Recomendación para
   evaluar: un mensaje cada ~15 s**, o usar una clave de Gemini con facturación activa (variable `GOOGLE_API_KEY`).
2. **La memoria se pierde al reiniciar** (`MemorySaver` en memoria del proceso). Heroku reinicia los dynos al menos una
   vez al día y al desplegar.
3. **Arranque en frío:** en plan Eco el dyno duerme tras 30 min sin tráfico; la primera llamada puede tardar unos segundos.
4. La ficha de los agentes se cachea 5 minutos en el coordinador.
5. Solo mensajes de **texto** (máx. 2000 caracteres al coordinador, 4000 a un agente).

## Tests y límites de Gemini

- `tests/test_seguridad.py` (**no llama a Gemini**, no consume cuota): fichas, `/salud`, Swagger, 401 sin clave o con clave
  incorrecta, entradas inválidas, y que sin clave configurada el servicio rechaza todo.
  `python -m pytest tests -q`
- `scripts/probar_recorrido.py [URL]` recorre los casos del enunciado contra el coordinador (local o nube) **respetando la
  cuota gratuita**: espera `PAUSA` segundos (por defecto 14) entre mensajes y reintenta hasta `REINTENTOS` (3) veces si el
  proveedor responde «cuota excedida». Imprime fecha, lo probado y lo obtenido (sirve como evidencia). Dura unos 4 minutos.
- `coordinador/saltos.py "pregunta" ...` imprime los **saltos** del coordinador eligiendo a cada agente (salida de terminal
  para las evidencias).

## Levantar todo en local (Windows · PowerShell)

Requisitos: Python 3.12, una clave de Gemini y (opcional) un bot de Telegram.

```powershell
py -3.12 -m venv .venv
.venv\Scripts\python.exe -m pip install -r coordinador\requirements.txt pytest
copy coordinador\.env.example .env          # y completa GOOGLE_API_KEY y TELEGRAM_BOT_TOKEN (valores reales, solo en tu máquina)
```

Crea `secretos\claves_sistema.env` con las claves del sistema (invéntalas largas y aleatorias):

```
CLAVE_AGENTE_GERARDO=...   CLAVE_AGENTE_DIEGO=...   CLAVE_AGENTE_JAIME=...   CLAVE_AGENTE_HENRY=...   (una por línea)
COORD_API_KEY=...
TELEGRAM_WEBHOOK_SECRET=...
```

```powershell
.venv\Scripts\python.exe scripts\levantar_local.py     # agentes en 8001-8004 y coordinador en 8000; Ctrl+C los detiene
.venv\Scripts\python.exe scripts\probar_recorrido.py    # recorrido completo (respeta la cuota de Gemini)
.venv\Scripts\python.exe -m pytest tests -q             # pruebas de seguridad (sin Gemini)
```

Cada servicio también se puede iniciar solo: `cd agentes\gerardo` y
`..\..\.venv\Scripts\python.exe -m uvicorn app:app --port 8001` con las variables de su `.env.example`.
**Detener:** `Ctrl+C` en `levantar_local.py`. Los envíos por Telegram solo ocurren si respondes tú desde el chat del bot;
no hay envíos automáticos.

Para usar Telegram en local hace falta exponer el puerto (por eso el canal se prueba contra la versión desplegada).

## Desplegar en Heroku

Una app por componente, cada una desde su subcarpeta (`Procfile`, `requirements.txt` y `.python-version` incluidos):

```bash
heroku apps:create g3-a2a-gerardo --remote h-gerardo
heroku config:set -a g3-a2a-gerardo GOOGLE_API_KEY=... MODELO=gemini-3.5-flash-lite AGENT_API_KEY=... URL_PUBLICA=https://<app>.herokuapp.com
git subtree push --prefix agentes/gerardo h-gerardo main
```

Igual para `diego`, `jaime` y `henry`. Coordinador:

```bash
heroku config:set -a g3-a2a-coordinador GOOGLE_API_KEY=... COORD_API_KEY=... TELEGRAM_WEBHOOK_SECRET=... TELEGRAM_BOT_TOKEN=... \
  URLS_AGENTES=https://<gerardo>,https://<diego>,https://<jaime>,https://<henry> CLAVES_AGENTES=<k1>,<k2>,<k3>,<k4>
git subtree push --prefix coordinador h-coordinador main
curl "https://api.telegram.org/bot<TOKEN>/setWebhook" --data-urlencode "url=https://<coordinador>/telegram" --data-urlencode "secret_token=<TELEGRAM_WEBHOOK_SECRET>"
```

`CLAVES_AGENTES` va en el **mismo orden** que `URLS_AGENTES`. Los puertos, direcciones y secretos se configuran solo por
variables de entorno (ver cada `.env.example`, con valores ficticios). Servicios externos: Gemini (Google AI Studio),
Telegram Bot API y Heroku. No se guardan datos persistentes.

## Estructura

```
agentes/{gerardo,diego,jaime,henry}/   servicio A2A + prompts + herramientas + blueprint.md + Procfile + .env.example
coordinador/                           API, supervisor (LangGraph), canal Telegram, saltos.py, Procfile, .env.example
scripts/                               levantar_local.py · probar_recorrido.py
tests/                                 test_seguridad.py
evidencias/                            una captura por resultado esperado, con fecha y explicación
_plantillas/                           plantilla común de los agentes y su generador
```

## Evidencias

Ver [`evidencias/`](evidencias/): una captura por cada resultado esperado (1 a 12), con entorno (LOCAL o NUBE), fecha, lo que
se probó, lo que debía pasar y lo que pasó, más las salidas de terminal de `saltos.py` y de cada agente respondiendo solo.
