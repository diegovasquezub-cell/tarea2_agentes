"""Levanta los 4 agentes (8001-8004) y el coordinador (8000) en local. Ctrl+C los detiene a todos.

Lee GOOGLE_API_KEY y TELEGRAM_BOT_TOKEN de ./.env y las claves del sistema de ./secretos/claves_sistema.env
(ambos ignorados por git). Uso:  .venv/Scripts/python scripts/levantar_local.py
"""
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

from dotenv import dotenv_values

RAIZ = Path(__file__).resolve().parent.parent
cfg = {**dotenv_values(RAIZ / ".env"), **dotenv_values(RAIZ / "secretos" / "claves_sistema.env")}
AGENTES = [("gerardo", 8001), ("diego", 8002), ("jaime", 8003), ("henry", 8004)]
procs = []


def lanzar(carpeta: Path, puerto: int, extra: dict):
    env = {**os.environ, "GOOGLE_API_KEY": cfg["GOOGLE_API_KEY"], "MODELO": cfg.get("MODELO", "gemini-3.5-flash-lite"), **extra}
    return subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app:app", "--port", str(puerto), "--log-level", "warning"],
        cwd=carpeta, env=env,
    )


for slug, puerto in AGENTES:
    procs.append(lanzar(RAIZ / "agentes" / slug, puerto, {
        "AGENT_API_KEY": cfg[f"CLAVE_AGENTE_{slug.upper()}"], "URL_PUBLICA": f"http://127.0.0.1:{puerto}"}))
procs.append(lanzar(RAIZ / "coordinador", 8000, {
    "COORD_API_KEY": cfg["COORD_API_KEY"], "TELEGRAM_WEBHOOK_SECRET": cfg["TELEGRAM_WEBHOOK_SECRET"],
    "TELEGRAM_BOT_TOKEN": cfg["TELEGRAM_BOT_TOKEN"],
    "URLS_AGENTES": ",".join(f"http://127.0.0.1:{p}" for _, p in AGENTES),
    "CLAVES_AGENTES": ",".join(cfg[f"CLAVE_AGENTE_{s.upper()}"] for s, _ in AGENTES)}))
print("Agentes en 8001-8004, coordinador en 8000. Ctrl+C para detener.")
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    pass
finally:
    for p in procs:
        p.terminate()
