"""Genera agentes/<slug>/ a partir de los proyectos del taller A2A y la plantilla común."""
import pprint
import re
import shutil
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).parent))
from perfiles import PERFILES  # noqa: E402

URL_COORD = "https://g3-a2a-coordinador-22655cb5eaa9.herokuapp.com"
ORIGEN = RAIZ.parent / "Taller-A2A-main" / "Taller-A2A-main"
AGENTES = {  # slug: (carpeta origen, integrante)
    "gerardo": ("mi-agente", "Gerardo Herrera"),
    "diego": ("segundo-agente", "Diego Vasquez"),
    "jaime": ("tercer-agente", "Jaime Vidal"),
    "henry": ("cuarto-agente", "Henry Ambicho"),
}
URLS_NUBE = {
    "gerardo": "https://g3-a2a-gerardo-106ec27110d5.herokuapp.com",
    "diego": "https://g3-a2a-diego-835311cf3a46.herokuapp.com",
    "jaime": "https://g3-a2a-jaime-247f1f25d28a.herokuapp.com",
    "henry": "https://g3-a2a-henry-3278a379eb91.herokuapp.com",
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
    bp = (ORIGEN / carpeta / "blueprint.md").read_text(encoding="utf-8")
    bp = re.sub(r"\| Dónde se ejecuta\s*\|[^\n]*",
                f"| Dónde se ejecuta  | Nube (Heroku): {URLS_NUBE[slug]} · ficha en /.well-known/agent-card.json · local: puerto 800X (ver README) |", bp)
    bp = bp.replace("Taller práctico A2A", "Taller práctico A2A · entrega del sistema de agentes")
    (d / "blueprint.md").write_text(bp, encoding="utf-8")
    shutil.copy(Path(__file__).parent / "agente_app.py", d / "app.py")
    # perfil descriptivo + página de inicio (mismo CSS que el coordinador)
    perfil = PERFILES[slug]
    hermanos = [{"nombre": "Agente " + PERFILES[o]["nombre_corto"], "url": URLS_NUBE[o], "iniciales": PERFILES[o]["iniciales"], "numero": PERFILES[o]["numero"]}
                for o in AGENTES if o != slug]
    (d / "agente" / "perfil.py").write_text(
        '"""Perfil descriptivo del agente (generado desde _plantillas/perfiles.py)."""\n'
        f"PERFIL = {pprint.pformat(perfil, width=110, sort_dicts=False)}\n"
        f"HERMANOS = {pprint.pformat(hermanos, width=110, sort_dicts=False)}\n"
        f"COORDINADOR = {URL_COORD!r}\n", encoding="utf-8")
    css = re.search(r"<style>.*?</style>", (RAIZ / "coordinador" / "static" / "index.html").read_text(encoding="utf-8"), re.S).group(0)
    (d / "index.html").write_text((Path(__file__).parent / "agente_index.html").read_text(encoding="utf-8").replace("{{CSS}}", css), encoding="utf-8")
    shutil.copy(Path(__file__).parent / "swagger_tema.py", d / "swagger_tema.py")
    (d / "requirements.txt").write_text(REQ)
    (d / ".env.example").write_text(ENV)
    (d / ".gitignore").write_text(GITIGNORE)
    (d / "Procfile").write_text("web: gunicorn app:app -k uvicorn.workers.UvicornWorker --workers 1 --timeout 90 --bind 0.0.0.0:$PORT\n")
    (d / ".python-version").write_text("3.12\n")
    print("ok", slug)

shutil.copy(Path(__file__).parent / "swagger_tema.py", RAIZ / "coordinador" / "swagger_tema.py")
print("ok coordinador (swagger_tema)")
