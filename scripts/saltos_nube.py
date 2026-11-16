"""Salida «--saltos» del coordinador DESPLEGADO: muestra cómo elige a cada agente (uno por pregunta) y cuándo dice «ninguno».

Uso:  python scripts/saltos_nube.py          (usa las direcciones de Heroku y las claves de secretos/claves_sistema.env)
Respeta la cuota gratuita de Gemini: espera PAUSA segundos (14 por defecto) entre preguntas.
"""
import asyncio
import datetime
import os
import sys
import uuid
from pathlib import Path

from dotenv import dotenv_values

try:  # almacén de certificados de Windows
    import truststore

    truststore.inject_into_ssl()
except ImportError:
    pass

RAIZ = Path(__file__).resolve().parent.parent
cfg = {**dotenv_values(RAIZ / ".env"), **dotenv_values(RAIZ / "secretos" / "claves_sistema.env")}
URLS = {
    "gerardo": "https://g3-a2a-gerardo-106ec27110d5.herokuapp.com",
    "diego": "https://g3-a2a-diego-835311cf3a46.herokuapp.com",
    "jaime": "https://g3-a2a-jaime-247f1f25d28a.herokuapp.com",
    "henry": "https://g3-a2a-henry-3278a379eb91.herokuapp.com",
}
os.environ["GOOGLE_API_KEY"] = cfg["GOOGLE_API_KEY"]
os.environ["MODELO"] = cfg.get("MODELO", "gemini-3.5-flash-lite")
os.environ["URLS_AGENTES"] = ",".join(URLS.values())
os.environ["CLAVES_AGENTES"] = ",".join(cfg[f"CLAVE_AGENTE_{n.upper()}"] for n in URLS)
sys.path.insert(0, str(RAIZ / "coordinador"))
from nucleo import EQUIPO, responder  # noqa: E402

PAUSA = float(os.environ.get("PAUSA", "14"))
PREGUNTAS = [
    "Tengo muchos archivos de datos desordenados en mi empresa, por donde parto para ordenarlos en la nube?",
    "Mi equipo de desarrollo entrega lento y con errores, como mejoro la forma en que trabajamos?",
    "En mi fabrica de alimentos se nos echan a perder lotes, que deberia controlar?",
    "Quiero hacer una app para el celular que funcione sin internet, que me conviene?",
    "Cual es la mejor receta de ceviche de reineta?",
]


async def main():
    print(f"# Saltos del coordinador (NUBE) · {datetime.datetime.now():%Y-%m-%d %H:%M}")
    await EQUIPO.refrescar(forzar=True)
    print("agentes leidos desde sus fichas publicas:", [a.nombre for a in EQUIPO.agentes])
    hilo = f"saltos:{uuid.uuid4()}"
    for i, p in enumerate(PREGUNTAS):
        if i:
            await asyncio.sleep(PAUSA)
        respuesta, saltos = await responder(p, hilo)
        print(f"\n>>> {p}")
        for s in saltos:
            print(f"    [salto] {s}")
        print(f"<<< {respuesta[:400]}{'…' if len(respuesta) > 400 else ''}")


asyncio.run(main())
