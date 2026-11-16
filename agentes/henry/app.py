"""Servicio A2A de un agente especialista (FastAPI).

Publica:
  GET  /.well-known/agent-card.json   ficha pública (qué hace y qué no, y su dirección en la nube)
  GET  /salud                         estado público
  POST /                              JSON-RPC 2.0 `message/send` (exige la clave del agente)
  POST /a2a                           alias de la ruta anterior

La clave se valida en el servidor con la variable AGENT_API_KEY (cabecera `X-API-Key` o
`Authorization: Bearer`). La memoria de cada conversación se guarda por `contextId`
(MemorySaver: un reinicio la borra, y está declarado como límite conocido).
"""
import hmac
import logging
import os
import re
import uuid

from dotenv import load_dotenv
from fastapi import FastAPI, Request, Security
from fastapi.security import APIKeyHeader
from fastapi.responses import FileResponse, JSONResponse
from pathlib import Path

load_dotenv()

from agente.herramientas import HERRAMIENTAS  # noqa: E402
import swagger_tema  # noqa: E402
from agente.perfil import COORDINADOR, HERMANOS, PERFIL  # noqa: E402
from agente.prompts import ESPECIALIDAD, NOMBRE, SYSTEM_VIAJES  # noqa: E402

log = logging.getLogger("agente")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")

AGENT_API_KEY = os.environ.get("AGENT_API_KEY", "")
URL_PUBLICA = os.environ.get("URL_PUBLICA", "http://127.0.0.1:" + os.environ.get("PORT", "8000")).rstrip("/")
MODELO = os.environ.get("MODELO", "gemini-3.5-flash-lite")
MAX_CHARS = 4000
FORMATO = (
    "\n\nFormato de salida: tu respuesta se muestra en un chat de texto plano (Telegram). No uses LaTeX ni signos $, "
    "ni asteriscos o almohadillas de Markdown; usa texto simple, numeración como «1)» y guiones. "
    "Conserva exactamente las cifras, unidades y supuestos del usuario y declara los supuestos que uses."
)

app = FastAPI(
    title=f"Agente {NOMBRE} (A2A)",
    docs_url=None,
    redoc_url=None,
    version="1.0.0",
    description=(
        "Servicio A2A de un agente especialista. La ficha (`/.well-known/agent-card.json`) y `/salud` son públicas; "
        "`POST /` (JSON-RPC `message/send`) exige la clave del agente: pulsa **Authorize** e ingresa la clave de prueba "
        "(cabecera `X-API-Key`). Límite conocido: el modelo corre en la capa gratuita de Gemini (15 solicitudes por minuto); "
        "si se supera, el agente responde un error claro de proveedor, no una respuesta falsa."
    ),
)
clave_docs = APIKeyHeader(name="X-API-Key", auto_error=False, description="Clave del agente (la valida el servidor).")
EJEMPLO_RPC = {
    "jsonrpc": "2.0", "id": 1, "method": "message/send",
    "params": {"message": {"kind": "message", "role": "user", "contextId": "mi-conversacion-1",
                           "messageId": "m1", "parts": [{"kind": "text", "text": "Hola, ¿en qué me puedes ayudar?"}]}},
}
RPC_DOC = {"requestBody": {"required": True, "content": {"application/json": {"schema": {"type": "object"}, "example": EJEMPLO_RPC}}}}

_graph = None


def get_graph():
    """El grafo se crea al primer uso: así /salud y la ficha responden aunque falte la clave del modelo."""
    global _graph
    if _graph is None:
        from langchain.agents import create_agent
        from langchain_google_genai import ChatGoogleGenerativeAI
        from langgraph.checkpoint.memory import MemorySaver

        _graph = create_agent(
            model=ChatGoogleGenerativeAI(model=MODELO, timeout=60, max_retries=5),
            tools=HERRAMIENTAS,
            system_prompt=SYSTEM_VIAJES + FORMATO,
            checkpointer=MemorySaver(),
            name="agente_" + NOMBRE.split()[0].lower(),
        )
    return _graph


def blueprint() -> dict:
    """Filas del blueprint del taller (blueprint.md, misma carpeta): rol, herramientas, autonomía y cuándo pide ayuda."""
    claves = {"Rol y alcance": "rol", "Herramientas": "herramientas", "Autonomía": "autonomia", "Cuándo pide ayuda": "cuando_pide_ayuda"}
    datos: dict = {}
    try:
        for linea in (Path(__file__).parent / "blueprint.md").read_text(encoding="utf-8").splitlines():
            celdas = [c.strip() for c in linea.strip().strip("|").split("|")]
            if len(celdas) >= 2 and celdas[0] in claves:
                datos[claves[celdas[0]]] = celdas[1]
    except Exception:
        pass
    return datos


def no_hace() -> str:
    """Texto «No hace: ...» del blueprint; si no está, usa uno general."""
    rol = blueprint().get("rol", "")
    m = re.search(r"No hace:\s*(.*)", rol, re.S)
    if m:
        return "NO hace: " + m.group(1).strip()
    return "NO hace: ejecutar cambios en sistemas reales, decidir por el negocio ni responder fuera de su especialidad."


def ficha() -> dict:
    descripcion = f"{PERFIL['resumen']} Cómo responde: {PERFIL['como_responde']} {no_hace()}"
    return {
        "protocolVersion": "0.3.0",
        "name": f"Agente {NOMBRE}",
        "description": descripcion,
        "url": URL_PUBLICA + "/",
        "preferredTransport": "JSONRPC",
        "version": "1.0.0",
        "provider": {"organization": "Grupo 3 · Curso 2 · Agentes en producción", "url": COORDINADOR},
        "documentationUrl": URL_PUBLICA + "/",
        "capabilities": {"streaming": False, "pushNotifications": False},
        "defaultInputModes": ["text/plain"],
        "defaultOutputModes": ["text/plain"],
        "securitySchemes": {"apiKey": {"type": "apiKey", "in": "header", "name": "X-API-Key"}},
        "security": [{"apiKey": []}],
        "skills": [
            {
                "id": f"skill-{i}",
                "name": sk["nombre"],
                "description": sk["descripcion"],
                "tags": [ESPECIALIDAD, PERFIL["rol"]],
                "examples": sk["ejemplos"],
                "inputModes": ["text/plain"],
                "outputModes": ["text/plain"],
            }
            for i, sk in enumerate(PERFIL["skills"], 1)
        ],
    }


def autorizado(request: Request) -> bool:
    if not AGENT_API_KEY:  # sin clave configurada el servicio rechaza todo (falla cerrado)
        return False
    dada = request.headers.get("x-api-key", "")
    if not dada:
        auth = request.headers.get("authorization", "")
        if auth.lower().startswith("bearer "):
            dada = auth[7:].strip()
    return hmac.compare_digest(dada.encode(), AGENT_API_KEY.encode())


def rpc_error(id_, code: int, message: str, status: int = 200) -> JSONResponse:
    return JSONResponse({"jsonrpc": "2.0", "id": id_, "error": {"code": code, "message": message}}, status_code=status)


@app.get("/.well-known/agent.json", include_in_schema=False)
@app.get("/.well-known/agent-card.json", summary="Ficha pública del agente")
def agent_card():
    return ficha()


PAGINA = Path(__file__).parent / "index.html"


@app.get("/", include_in_schema=False)
def pagina():
    """Página de inicio del agente: quién es, skills, blueprint y un chat de prueba directa (la clave la ingresa quien prueba)."""
    return FileResponse(PAGINA, media_type="text/html; charset=utf-8", headers={"Cache-Control": "no-cache"})


@app.get("/perfil", summary="Perfil público del agente (alimenta la página de inicio)")
def perfil():
    return {
        "nombre": f"Agente {NOMBRE}",
        "numero": PERFIL["numero"],
        "iniciales": PERFIL["iniciales"],
        "rol": PERFIL["rol"],
        "resumen": PERFIL["resumen"],
        "como_responde": PERFIL["como_responde"],
        "ideal_para": PERFIL["ideal_para"],
        "herramienta": PERFIL["herramienta"],
        "ejemplos_chat": PERFIL["ejemplos_chat"],
        "blueprint": blueprint(),
        "hermanos": HERMANOS,
        "coordinador": COORDINADOR,
        "url": URL_PUBLICA,
    }


@app.get("/docs", include_in_schema=False)
def docs():
    return swagger_tema.pagina(
        app, f"Agente {NOMBRE}",
        "API A2A del agente: ficha pública, estado y message/send (con clave). Pulsa Authorize e ingresa la clave de prueba.",
        "/", "Página del agente", PERFIL["iniciales"],
    )


@app.get("/salud")
def salud():
    return {"estado": "ok", "agente": f"Agente {NOMBRE}", "modelo_configurado": bool(os.environ.get("GOOGLE_API_KEY"))}


def texto_de(parts) -> str:
    return "\n".join(p.get("text", "") for p in parts if isinstance(p, dict) and p.get("kind", "text") == "text").strip()


@app.post("/a2a", include_in_schema=False)
@app.post("/", dependencies=[Security(clave_docs)], openapi_extra=RPC_DOC, summary="A2A message/send",
          description="JSON-RPC 2.0 `message/send`. 401 sin clave o con clave incorrecta.")
async def message_send(request: Request):
    if not autorizado(request):
        return JSONResponse({"error": "No autorizado: falta la clave del agente o es incorrecta."}, status_code=401)
    try:
        body = await request.json()
    except Exception:
        return rpc_error(None, -32700, "JSON inválido.", 400)
    if not isinstance(body, dict):
        return rpc_error(None, -32600, "Solicitud inválida.", 400)
    id_ = body.get("id")
    if body.get("method") != "message/send":
        return rpc_error(id_, -32601, "Método no soportado. Usa message/send.")
    msg = (body.get("params") or {}).get("message") or {}
    pregunta = texto_de(msg.get("parts") or [])
    if not pregunta:
        return rpc_error(id_, -32602, "El mensaje no contiene texto que pueda leer.")
    if len(pregunta) > MAX_CHARS:
        return rpc_error(id_, -32602, f"El mensaje supera el máximo de {MAX_CHARS} caracteres.")
    context_id = msg.get("contextId") or str(uuid.uuid4())
    try:
        resultado = await get_graph().ainvoke(
            {"messages": [{"role": "user", "content": pregunta}]},
            config={"configurable": {"thread_id": context_id}},
        )
        contenido = resultado["messages"][-1].content
        if isinstance(contenido, list):
            contenido = "".join(b.get("text", "") if isinstance(b, dict) else str(b) for b in contenido)
        respuesta = str(contenido).strip()
        if not respuesta:
            return rpc_error(id_, -32000, "El modelo no devolvió respuesta.")
    except Exception as exc:  # fallas del proveedor: se informan, nunca se presentan como éxito
        log.exception("fallo del modelo")
        return rpc_error(id_, -32000, f"El proveedor del modelo falló ({type(exc).__name__}). Intenta de nuevo.")
    log.info("message/send contexto=%s pregunta=%r", context_id[:8], pregunta[:80])
    return {
        "jsonrpc": "2.0",
        "id": id_,
        "result": {
            "kind": "message",
            "role": "agent",
            "messageId": str(uuid.uuid4()),
            "contextId": context_id,
            "parts": [{"kind": "text", "text": respuesta}],
        },
    }
