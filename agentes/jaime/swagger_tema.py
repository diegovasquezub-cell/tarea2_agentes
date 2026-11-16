"""Swagger UI con la paleta del sistema (atardecer azul/púrpura, cobre y estelas de luz).

Se sirve en /docs reemplazando la página por defecto de FastAPI: mismo Swagger UI, mismo /openapi.json, otro tema.
"""
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import HTMLResponse

CSS = """
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Montserrat:wght@600;700;800&display=swap" rel="stylesheet">
<style>
  :root{--bg:#080b1c;--panel:rgba(13,17,43,.72);--panel2:rgba(7,10,28,.66);--line:rgba(255,255,255,.15);--line2:rgba(255,255,255,.08);
    --text:#f5f2ef;--muted:#aaa7c4;--accent:#e29a5b;--accent2:#ff7a2f;--blue:#6f86ff;--ok:#3ddc84;--warn:#ffb454;--bad:#ff5a6b;
    --head:"Montserrat","Segoe UI",system-ui,Arial,sans-serif;--font:"Inter","Segoe UI",system-ui,Arial,sans-serif}
  html,body{margin:0;background:#0a0e29}
  body{color:var(--text);font-family:var(--font);min-height:100vh;
    background:radial-gradient(1100px 520px at 88% -8%,rgba(226,154,91,.24),transparent 60%),radial-gradient(900px 520px at 6% 4%,rgba(111,134,255,.20),transparent 60%),linear-gradient(180deg,#0a0e29 0%,#1a1440 36%,#0c0b20 100%);background-attachment:fixed}
  body::before{content:"";position:fixed;left:0;right:0;bottom:0;height:34vh;z-index:-1;pointer-events:none;opacity:.9;
    background:linear-gradient(90deg,transparent 0,rgba(255,90,40,.55) 30%,rgba(255,170,80,.5) 55%,rgba(100,125,255,.55) 82%,transparent 100%) 0 58%/100% 2px no-repeat,
    linear-gradient(90deg,transparent,rgba(255,150,60,.45) 38%,rgba(130,150,255,.4) 76%,transparent) 0 70%/100% 1px no-repeat,
    linear-gradient(90deg,transparent 4%,rgba(232,64,42,.45) 28%,rgba(255,205,130,.4) 62%,transparent 96%) 0 82%/100% 3px no-repeat}
  /* cabecera */
  .g3-top{display:flex;align-items:center;gap:14px;padding:14px 28px;border-bottom:1px solid var(--line);background:rgba(7,10,28,.6);backdrop-filter:blur(14px)}
  .g3-logo{width:38px;height:38px;background:linear-gradient(145deg,#f0b27a,#a85f2a);display:grid;place-items:center;color:#1a0e05;font:800 13px var(--head);clip-path:polygon(50% 0,100% 28%,88% 100%,12% 100%,0 28%)}
  .g3-top b{font:800 14px var(--head);letter-spacing:.2em;text-transform:uppercase;display:block}
  .g3-top small{color:var(--accent);font:600 11px var(--head);letter-spacing:.18em;text-transform:uppercase}
  .g3-top a{margin-left:auto;color:var(--text);text-decoration:none;border:1px solid var(--line);padding:7px 14px;border-radius:3px;font:600 11.5px var(--head);letter-spacing:.12em;text-transform:uppercase}
  .g3-top a:hover{border-color:var(--accent);color:var(--accent)}
  .g3-hero{position:relative;overflow:hidden;border-bottom:1px solid var(--line);padding:22px 28px 34px}
  .g3-hero::after{content:"";position:absolute;left:0;right:0;bottom:14px;height:2px;background:linear-gradient(90deg,transparent,rgba(255,90,40,.9) 25%,rgba(255,170,80,.9) 55%,rgba(100,125,255,.9) 85%,transparent);box-shadow:0 7px 0 -1px rgba(255,150,60,.5)}
  .g3-hero .eb{font:600 11.5px var(--head);letter-spacing:.3em;text-transform:uppercase;color:var(--accent);margin:0 0 6px}
  .g3-hero h1{margin:0;font:800 clamp(22px,3.2vw,36px)/1.1 var(--head);letter-spacing:.07em;text-transform:uppercase;color:#fff}
  .g3-hero p{margin:10px 0 0;max-width:820px;color:var(--muted);font-size:14px}
  /* swagger ui */
  .swagger-ui{font-family:var(--font);color:var(--text)}
  .swagger-ui .wrapper{max-width:1180px;padding:0 28px}
  .swagger-ui .info{margin:26px 0 8px}
  .swagger-ui .info .title{font:800 24px var(--head);letter-spacing:.06em;text-transform:uppercase;color:#fff}
  .swagger-ui .info .title small{background:linear-gradient(90deg,#b8763e,#ecb07a);color:#1b1007;border-radius:0;font:700 10px var(--head);letter-spacing:.1em;padding:3px 10px}
  .swagger-ui .info .title small.version-stamp{background:linear-gradient(90deg,#6f86ff,#aab6ff);color:#0a0e28}
  .swagger-ui .info p,.swagger-ui .info li,.swagger-ui .info table,.swagger-ui .markdown p,.swagger-ui .renderedMarkdown p{color:var(--muted);font-size:14px}
  .swagger-ui .info a,.swagger-ui .markdown a{color:var(--accent)}
  .swagger-ui .markdown code,.swagger-ui .renderedMarkdown code{background:rgba(255,255,255,.08);color:#ffc9a0;border-radius:3px;padding:1px 6px}
  .swagger-ui .scheme-container{background:var(--panel);backdrop-filter:blur(14px);border:1px solid var(--line);border-radius:6px;box-shadow:none;margin:14px 0 6px;padding:16px 20px}
  .swagger-ui .btn{border-radius:3px;font-family:var(--head);letter-spacing:.1em;text-transform:uppercase;font-weight:700;font-size:11.5px;box-shadow:none}
  .swagger-ui .btn.authorize{color:var(--accent);border:1px solid var(--accent);background:transparent}
  .swagger-ui .btn.authorize svg{fill:var(--accent)}
  .swagger-ui .btn.authorize:hover{background:rgba(226,154,91,.12)}
  .swagger-ui .btn.execute{background:linear-gradient(135deg,#f0b27a,#d9702a);border:0;color:#1b0e05}
  .swagger-ui .btn.execute:hover{filter:brightness(1.1)}
  .swagger-ui .btn.try-out__btn{color:var(--text);border:1px solid var(--line);background:transparent}
  .swagger-ui .btn.try-out__btn:hover{border-color:var(--accent);color:var(--accent)}
  .swagger-ui .btn.cancel{color:var(--bad);border-color:var(--bad);background:transparent}
  .swagger-ui .btn.btn-clear{color:var(--muted);border-color:var(--line)}
  .swagger-ui select{background:var(--panel2);color:var(--text);border:1px solid var(--line);border-radius:3px}
  .swagger-ui input[type=text],.swagger-ui input[type=password],.swagger-ui input[type=search],.swagger-ui input[type=email],.swagger-ui textarea{background:var(--panel2);color:var(--text);border:1px solid var(--line);border-radius:3px}
  .swagger-ui input:focus,.swagger-ui textarea:focus{border-color:var(--accent);outline:none;box-shadow:0 0 0 3px rgba(226,154,91,.15)}
  .swagger-ui .opblock-tag{border-bottom:1px solid var(--line2);color:var(--text);font-family:var(--head);letter-spacing:.14em;text-transform:uppercase;font-size:14px}
  .swagger-ui .opblock-tag small{color:var(--muted);font-family:var(--font);text-transform:none;letter-spacing:0}
  .swagger-ui .opblock-tag:hover{background:rgba(255,255,255,.03)}
  .swagger-ui .opblock{background:var(--panel);backdrop-filter:blur(10px);border-radius:6px;box-shadow:none;border:1px solid var(--line)}
  .swagger-ui .opblock .opblock-summary{border-bottom:0}
  .swagger-ui .opblock .opblock-summary-method{font-family:var(--head);border-radius:2px;letter-spacing:.08em;text-shadow:none;min-width:72px;color:#fff}
  .swagger-ui .opblock .opblock-summary-path,.swagger-ui .opblock .opblock-summary-path__deprecated{color:var(--text);font-family:ui-monospace,Consolas,monospace;font-size:14px}
  .swagger-ui .opblock .opblock-summary-description{color:var(--muted)}
  .swagger-ui .opblock.opblock-get{background:rgba(111,134,255,.07);border-color:rgba(111,134,255,.55)}
  .swagger-ui .opblock.opblock-get .opblock-summary-method{background:linear-gradient(135deg,#4a63e0,#6f86ff)}
  .swagger-ui .opblock.opblock-get .opblock-summary{border-color:rgba(111,134,255,.55)}
  .swagger-ui .opblock.opblock-post{background:rgba(255,122,47,.07);border-color:rgba(255,122,47,.6)}
  .swagger-ui .opblock.opblock-post .opblock-summary-method{background:linear-gradient(135deg,#c9601f,#ff7a2f)}
  .swagger-ui .opblock.opblock-put{background:rgba(226,154,91,.07);border-color:rgba(226,154,91,.55)}
  .swagger-ui .opblock.opblock-put .opblock-summary-method{background:linear-gradient(135deg,#a85f2a,#e29a5b)}
  .swagger-ui .opblock.opblock-delete{background:rgba(255,90,107,.07);border-color:rgba(255,90,107,.55)}
  .swagger-ui .opblock.opblock-delete .opblock-summary-method{background:linear-gradient(135deg,#d63a4f,#ff5a6b)}
  .swagger-ui .opblock .opblock-section-header{background:rgba(7,10,28,.6);box-shadow:none;border-bottom:1px solid var(--line2)}
  .swagger-ui .opblock .opblock-section-header h4,.swagger-ui .opblock-section-header label{color:var(--accent);font-family:var(--head);letter-spacing:.14em;text-transform:uppercase;font-size:12px}
  .swagger-ui .opblock-description-wrapper p,.swagger-ui .opblock-external-docs-wrapper p,.swagger-ui .opblock-title_normal p,.swagger-ui .opblock-description-wrapper h4{color:var(--muted)}
  .swagger-ui table thead tr td,.swagger-ui table thead tr th,.swagger-ui .parameter__name,.swagger-ui .parameter__type,.swagger-ui .parameter__in,.swagger-ui .response-col_status,.swagger-ui .response-col_description,.swagger-ui .response-col_links,.swagger-ui .tab li,.swagger-ui label,.swagger-ui .col_header{color:var(--text);border-color:var(--line2)}
  .swagger-ui .parameter__name.required span,.swagger-ui .parameter__name.required::after{color:var(--bad)}
  .swagger-ui .parameter__in,.swagger-ui .parameter__extension{color:var(--muted)}
  .swagger-ui .responses-inner h4,.swagger-ui .responses-inner h5{color:var(--text)}
  .swagger-ui .tab li button.tablinks{color:var(--muted)} .swagger-ui .tab li.active button.tablinks{color:var(--accent)}
  .swagger-ui .opblock-body pre.microlight,.swagger-ui .highlight-code>.microlight,.swagger-ui .highlight-code pre{background:#0a0d24!important;border:1px solid var(--line2);border-radius:4px;color:#ffe6cf}
  .swagger-ui .copy-to-clipboard{background:rgba(255,255,255,.1);border-radius:3px}
  .swagger-ui .response-control-media-type__accept-message{color:var(--ok)}
  .swagger-ui .responses-table .response .response-col_status{color:var(--accent)}
  .swagger-ui .model-box,.swagger-ui .model,.swagger-ui .model-title,.swagger-ui .prop-type,.swagger-ui .prop-format,.swagger-ui section.models h4,.swagger-ui .models-control{color:var(--text)}
  .swagger-ui section.models{background:var(--panel);border:1px solid var(--line);border-radius:6px}
  .swagger-ui section.models.is-open h4{border-bottom:1px solid var(--line2)}
  .swagger-ui section.models .model-container{background:rgba(7,10,28,.55);border-radius:4px}
  .swagger-ui svg:not(.authorize svg){fill:var(--muted)}
  .swagger-ui .arrow{fill:var(--muted)}
  .swagger-ui .authorization__btn svg,.swagger-ui .opblock-summary-control svg.locked,.swagger-ui .authorization__btn.locked svg{fill:var(--accent)!important}
  .swagger-ui .authorization__btn.unlocked svg{fill:var(--ok)!important}
  .swagger-ui .loading-container .loading::after{color:var(--accent)}
  .swagger-ui .dialog-ux .modal-ux{background:#12163a;border:1px solid var(--line);border-radius:8px;color:var(--text);box-shadow:0 30px 70px rgba(0,0,0,.6)}
  .swagger-ui .dialog-ux .modal-ux-header{border-bottom:1px solid var(--line2)}
  .swagger-ui .dialog-ux .modal-ux-header h3,.swagger-ui .dialog-ux .modal-ux-content h4,.swagger-ui .dialog-ux .modal-ux-content p,.swagger-ui .auth-container h4,.swagger-ui .auth-container h6,.swagger-ui .auth-container .wrapper label{color:var(--text);font-family:var(--head)}
  .swagger-ui .auth-container{border-bottom:1px solid var(--line2)}
  .swagger-ui .dialog-ux .backdrop-ux{background:rgba(5,6,20,.72)}
  .swagger-ui .errors-wrapper{background:rgba(255,90,107,.12);border:1px solid var(--bad)}
  .swagger-ui .errors-wrapper .errors h4,.swagger-ui .errors-wrapper hgroup h4{color:var(--bad)}
  .swagger-ui .filter .operation-filter-input{background:var(--panel2);color:var(--text);border:1px solid var(--line)}
  .swagger-ui .servers>label select{min-width:260px}
  ::-webkit-scrollbar{width:10px;height:10px}::-webkit-scrollbar-track{background:#0a0e29}::-webkit-scrollbar-thumb{background:#3a3f78;border-radius:6px}
</style>
"""


def pagina(app, titulo: str, descripcion: str, volver_url: str, volver_texto: str, siglas: str = "G3") -> HTMLResponse:
    """Swagger UI con el tema del sistema + cabecera con enlace de vuelta a la página principal del servicio."""
    base = get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=titulo + " · API",
        swagger_ui_parameters={
            "docExpansion": "list",
            "persistAuthorization": True,
            "displayRequestDuration": True,
            "defaultModelsExpandDepth": -1,
            "syntaxHighlight": {"theme": "monokai"},
            "tryItOutEnabled": True,
        },
    ).body.decode("utf-8")
    cabecera = (
        f'<div class="g3-top"><div class="g3-logo">{siglas}</div><div><b>{titulo}</b><small>Grupo 3 · Documentación de la API</small></div>'
        f'<a href="{volver_url}">{volver_texto}</a></div>'
        f'<div class="g3-hero"><p class="eb">Swagger · OpenAPI</p><h1>{titulo}</h1><p>{descripcion}</p></div>'
    )
    base = base.replace("</head>", CSS + "</head>", 1).replace('<div id="swagger-ui">', cabecera + '<div id="swagger-ui">', 1)
    return HTMLResponse(base)
