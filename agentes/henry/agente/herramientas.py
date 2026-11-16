"""Herramientas del agente de Henry Ambicho (Grupo 3 · Taller A2A).

Una skill describe lo que el agente sabe hacer; una herramienta es una función que puede ejecutar.
Aquí la única herramienta consulta los apuntes de la persona que el agente representa.
"""
from langchain_core.tools import tool

APUNTES = {
    "conceptos": "1) Nativo (Swift/Kotlin), multiplataforma o web/PWA: cambian el rendimiento, el acceso al hardware y el costo de mantener dos bases de código. 2) Offline-first: guardar en local y sincronizar después, resolviendo los conflictos. 3) Backend para móvil: API o BFF en Node.js, notificaciones push y tiempo real con WebSockets.",
    "criterios": "Una buena solución: (a) funciona con mala conectividad, (b) cuida la batería y los datos, con una frecuencia adaptativa de geolocalización, (c) seguridad: tokens y nada sensible sin cifrar en el dispositivo, (d) consentimiento explícito para usar la ubicación y (e) MVP medible y luego iteración.",
    "caso": "Caso de referencia: una app de seguimiento de repartidores enviaba la ubicación GPS cada segundo; agotaba la batería y saturaba el backend. Se pasó a un envío adaptativo (frecuente en movimiento, pausado cuando está detenido), una cola local offline y WebSocket solo para el panel de despacho. Lección: en móvil, lo escaso es la batería y la red.",
}


@tool
def consultar_mis_apuntes(tema: str = "") -> str:
    """Consulta mis apuntes: conceptos, criterios o caso. Vacío devuelve todos."""
    clave = tema.lower().strip()
    if not clave:
        return "\n".join(f"{nombre}: {texto}" for nombre, texto in APUNTES.items())
    return APUNTES.get(clave, "No tengo ese tema registrado. Consulta conceptos, criterios o caso.")


HERRAMIENTAS = [consultar_mis_apuntes]
