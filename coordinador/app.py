"""API del coordinador (FastAPI).

  GET  /salud      público
  POST /chat       exige la cabecera X-API-Key = COORD_API_KEY      {"mensaje": "...", "conversacion_id": "..."}
  POST /telegram   exige la cabecera X-Telegram-Bot-Api-Secret-Token = TELEGRAM_WEBHOOK_SECRET
"""
import hmac
import logging
import os
import uuid

import httpx
from dotenv import load_dotenv
from fastapi import BackgroundTasks, FastAPI, Request
from fastapi.responses import JSONResponse

load_dotenv()

from nucleo import EQUIPO, responder  # noqa: E402

log = logging.getLogger("coordinador.api")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")

COORD_API_KEY = os.environ.get("COORD_API_KEY", "")
WEBHOOK_SECRET = os.environ.get("TELEGRAM_WEBHOOK_SECRET", "")
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
CHATS_PERMITIDOS = {x.strip() for x in os.environ.get("TELEGRAM_CHATS_PERMITIDOS", "").split(",") if x.strip()}
MAX_CHARS = 2000

app = FastAPI(title="Coordinador Grupo 3", docs_url=None, redoc_url=None, openapi_url=None)
_vistos: list[int] = []  # update_id ya procesados (Telegram reintenta si tarda)


def igual(a: str, b: str) -> bool:
    return bool(b) and hmac.compare_digest(a.encode(), b.encode())


@app.on_event("startup")
async def arranque():
    await EQUIPO.refrescar(forzar=True)
    log.info("agentes cargados: %s", [a.nombre for a in EQUIPO.agentes])


@app.get("/salud")
def salud():
    return {"estado": "ok", "agentes": [{"nombre": a.nombre, "url": a.url} for a in EQUIPO.agentes]}


@app.post("/chat")
async def chat(request: Request):
    if not igual(request.headers.get("x-api-key", ""), COORD_API_KEY):
        return JSONResponse({"error": "No autorizado: falta la clave del coordinador o es incorrecta."}, status_code=401)
    try:
        body = await request.json()
    except Exception:
        return JSONResponse({"error": "JSON inválido."}, status_code=400)
    mensaje = body.get("mensaje") if isinstance(body, dict) else None
    if not isinstance(mensaje, str) or not mensaje.strip():
        return JSONResponse({"error": "Falta el campo 'mensaje' con texto."}, status_code=422)
    if len(mensaje) > MAX_CHARS:
        return JSONResponse({"error": f"El mensaje supera los {MAX_CHARS} caracteres."}, status_code=422)
    conv = str(body.get("conversacion_id") or uuid.uuid4())[:100]
    respuesta, saltos = await responder(mensaje.strip(), f"api:{conv}")
    return {"respuesta": respuesta, "conversacion_id": conv, "saltos": saltos}


async def enviar_telegram(chat_id: int, texto: str):
    if not BOT_TOKEN:
        log.error("falta TELEGRAM_BOT_TOKEN")
        return
    async with httpx.AsyncClient(timeout=15) as c:
        for i in range(0, len(texto), 4000):  # límite de Telegram: 4096 caracteres
            r = await c.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", json={"chat_id": chat_id, "text": texto[i : i + 4000]})
            if r.status_code != 200:
                log.error("sendMessage falló: HTTP %s", r.status_code)


async def procesar_update(chat_id: int, texto: str | None):
    if texto is None:
        await enviar_telegram(chat_id, "No puedo leer ese tipo de mensaje (fotos, stickers, audios u otros archivos). Escríbeme tu consulta en texto.")
        return
    if len(texto) > MAX_CHARS:
        await enviar_telegram(chat_id, f"Tu mensaje es demasiado largo (máximo {MAX_CHARS} caracteres).")
        return
    respuesta, saltos = await responder(texto, f"tg:{chat_id}")
    log.info("telegram chat=%s saltos=%s", chat_id, saltos)
    await enviar_telegram(chat_id, respuesta)


@app.post("/telegram")
async def telegram(request: Request, tareas: BackgroundTasks):
    if not igual(request.headers.get("x-telegram-bot-api-secret-token", ""), WEBHOOK_SECRET):
        return JSONResponse({"error": "No autorizado: secreto del webhook incorrecto."}, status_code=401)
    try:
        upd = await request.json()
    except Exception:
        return JSONResponse({"error": "JSON inválido."}, status_code=400)
    uid = upd.get("update_id")
    if uid in _vistos:
        return {"ok": True}
    _vistos.append(uid)
    del _vistos[:-500]
    msg = upd.get("message")
    if not msg or "chat" not in msg:
        return {"ok": True}  # otros tipos de update (ediciones, etc.): se ignoran
    chat_id = msg["chat"]["id"]
    if CHATS_PERMITIDOS and str(chat_id) not in CHATS_PERMITIDOS:
        log.warning("chat no autorizado: %s", chat_id)
        return {"ok": True}
    tareas.add_task(procesar_update, chat_id, msg.get("text"))
    return {"ok": True}
