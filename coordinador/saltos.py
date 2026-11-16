"""Salida de terminal «--saltos»: muestra cómo el coordinador elige a cada agente.

Uso:  python saltos.py "pregunta 1" "pregunta 2" ...      (todas en la misma conversación)
Usa URLS_AGENTES / CLAVES_AGENTES / GOOGLE_API_KEY del entorno o del .env (en local o contra la nube).
"""
import asyncio
import os
import sys
import uuid

from dotenv import load_dotenv

load_dotenv()

from nucleo import EQUIPO, responder  # noqa: E402

PAUSA = float(os.environ.get("PAUSA", "14"))  # Gemini gratis: 15 solicitudes/minuto


async def main(preguntas: list[str]):
    await EQUIPO.refrescar(forzar=True)
    hilo = f"saltos:{uuid.uuid4()}"
    for i, p in enumerate(preguntas):
        if i:
            await asyncio.sleep(PAUSA)
        respuesta, saltos = await responder(p, hilo)
        print(f"\n>>> {p}")
        for s in saltos:
            print(f"    [salto] {s}")
        print(f"<<< {respuesta}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit('Uso: python saltos.py "pregunta" ["otra pregunta" ...]')
    asyncio.run(main(sys.argv[1:]))
