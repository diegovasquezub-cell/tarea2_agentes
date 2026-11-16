"""Prueba directa a cada agente (sin pasar por el coordinador): ficha pública, rechazo sin clave y respuesta con clave.

Uso:  python scripts/probar_agentes_directo.py [--local]
Por defecto prueba las direcciones de Heroku; con --local prueba 127.0.0.1:8001-8004.
Lee las claves de secretos/claves_sistema.env (ignorado por git; la salida NO imprime ninguna clave).
Respeta la cuota gratuita de Gemini (15 solicitudes por minuto): espera PAUSA segundos entre agentes.
"""
import datetime
import os
import sys
import time
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
LOCAL = "--local" in sys.argv
URLS = {
    "gerardo": "https://g3-a2a-gerardo-106ec27110d5.herokuapp.com",
    "diego": "https://g3-a2a-diego-835311cf3a46.herokuapp.com",
    "jaime": "https://g3-a2a-jaime-247f1f25d28a.herokuapp.com",
    "henry": "https://g3-a2a-henry-3278a379eb91.herokuapp.com",
}
if LOCAL:
    URLS = {n: f"http://127.0.0.1:{8001 + i}" for i, n in enumerate(URLS)}
PREGUNTAS = {
    "gerardo": "Presentate en dos frases y dime que NO haces.",
    "diego": "Tengo datos desordenados en la nube, por donde parto? Responde breve.",
    "jaime": "Si produzco 1.250 kg por turno con 3 turnos y 2,5% de merma, cuantos kg buenos salen por dia?",
    "henry": "Que me conviene para una app movil que funcione sin internet? Responde breve.",
}
PAUSA = float(os.environ.get("PAUSA", "10"))

print(f"# Prueba directa a cada agente · {datetime.datetime.now():%Y-%m-%d %H:%M} · {'LOCAL' if LOCAL else 'NUBE (Heroku)'}")
for nombre, base in URLS.items():
    print(f"\n## Agente {nombre}  {base}")
    ficha = httpx.get(base + "/.well-known/agent-card.json", timeout=30).json()
    print(f"  ficha pública: name={ficha['name']!r} url={ficha['url']!r} skills={len(ficha['skills'])}")
    print(f"  ficha dice qué NO hace: {'NO hace' in ficha['description']}")
    rpc = {"jsonrpc": "2.0", "id": 1, "method": "message/send", "params": {"message": {
        "kind": "message", "role": "user", "contextId": f"directo-{nombre}", "messageId": "m1",
        "parts": [{"kind": "text", "text": PREGUNTAS[nombre]}]}}}
    print("  sin clave        ->", httpx.post(base + "/", json=rpc, timeout=30).status_code)
    print("  clave incorrecta ->", httpx.post(base + "/", json=rpc, headers={"X-API-Key": "incorrecta"}, timeout=30).status_code)
    time.sleep(PAUSA)
    t0 = time.time()
    r = httpx.post(base + "/", json=rpc, headers={"X-API-Key": cfg[f"CLAVE_AGENTE_{nombre.upper()}"]}, timeout=120)
    d = r.json()
    print(f"  con clave        -> {r.status_code} en {time.time() - t0:.1f}s")
    print(f"  pregunta: {PREGUNTAS[nombre]}")
    texto = "\n".join(p["text"] for p in d.get("result", {}).get("parts", [])) or str(d.get("error"))
    print("  respuesta:\n    " + texto.replace("\n", "\n    "))
