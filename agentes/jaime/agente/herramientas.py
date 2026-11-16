"""Herramientas del agente de Jaime Vidal (Grupo 3 · Taller A2A).

Una skill describe lo que el agente sabe hacer; una herramienta es una función que puede ejecutar.
Aquí la única herramienta consulta los apuntes de la persona que el agente representa.
"""
from langchain_core.tools import tool

APUNTES = {
    "conceptos": "1) FEFO frente a FIFO: en alimentos sale primero lo que vence antes. 2) HACCP: peligros, puntos críticos de control, límites, monitoreo y acciones correctivas. Inocuidad no es lo mismo que calidad. 3) Indicadores de operación: OEE (disponibilidad × rendimiento × calidad), merma, rotación de inventario y OTIF.",
    "criterios": "Una buena solución: (a) primero la inocuidad, después el costo, (b) trazabilidad por lote, del proveedor al cliente, (c) cada mejora tiene un KPI y una meta, (d) un estándar escrito y el turno capacitado y (e) cadena de frío y rotación FEFO.",
    "caso": "Caso de referencia: una bodega con mermas por vencimiento ordenaba por fecha de llegada (FIFO). Se pasó a FEFO, con fecha de vencimiento visible, conteo cíclico semanal de los productos de alta rotación y una alerta de «próximo a vencer» para promocionar o donar. Lección: la merma se controla con disciplina diaria y un indicador a la vista.",
}


@tool
def consultar_mis_apuntes(tema: str = "") -> str:
    """Consulta mis apuntes: conceptos, criterios o caso. Vacío devuelve todos."""
    clave = tema.lower().strip()
    if not clave:
        return "\n".join(f"{nombre}: {texto}" for nombre, texto in APUNTES.items())
    return APUNTES.get(clave, "No tengo ese tema registrado. Consulta conceptos, criterios o caso.")


HERRAMIENTAS = [consultar_mis_apuntes]
