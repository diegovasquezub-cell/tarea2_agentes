# Evidencias de respaldo · Grupo 3

Esta carpeta guarda una **ejecución completa, grabada y fechada, del sistema ya desplegado** (Heroku), pensada para el caso en que una
prueba en vivo falle por algo ajeno a la implementación. Todo se grabó el **2026-11-16 y 2026-11-17** contra las direcciones públicas
del README, con navegador real (Edge) y con los mismos scripts del repositorio, así que se puede repetir.

## Si una prueba en vivo falla, mira esto primero

| Lo que ves | Qué significa | Qué hacer |
|---|---|---|
| «El proveedor del modelo falló (…RateLimitError)» o «esa parte no está disponible en este momento» **sin que haya un agente apagado** | Se agotó la cuota gratuita de Gemini (**15 solicitudes por minuto**; cada mensaje usa 2 a 4). El sistema lo informa en vez de inventar una respuesta, que es el comportamiento pedido. | Espera 60 segundos y repite. Para pruebas seguidas, un mensaje cada ~15 s. |
| La primera llamada tarda varios segundos | El dyno de Heroku (plan Eco) dormía tras 30 minutos sin tráfico. | Repite; las siguientes responden en 1 a 5 s. |
| «Clave incorrecta» / 401 | El rechazo es correcto: falta la clave o es incorrecta (resultado 8). | Usa la clave de prueba entregada por la vía privada. |
| La memoria «olvidó» la conversación | El servidor se reinició (Heroku reinicia a diario) y la memoria vive en el proceso: **límite conocido y declarado**. | Empieza una conversación nueva. |

Si algo sigue fallando, los resultados 1 a 11 están demostrados con evidencia grabada, resumida abajo.

## Qué resultado demuestra cada archivo

Las capturas están en [`capturas/`](capturas/) (índice con fecha en [`capturas/_indice.txt`](capturas/_indice.txt)) y fueron tomadas con el
chat web del coordinador y las páginas de cada agente. Ninguna muestra claves: las claves se inyectan en la pestaña sin escribirse en pantalla.

| # | Resultado esperado | Captura(s) | Salida de terminal / datos |
|---|---|---|---|
| 1 | «hola» → el coordinador dice qué agentes tiene y qué sabe cada uno | `01_hola_lista_de_agentes.png` | [`salidas/recorrido_completo_nube.txt`](salidas/recorrido_completo_nube.txt) §1 · logs de Telegram con «responde saludo» |
| 2 | Una pregunta por agente llega al agente correcto y dice cuál respondió | `02a` Diego · `02b` Gerardo · `02c` Jaime · `02d` Henry | `recorrido_completo_nube.txt` §2 · [`../salidas/saltos_coordinador_nube.txt`](../salidas/saltos_coordinador_nube.txt) |
| 3 | Tema que nadie sabe → «no tengo un agente para eso» | `03_tema_que_nadie_sabe_ninguno.png` | `recorrido_completo_nube.txt` §3 |
| 4 | Cifras y unidades llegan iguales | `04_cifras_y_unidades_se_conservan.png` (1.250 kg × 3 turnos = 3.750 kg; 2,5 % → 93,75 kg; 3.656,25 kg buenos) | `recorrido_completo_nube.txt` §4 |
| 5 | Memoria dentro de la conversación y sin mezclar clientes | `05a_memoria_misma_conversacion.png` · `05b_memoria_otra_conversacion_no_hereda.png` | `recorrido_completo_nube.txt` §5 |
| 6 | Ficha pública de cada agente (qué hace, qué no hace, su dirección en la nube) | `06_ficha_publica_{gerardo,diego,jaime,henry}.png` | [`fichas/ficha_*.json`](fichas/) (copia de la ficha pública) · [`fichas/perfil_*.json`](fichas/) |
| 7 | Mensaje directo a cada agente con su clave, sin el coordinador | `07_mensaje_directo_{gerardo,diego,jaime,henry}.png` | [`../salidas/agentes_directo_nube.txt`](../salidas/agentes_directo_nube.txt) |
| 8 | Sin clave o con clave incorrecta, todo rechaza | `08_clave_incorrecta_rechazada_401.png` (coordinador) · `08_agente_sin_clave_valida_rechazado_401.png` (agente) | `recorrido_completo_nube.txt` §8 (`/chat` y `/telegram` sin clave → 401) · `agentes_directo_nube.txt` (401 en los 4) · logs de Telegram (`POST /telegram` → 401) |
| 9 | Un agente apagado: el coordinador avisa y los demás siguen | — | [`../salidas/caso9_agente_apagado.txt`](../salidas/caso9_agente_apagado.txt) (`/salud` de Jaime en 503; Henry sigue respondiendo) · [`../salidas/caso9_agente_recuperado.txt`](../salidas/caso9_agente_recuperado.txt) |
| 10 | Foto o sticker → «no puedo leer ese tipo de mensaje» | — | Prueba automática `tests/test_seguridad.py::test_voz_telegram` (envía una foto y verifica la respuesta). *Falta captura real en Telegram.* |
| 11 | «Ignora tus instrucciones» → no obedece | `11_ignora_tus_instrucciones_rechazado.png` | `recorrido_completo_nube.txt` §11 |
| 12 | Clonar y seguir el README | — | Clon limpio desde GitHub sin `.env` ni `secretos/`: `pip install` + `pytest` → 7 pruebas pasan (ver `../README.md`, fila 12) |

### Canal de Telegram (sin capturas de pantalla del celular)

[`logs/telegram_coordinador.txt`](logs/telegram_coordinador.txt) es un extracto de los logs reales del coordinador en Heroku (sin token, con el id del
chat anonimizado). Muestra mensajes que entraron por Telegram: el saludo (lista de agentes), una consulta derivada a un agente, **dos notas de
voz** (descargadas, transcritas con Gemini y enrutadas: «audio transcrito (… caracteres)») y el rechazo `POST /telegram → 401` cuando
se llama sin el secreto del webhook. Las horas de los logs están en UTC.

### Extras

- **Segundo canal:** el chat web del coordinador (todas las capturas `01` a `11` salen de él).
- **Voz:** [`../salidas/voz_transcripcion.txt`](../salidas/voz_transcripcion.txt) + [`../audio/prueba_voz.wav`](../audio/prueba_voz.wav) y las dos notas de voz reales de los logs de Telegram.

## Cómo repetir la grabación

```powershell
.venv\Scripts\python.exe -m pip install playwright truststore
.venv\Scripts\python.exe scripts\capturas_respaldo.py                       # 20 capturas (usa Edge; unos 7 minutos por la cuota de Gemini)
.venv\Scripts\python.exe scripts\probar_recorrido.py <URL_COORDINADOR>      # recorrido completo en texto
.venv\Scripts\python.exe scripts\probar_agentes_directo.py                  # cada agente por separado
.venv\Scripts\python.exe scripts\saltos_nube.py                             # saltos del coordinador
```

## Honestidad sobre lo que cubre y lo que no

- Las capturas del respaldo son del **chat web**; las de **Telegram** (casos 1 y 10 y la voz) se respaldan con los logs, y se agregan a `../capturas/`
  cuando se tomen desde el celular.
- Las respuestas de los agentes cambian un poco entre ejecuciones (es un modelo de lenguaje); lo que se verifica es el comportamiento: a qué
  agente llega cada pregunta, que las cifras se conserven y que los rechazos ocurran.
- Una ejecución «de respaldo» no reemplaza la prueba en vivo: demuestra que el sistema funcionó en esa fecha con esta versión del código
  (commit del repositorio en la fecha indicada).
