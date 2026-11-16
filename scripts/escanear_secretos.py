"""Busca secretos en lo que se entrega: archivos versionados en git y TODO el historial.

Uso:  python scripts/escanear_secretos.py
Compara contra los valores reales de ./.env y ./secretos/*.env (que NO se imprimen) y contra patrones comunes
(claves de Google «AIza...», tokens de bot de Telegram «123456789:AA...»). Termina con código 1 si encuentra algo.
Las capturas (imágenes) no se pueden escanear como texto: revísalas a mano antes de enviar.
"""
import re
import subprocess
import sys
from pathlib import Path

from dotenv import dotenv_values

RAIZ = Path(__file__).resolve().parent.parent
valores = set()
for f in [RAIZ / ".env", *sorted((RAIZ / "secretos").glob("*.env"))]:
    if f.exists():
        valores |= {
            v.strip()
            for k, v in dotenv_values(f).items()
            if v and len(v.strip()) >= 12 and re.search(r"KEY|TOKEN|SECRET|CLAVE", k, re.I)  # solo variables secretas
        }
PATRONES = {
    "clave de Google (AIza...)": re.compile(r"AIza[0-9A-Za-z_\-]{30,}"),
    "token de bot de Telegram": re.compile(r"\b\d{8,10}:[A-Za-z0-9_\-]{35}\b"),
}


def git(*args):
    return subprocess.run(["git", *args], cwd=RAIZ, capture_output=True, text=True, encoding="utf-8", errors="replace").stdout


hallazgos = []
archivos = [a for a in git("ls-files").splitlines() if not a.lower().endswith((".png", ".jpg", ".wav", ".ogg"))]
for a in archivos:
    try:
        txt = (RAIZ / a).read_text(encoding="utf-8", errors="ignore")
    except OSError:
        continue
    for v in valores:
        if v in txt:
            hallazgos.append((a, "valor real de .env / secretos"))
    for nombre, pat in PATRONES.items():
        for m in pat.findall(txt):
            if "FICTICIO" not in m.upper():
                hallazgos.append((a, nombre))
historial = git("log", "-p", "--all")
for v in valores:
    if v in historial:
        hallazgos.append(("(historial de git)", "valor real de .env / secretos"))
prohibidos = [a for a in git("ls-files").splitlines() if a.split("/")[-1] == ".env" or a.startswith(("secretos/", ".venv/"))]
hallazgos += [(a, "archivo que no debe versionarse") for a in prohibidos]

print(f"archivos revisados: {len(archivos)} · valores secretos comparados: {len(valores)} (no se imprimen)")
if hallazgos:
    for a, motivo in sorted(set(hallazgos)):
        print(f"  ENCONTRADO en {a}: {motivo}")
    sys.exit(1)
print("OK: no se encontraron secretos en los archivos versionados ni en el historial de git.")
