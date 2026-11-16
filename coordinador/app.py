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
from fastapi import BackgroundTasks, FastAPI, Request, Security
from fastapi.security import APIKeyHeader
from pydantic import BaseModel, Field
from fastapi.responses import FileResponse, JSONResponse
from pathlib import Path

load_dotenv()

import swagger_tema  # noqa: E402
import voz  # noqa: E402
from nucleo import EQUIPO, responder  # noqa: E402

log = logging.getLogger("coordinador.api")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")

COORD_API_KEY = os.environ.get("COORD_API_KEY", "")
WEBHOOK_SECRET = os.environ.get("TELEGRAM_WEBHOOK_SECRET", "")
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
CHATS_PERMITIDOS = {x.strip() for x in os.environ.get("TELEGRAM_CHATS_PERMITIDOS", "").split(",") if x.strip()}
MAX_CHARS = 2000

app = FastAPI(
    title="Coordinador Grupo 3 (A2A)",
    docs_url=None,
    redoc_url=None,
    version="1.0.0",
    description=(
        "Coordinador del sistema de agentes del Grupo 3: elige a qué agente preguntarle, conserva su respuesta y recuerda "
        "la conversación. `POST /chat` exige la clave del coordinador (**Authorize**, cabecera `X-API-Key`); `POST /telegram` "
        "exige el secreto del webhook de Telegram (acepta texto y notas de voz, que se transcriben con Gemini). Límite conocido: Gemini en capa gratuita (15 solicitudes por minuto); si se "
        "supera, el sistema avisa que el proveedor falló en vez de simular una respuesta. La memoria vive en el servidor y se "
        "pierde al reiniciar."
    ),
)
clave_docs = APIKeyHeader(name="X-API-Key", auto_error=False, description="Clave del coordinador (la valida el servidor).")
secreto_docs = APIKeyHeader(name="X-Telegram-Bot-Api-Secret-Token", auto_error=False, description="Secreto del webhook de Telegram.")


class ChatIn(BaseModel):
    mensaje: str = Field(description="Texto del usuario (máx. 2000 caracteres).", examples=["hola"])
    conversacion_id: str | None = Field(default=None, description="Identifica la conversación (memoria). Si falta se crea una nueva.")
_vistos: list[int] = []  # update_id ya procesados (Telegram reintenta si tarda)


def igual(a: str, b: str) -> bool:
    return bool(b) and hmac.compare_digest(a.encode(), b.encode())


@app.on_event("startup")
async def arranque():
    await EQUIPO.refrescar(forzar=True)
    log.info("agentes cargados: %s", [a.nombre for a in EQUIPO.agentes])


PAGINA = Path(__file__).parent / "static" / "index.html"


@app.get("/", include_in_schema=False)
def pagina():
    """Chat web de prueba + diagrama de la arquitectura. No contiene ninguna clave: la ingresa quien prueba."""
    return FileResponse(PAGINA, media_type="text/html; charset=utf-8", headers={"Cache-Control": "no-cache"})


@app.get("/docs", include_in_schema=False)
def docs():
    return swagger_tema.pagina(
        app, "Coordinador Grupo 3",
        "API del coordinador: chat protegido por clave, estado de los agentes y webhook de Telegram. Pulsa Authorize e ingresa la clave de prueba.",
        "/", "Chat con el coordinador", "G3",
    )


@app.get("/estado", summary="Estado público de los agentes (alimenta el diagrama)")
async def estado():
    await EQUIPO.refrescar()
    disp = await EQUIPO.disponibles()
    return {
        "coordinador": "ok",
        "agentes": [
            {
                "nombre": a.nombre,
                "skills": [x.get("name", "") for x in (a.ficha or {}).get("skills", [])],
                "ficha": a.url + "/.well-known/agent-card.json",
                "disponible": disp.get(a.url, False),
            }
            for a in EQUIPO.agentes
        ],
    }


@app.get("/salud")
def salud():
    return {"estado": "ok", "agentes": [{"nombre": a.nombre, "url": a.url} for a in EQUIPO.agentes]}


@app.post("/chat", dependencies=[Security(clave_docs)], summary="Enviar un mensaje al coordinador",
          openapi_extra={"requestBody": {"required": True, "content": {"application/json": {"schema": ChatIn.model_json_schema(), "example": {"mensaje": "hola", "conversacion_id": "demo-1"}}}}})
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


async def procesar_update(chat_id: int, msg: dict):
    texto = msg.get("text")
    prefijo = ""
    nota = msg.get("voice") or msg.get("audio")
    if texto is None and nota:  # nota de voz o archivo de audio: se transcribe antes de llegar al coordinador
        if int(nota.get("duration", 0)) > voz.MAX_SEGUNDOS:
            await enviar_telegram(chat_id, f"Tu audio dura más de {voz.MAX_SEGUNDOS} segundos. Envía uno más corto o escríbeme tu consulta.")
            return
        try:
            audio = await voz.descargar_audio(BOT_TOKEN, nota["file_id"])
            texto = await voz.transcribir(audio, nota.get("mime_type") or "audio/ogg")
        except voz.ErrorVoz as exc:
            await enviar_telegram(chat_id, str(exc))
            return
        log.info("telegram chat=%s audio transcrito (%s caracteres)", chat_id, len(texto))
        prefijo = f"Entendí tu audio: «{texto}»\n\n"  # se muestra lo entendido para que el usuario pueda corregir
    if texto is None:
        await enviar_telegram(chat_id, "No puedo leer ese tipo de mensaje (fotos, stickers u otros archivos). Escríbeme tu consulta en texto o mándame una nota de voz.")
        return
    if len(texto) > MAX_CHARS:
        await enviar_telegram(chat_id, f"Tu mensaje es demasiado largo (máximo {MAX_CHARS} caracteres).")
        return
    respuesta, saltos = await responder(texto, f"tg:{chat_id}")
    log.info("telegram chat=%s saltos=%s", chat_id, saltos)
    await enviar_telegram(chat_id, prefijo + respuesta)


@app.post("/telegram", dependencies=[Security(secreto_docs)], summary="Webhook de Telegram")
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
    tareas.add_task(procesar_update, chat_id, msg)
    return {"ok": True}
