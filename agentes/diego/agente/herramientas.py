"""Herramientas del agente de Diego Vasquez (Grupo 3 · Taller A2A).

Una skill describe lo que el agente sabe hacer; una herramienta es una función que puede ejecutar.
Aquí la única herramienta consulta los apuntes de la persona que el agente representa.
"""
from langchain_core.tools import tool

APUNTES = {
    "conceptos": "1) Arquitectura medallón en Databricks/Delta Lake: bronze guarda lo crudo, silver lo limpio y conformado, gold lo listo para negocio. 2) ADF orquesta y mueve (pipelines, actividades, triggers); Databricks transforma. 3) Datos no estructurados (video, audio, imágenes): el archivo vive en el data lake y lo que se consulta es su metadato (fecha, origen, eventos detectados), catalogado en tablas.",
    "criterios": "Una buena solución: (a) pipelines idempotentes y re-ejecutables, (b) ingesta incremental cuando el volumen crece, (c) linaje y trazabilidad, (d) costo de cómputo controlado (autoescalado y apagado automático) y (e) gobierno y mínimo privilegio, con datos sensibles enmascarados.",
    "caso": "Caso de referencia: una carga nocturna completa de transacciones tardaba horas y fallaba a mitad sin poder reanudarse. Se migró a ingesta incremental orquestada con ADF y capas medallón en Databricks, con validaciones de calidad entre capas. Lección: diseñar para re-ejecutar sin duplicar vale más que optimizar la consulta.",
}


@tool
def consultar_mis_apuntes(tema: str = "") -> str:
    """Consulta mis apuntes: conceptos, criterios o caso. Vacío devuelve todos."""
    clave = tema.lower().strip()
    if not clave:
        return "\n".join(f"{nombre}: {texto}" for nombre, texto in APUNTES.items())
    return APUNTES.get(clave, "No tengo ese tema registrado. Consulta conceptos, criterios o caso.")


HERRAMIENTAS = [consultar_mis_apuntes]
