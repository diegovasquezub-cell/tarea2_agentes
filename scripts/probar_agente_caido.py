"""Caso 9: un agente está apagado y se le hace una pregunta de su tema; los otros agentes deben seguir respondiendo.

Uso (el apagado y encendido se hacen con el CLI de Heroku, ver README):
    heroku ps:scale web=0 -a g3-a2a-jaime
    python scripts/probar_agente_caido.py jaime            # pregunta al caído y a otro agente
    heroku ps:scale web=1 -a g3-a2a-jaime
    python scripts/probar_agente_caido.py jaime --recuperado
Respeta la cuota gratuita de Gemini: espera PAUSA segundos (14) entre preguntas.
"""
import datetime
import os
import sys
import time
import uuid
from pathlib import Path

import httpx

try:  # almacén de certificados de Windows
    import truststore

    truststore.inject_into_ssl()
except ImportError:
    pass
from dotenv import dotenv_values

RAIZ = Path(__file__).resolve().parent.parent
cfg = dotenv_values(RAIZ / "secretos" / "claves_sistema.env")
BASE = os.environ.get("COORDINADOR_URL", "https://g3-a2a-coordinador-22655cb5eaa9.herokuapp.com")
AGENTES = {
    "gerardo": ("https://g3-a2a-gerardo-106ec27110d5.herokuapp.com", "Mi equipo de desarrollo entrega lento y con errores, ¿qué mejoro primero?"),
    "diego": ("https://g3-a2a-diego-835311cf3a46.herokuapp.com", "Tengo datos desordenados en la nube, ¿por dónde parto?"),
    "jaime": ("https://g3-a2a-jaime-247f1f25d28a.herokuapp.com", "En mi fábrica de alimentos se nos echan a perder lotes, ¿qué debería controlar?"),
    "henry": ("https://g3-a2a-henry-3278a379eb91.herokuapp.com", "Quiero una app móvil que funcione sin internet, ¿qué me conviene?"),
}
PAUSA = float(os.environ.get("PAUSA", "14"))
caido = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else "jaime"
recuperado = "--recuperado" in sys.argv
otro = "henry" if caido != "henry" else "diego"
conv = str(uuid.uuid4())


def salud(url):
    try:
        return httpx.get(url + "/salud", timeout=15).status_code
    except Exception as exc:
        return type(exc).__name__


def preguntar(texto):
    time.sleep(PAUSA)
    r = httpx.post(f"{BASE}/chat", json={"mensaje": texto, "conversacion_id": conv}, headers={"X-API-Key": cfg["COORD_API_KEY"]}, timeout=180)
    d = r.json()
    print(f"\n>>> {texto}")
    for s in d.get("saltos", []):
        print(f"    [salto] {s}")
    print(f"<<< {d.get('respuesta', d)[:500]}")


print(f"# Caso 9 · {'agente recuperado' if recuperado else 'agente apagado'} · NUBE · {datetime.datetime.now():%Y-%m-%d %H:%M}")
for nombre, (url, _) in AGENTES.items():
    estado = salud(url)
    print(f"  /salud de {nombre}: {estado}{'  <- apagado' if estado != 200 else ''}")
preguntar(AGENTES[caido][1])
if not recuperado:
    print(f"\n-- los otros agentes siguen respondiendo: se le pregunta a {otro} --")
    preguntar(AGENTES[otro][1])
