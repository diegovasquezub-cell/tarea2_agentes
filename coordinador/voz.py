"""Mensajes de voz de Telegram: descarga del audio y transcripción con Gemini antes de llegar al coordinador.

El texto transcrito se trata como cualquier mensaje del usuario (dato, nunca instrucciones). Siempre se le muestra
al usuario lo que se entendió, para que pueda corregir si la transcripción falló.
"""
import asyncio
import logging
import os

import httpx

log = logging.getLogger("coordinador.voz")

MAX_SEGUNDOS = int(os.environ.get("VOZ_MAX_SEGUNDOS", "60"))
MAX_BYTES = 5 * 1024 * 1024
MODELO = os.environ.get("MODELO", "gemini-3.5-flash-lite")
INAUDIBLE = "[INAUDIBLE]"
PROMPT = (
    "Transcribe literalmente lo que se dice en este audio, en el idioma original (normalmente español). "
    "Devuelve SOLO la transcripción, sin comillas, sin comentarios y sin agregar nada. "
    f"Si no hay voz humana inteligible, responde exactamente {INAUDIBLE}."
)


class ErrorVoz(Exception):
    """Falla controlada: el mensaje es apto para mostrárselo al usuario."""


async def descargar_audio(token: str, file_id: str) -> bytes:
    """Baja el archivo desde Telegram (getFile + descarga)."""
    async with httpx.AsyncClient(timeout=30) as c:
        r = await c.get(f"https://api.telegram.org/bot{token}/getFile", params={"file_id": file_id})
        if r.status_code != 200 or not r.json().get("ok"):
            raise ErrorVoz("No pude descargar el audio desde Telegram.")
        info = r.json()["result"]
        if int(info.get("file_size", 0)) > MAX_BYTES:
            raise ErrorVoz("El audio es demasiado pesado.")
        d = await c.get(f"https://api.telegram.org/file/bot{token}/{info['file_path']}")
        if d.status_code != 200:
            raise ErrorVoz("No pude descargar el audio desde Telegram.")
        return d.content


async def transcribir(audio: bytes, mime: str = "audio/ogg") -> str:
    """Transcribe con Gemini. Reintenta si la cuota gratuita (15 solicitudes/min) se excede."""
    from google import genai
    from google.genai import types

    cliente = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY", ""))
    ultimo = None
    for intento in range(3):
        try:
            r = await cliente.aio.models.generate_content(
                model=MODELO, contents=[types.Part.from_bytes(data=audio, mime_type=mime), PROMPT]
            )
            texto = (r.text or "").strip()
            if not texto or INAUDIBLE in texto:
                raise ErrorVoz("No pude entender el audio. ¿Puedes repetirlo o escribirlo?")
            return texto
        except ErrorVoz:
            raise
        except Exception as exc:
            ultimo = exc
            log.warning("transcripción falló (intento %s): %s", intento + 1, type(exc).__name__)
            await asyncio.sleep(8 * (intento + 1))
    raise ErrorVoz(f"No pude transcribir el audio: el proveedor del modelo falló ({type(ultimo).__name__}). Intenta de nuevo o escríbelo.")
