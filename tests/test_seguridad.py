"""Pruebas sin red ni modelo: ficha pública, /salud, rechazo sin clave y entradas inválidas."""
import importlib
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

RAIZ = Path(__file__).resolve().parent.parent
AGENTES = ["gerardo", "diego", "jaime", "henry"]


def cargar(carpeta: Path, monkeypatch, **env):
    for k, v in env.items():
        monkeypatch.setenv(k, v)
    for m in [m for m in sys.modules if m == "agente" or m.startswith("agente.") or m in ("app", "nucleo")]:
        del sys.modules[m]
    monkeypatch.syspath_prepend(str(carpeta))
    return importlib.import_module("app")


@pytest.mark.parametrize("slug", AGENTES)
def test_agente(slug, monkeypatch):
    m = cargar(RAIZ / "agentes" / slug, monkeypatch, AGENT_API_KEY="k-test", URL_PUBLICA=f"https://{slug}.example.com")
    c = TestClient(m.app)
    ficha = c.get("/.well-known/agent-card.json").json()
    assert ficha["url"] == f"https://{slug}.example.com/"          # la ficha publica su dirección en la nube
    assert ficha["skills"] and "NO hace" in ficha["description"]    # dice qué hace y qué no
    assert c.get("/salud").status_code == 200
    pagina = c.get("/")                                                        # página de inicio, sin claves embebidas
    assert pagina.status_code == 200 and "Quién es este agente" in pagina.text and "AIza" not in pagina.text
    perfil = c.get("/perfil").json()
    assert perfil["blueprint"]["rol"] and len(perfil["hermanos"]) == 3 and perfil["ejemplos_chat"]
    assert all(sk["examples"] for sk in ficha["skills"]) and len(ficha["description"]) > 300   # ficha descriptiva
    esquema = c.get("/openapi.json").json()                                    # Swagger disponible y documenta la clave
    assert "apiKey" in str(esquema["components"]["securitySchemes"]) and c.get("/docs").status_code == 200
    rpc = {"jsonrpc": "2.0", "id": 1, "method": "message/send",
           "params": {"message": {"role": "user", "parts": [{"kind": "text", "text": "hola"}]}}}
    assert c.post("/", json=rpc).status_code == 401                              # sin clave
    assert c.post("/", json=rpc, headers={"X-API-Key": "mala"}).status_code == 401  # clave incorrecta
    ok = {"X-API-Key": "k-test"}
    vacio = {**rpc, "params": {"message": {"role": "user", "parts": []}}}
    assert "error" in c.post("/", json=vacio, headers=ok).json()                  # entrada inválida
    assert "error" in c.post("/", json={**rpc, "method": "otra"}, headers=ok).json()
    assert c.post("/", content="no-json", headers=ok).status_code == 400


def test_agente_sin_clave_configurada_falla_cerrado(monkeypatch):
    monkeypatch.delenv("AGENT_API_KEY", raising=False)
    m = cargar(RAIZ / "agentes" / "gerardo", monkeypatch)
    m.AGENT_API_KEY = ""
    assert TestClient(m.app).post("/", json={}, headers={"X-API-Key": ""}).status_code == 401


def test_coordinador(monkeypatch):
    m = cargar(RAIZ / "coordinador", monkeypatch, COORD_API_KEY="c-test", TELEGRAM_WEBHOOK_SECRET="s-test",
               URLS_AGENTES="http://127.0.0.1:9", CLAVES_AGENTES="x")
    m.COORD_API_KEY, m.WEBHOOK_SECRET = "c-test", "s-test"
    c = TestClient(m.app)
    assert c.get("/salud").status_code == 200
    assert c.get("/docs").status_code == 200 and "/chat" in c.get("/openapi.json").json()["paths"]
    pag = c.get("/")                                                            # chat web + diagrama, sin claves embebidas
    assert pag.status_code == 200 and "Arquitectura en vivo" in pag.text and "AIza" not in pag.text
    assert c.get("/estado").json()["coordinador"] == "ok"
    assert c.post("/chat", json={"mensaje": "hola"}).status_code == 401
    assert c.post("/chat", json={"mensaje": "hola"}, headers={"X-API-Key": "mala"}).status_code == 401
    assert c.post("/telegram", json={}).status_code == 401
    assert c.post("/telegram", json={}, headers={"X-Telegram-Bot-Api-Secret-Token": "mala"}).status_code == 401
    assert c.post("/chat", json={}, headers={"X-API-Key": "c-test"}).status_code == 422
    assert c.post("/chat", json={"mensaje": "x" * 5000}, headers={"X-API-Key": "c-test"}).status_code == 422
