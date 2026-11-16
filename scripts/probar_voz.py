"""Prueba la transcripción de voz (la misma función que usa el bot de Telegram) con un archivo de audio.

Uso:  python scripts/probar_voz.py ruta/al/audio.wav|.ogg|.mp3
Lee GOOGLE_API_KEY de ./.env (ignorado por git). Gasta 1 solicitud de Gemini.
"""
import asyncio
import os
import pathlib
import sys

from dotenv import dotenv_values

RAIZ = pathlib.Path(__file__).resolve().parent.parent
os.environ.setdefault("GOOGLE_API_KEY", dotenv_values(RAIZ / ".env").get("GOOGLE_API_KEY", ""))
sys.path.insert(0, str(RAIZ / "coordinador"))
import voz  # noqa: E402

if len(sys.argv) < 2:
    sys.exit("Uso: python scripts/probar_voz.py audio.wav")
ruta = pathlib.Path(sys.argv[1])
mime = {".wav": "audio/wav", ".ogg": "audio/ogg", ".oga": "audio/ogg", ".mp3": "audio/mp3", ".m4a": "audio/mp4"}.get(ruta.suffix.lower(), "audio/ogg")
print(f"audio: {ruta.name} ({ruta.stat().st_size} bytes, {mime})")
print("transcripción:", asyncio.run(voz.transcribir(ruta.read_bytes(), mime)))
