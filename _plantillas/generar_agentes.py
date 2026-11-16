"""Genera agentes/<slug>/ a partir de los proyectos del taller A2A y la plantilla común."""
import shutil
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
ORIGEN = RAIZ.parent / "Taller-A2A-main" / "Taller-A2A-main"
AGENTES = {  # slug: (carpeta origen, integrante)
    "gerardo": ("mi-agente", "Gerardo Herrera"),
    "diego": ("segundo-agente", "Diego Vasquez"),
    "jaime": ("tercer-agente", "Jaime Vidal"),
    "henry": ("cuarto-agente", "Henry Ambicho"),
}
REQ = """# runtime del agente (versiones validadas en el taller A2A)
fastapi>=0.115
uvicorn[standard]>=0.30
gunicorn>=22
langchain>=1.3,<2
langchain-core>=1.6,<2
langgraph>=1.2,<2
langchain-google-genai>=4.3,<5
pydantic>=2.7,<3
python-dotenv>=1.0
httpx>=0.27
"""
ENV = """# Copia este archivo a .env y completa los valores. NUNCA subas .env al repositorio.
# Clave de Gemini (https://aistudio.google.com/apikey). Valor ficticio:
GOOGLE_API_KEY=AIza-VALOR-FICTICIO
MODELO=gemini-3.5-flash-lite
# Clave que deben enviar los clientes en la cabecera X-API-Key (inventa una larga y aleatoria). Valor ficticio:
AGENT_API_KEY=clave-de-prueba-ficticia-cambiame
# Dirección pública del agente (la publica su ficha). En local: http://127.0.0.1:PUERTO
URL_PUBLICA=http://127.0.0.1:8001
"""
GITIGNORE = ".env\n.venv/\n__pycache__/\n*.pyc\n.pytest_cache/\n"

for slug, (carpeta, integrante) in AGENTES.items():
    d = RAIZ / "agentes" / slug
    (d / "agente").mkdir(parents=True, exist_ok=True)
    (d / "agente" / "__init__.py").write_text("")
    for f in ("prompts.py", "herramientas.py"):
        shutil.copy(ORIGEN / carpeta / "src" / "agente_viajes" / f, d / "agente" / f)
    shutil.copy(ORIGEN / carpeta / "blueprint.md", d / "blueprint.md")
    shutil.copy(Path(__file__).parent / "agente_app.py", d / "app.py")
    (d / "requirements.txt").write_text(REQ)
    (d / ".env.example").write_text(ENV)
    (d / ".gitignore").write_text(GITIGNORE)
    (d / "Procfile").write_text("web: gunicorn app:app -k uvicorn.workers.UvicornWorker --workers 1 --timeout 90 --bind 0.0.0.0:$PORT\n")
    (d / ".python-version").write_text("3.12\n")
    print("ok", slug)
