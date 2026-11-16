"""Contenido descriptivo de la ficha y de la página de inicio de cada agente.

Todo sale del perfil que cada integrante definió en el taller A2A (prompts, apuntes y blueprint); aquí solo se
ordena para que la ficha y la página sean claras para alguien que no conoce al agente.
"""

PERFILES = {
    "gerardo": {
        "nombre_corto": "Gerardo Herrera",
        "numero": 1,
        "iniciales": "GH",
        "rol": "Arquitectura de software y sistemas con agentes de IA",
        "resumen": (
            "Consultor Senior de IA en la industria financiera, con 20 años de experiencia en desarrollo, arquitectura, "
            "DevSecOps, ingeniería Cloud e IA generativa. Revisa diseños de software y de sistemas con agentes, compara "
            "alternativas con criterios explícitos y trade-offs, y propone planes incrementales con pruebas verificables."
        ),
        "como_responde": (
            "Directo y didáctico: explica primero el concepto y después el código, usa analogías de construcción, "
            "señala los atajos riesgosos y siempre ofrece alternativas con sus ventajas y desventajas."
        ),
        "ideal_para": [
            "Equipos que quieren ordenar su arquitectura o modernizar su tecnología",
            "Quien necesita comparar alternativas de diseño con criterios claros",
            "Quien busca incorporar seguridad y automatización en la forma de trabajar",
        ],
        "herramienta": "consultar_mis_apuntes: conceptos (arquitectura hexagonal, screaming architecture, agente como grafo A2A), criterios de una buena solución y un caso de referencia.",
        "skills": [
            {
                "nombre": "Liderazgo técnico de equipos multidisciplinarios",
                "descripcion": "Cómo organizar y alinear equipos de desarrollo, arquitectura y operaciones hacia objetivos técnicos y de negocio, bajo una cultura de alto desempeño y agilidad.",
                "ejemplos": ["Mi equipo de desarrollo y el de operaciones no se coordinan, ¿cómo lo ordeno?", "¿Cómo alineo a un equipo técnico con los objetivos del negocio?"],
            },
            {
                "nombre": "Evangelizador de prácticas DevOps y DevSecOps",
                "descripcion": "Implantar DevOps y DevSecOps: seguridad desde el diseño, automatización y entrega continua, con foco en talento, seguridad y escalamiento.",
                "ejemplos": ["¿Por dónde parto para meter seguridad en el proceso de entrega de software?", "¿Cómo explico DevSecOps a un equipo que nunca lo ha usado?"],
            },
            {
                "nombre": "Mejora continua de procesos con foco en SDLC",
                "descripcion": "Revisar el ciclo de vida del desarrollo de software para encontrar cuellos de botella y proponer mejoras medibles.",
                "ejemplos": ["Mi equipo de desarrollo entrega lento y con errores, ¿qué mejoro primero?", "¿Cómo diseño un sistema con varios agentes de IA sin que se vuelva inmanejable?"],
            },
        ],
        "ejemplos_chat": [
            "Presentate y cuéntame cómo me puedes ayudar.",
            "Mi equipo de desarrollo entrega lento y con errores, ¿cómo puedo mejorar la forma en que trabajamos?",
            "¿Qué es la arquitectura hexagonal y cuándo conviene usarla?",
        ],
    },
    "diego": {
        "nombre_corto": "Diego Vasquez",
        "numero": 2,
        "iniciales": "DV",
        "rol": "Ingeniería de datos en Azure",
        "resumen": (
            "Data Engineer Senior en Itaú Chile, especializado en analítica y en proyectos tecnológicos de datos. "
            "Orienta el diseño de pipelines y arquitecturas de datos en Azure (medallón en Databricks y Delta Lake, "
            "orquestación con Azure Data Factory), propone controles de calidad entre capas y pone el costo de cómputo "
            "y el gobierno del dato como criterios de decisión."
        ),
        "como_responde": (
            "Analítico y orientado a datos: antes de opinar pregunta de dónde viene el dato y quién lo va a consumir. "
            "Explica con analogías de una planta de tratamiento de agua (el dato entra crudo y sale potable) y cierra "
            "siempre con un siguiente paso medible."
        ),
        "ideal_para": [
            "Empresas con datos dispersos o desordenados que quieren llevarlos a la nube",
            "Equipos que arman o corrigen pipelines de carga y transformación",
            "Quien necesita bajar el costo o subir la calidad de la gestión de datos",
        ],
        "herramienta": "consultar_mis_apuntes: arquitectura medallón (bronze, silver, gold), rol de ADF y Databricks, datos no estructurados, criterios de una buena solución y un caso de referencia.",
        "skills": [
            {
                "nombre": "Diseñar y orquestar pipelines de datos con Azure Data Factory y Azure Databricks",
                "descripcion": "ADF orquesta y mueve los datos; Databricks los transforma. Diseña flujos re-ejecutables, con ingesta incremental y validaciones.",
                "ejemplos": ["Mi carga nocturna de datos tarda horas y falla a la mitad, ¿cómo la rediseño?", "¿Qué hace Data Factory y qué hace Databricks?"],
            },
            {
                "nombre": "Organizar y gobernar datos estructurados y no estructurados en un data lake por capas",
                "descripcion": "Capas bronze (crudo), silver (limpio y conformado) y gold (listo para negocio), incluyendo datos no estructurados como video, con linaje y mínimo privilegio.",
                "ejemplos": ["Tengo muchos archivos de datos desordenados en mi empresa, ¿por dónde parto para ordenarlos en la nube?", "¿Cómo organizo un data lake en capas?"],
            },
            {
                "nombre": "Mejorar la eficiencia, la calidad y el costo de la gestión de datos",
                "descripcion": "Controla el costo de cómputo (autoescalado y apagado automático), agrega controles de calidad entre capas y define gobierno del dato.",
                "ejemplos": ["Mis procesos de datos cuestan demasiado, ¿qué reviso primero?", "¿Qué controles de calidad pongo entre las capas de datos?"],
            },
        ],
        "ejemplos_chat": [
            "Tengo muchos archivos de datos desordenados en mi empresa, ¿por dónde parto para ordenarlos en la nube?",
            "¿Qué es la arquitectura medallón?",
            "Mi carga de datos nocturna tarda horas y falla a la mitad, ¿cómo la mejoro?",
        ],
    },
    "jaime": {
        "nombre_corto": "Jaime Vidal",
        "numero": 3,
        "iniciales": "JV",
        "rol": "Operaciones en la industria de alimentos",
        "resumen": (
            "Jefe de Operaciones con 9 años en PF Alimentos. Supervisa la fabricación, el control de calidad e inocuidad, "
            "la optimización de recursos, la gestión de inventarios, la recepción y despachos, la relación con proveedores "
            "y el control de indicadores (KPI)."
        ),
        "como_responde": (
            "Práctico y ordenado, con mentalidad de planta: habla de procesos, turnos e indicadores y da instrucciones "
            "en pasos concretos. Prioriza la inocuidad y la seguridad antes que la velocidad, con ejemplos de la línea "
            "de producción y de la bodega."
        ),
        "ideal_para": [
            "Plantas y bodegas con mermas, vencimientos o problemas de rotación",
            "Quien necesita ordenar controles de calidad e inocuidad",
            "Quien quiere medir la operación con indicadores y metas claras",
        ],
        "herramienta": "consultar_mis_apuntes: FEFO frente a FIFO, HACCP, indicadores de operación (OEE y otros), criterios de una buena solución y un caso de referencia.",
        "skills": [
            {
                "nombre": "Supervisar la fabricación de alimentos",
                "descripcion": "Organizar procesos, turnos e indicadores de la línea de producción para producir de forma estable y segura.",
                "ejemplos": ["Produzco 1.250 kg por turno, con 3 turnos y 2,5% de merma, ¿cuántos kg buenos salen por día?", "¿Qué indicadores debería mirar en mi línea de producción?"],
            },
            {
                "nombre": "Control de calidad e inocuidad de los alimentos",
                "descripcion": "Aplicar HACCP (peligros, puntos críticos, límites, monitoreo y acciones correctivas) y trazabilidad por lote, del proveedor al cliente.",
                "ejemplos": ["En mi fábrica de alimentos se nos echan a perder lotes, ¿qué debería controlar?", "¿Qué diferencia hay entre calidad e inocuidad?"],
            },
            {
                "nombre": "Gestión de inventarios",
                "descripcion": "Rotación FEFO (sale primero lo que vence antes), conteo cíclico, cadena de frío y alertas de próximo vencimiento.",
                "ejemplos": ["Tengo mermas por vencimiento en la bodega, ¿cómo ordeno la rotación?", "¿Qué es FEFO y en qué se diferencia de FIFO?"],
            },
        ],
        "ejemplos_chat": [
            "Si produzco 1.250 kg por turno, tengo 3 turnos al día y una merma de 2,5%, ¿cuántos kg buenos salen por día?",
            "En mi fábrica de alimentos se nos echan a perder lotes, ¿qué debería controlar?",
            "¿Qué es FEFO y cuándo uso FEFO en vez de FIFO?",
        ],
    },
    "henry": {
        "nombre_corto": "Henry Ambicho",
        "numero": 4,
        "iniciales": "HA",
        "rol": "Tecnología móvil y desarrollo full-stack",
        "resumen": (
            "Desarrollador de sistemas full-stack con experiencia en planificación, análisis y construcción de soluciones "
            "automatizadas complejas, en todas las etapas: requisitos, diseño, arquitectura, pruebas y soporte. "
            "Orienta el diseño de apps móviles y su backend (nativo, multiplataforma o PWA, offline-first, API o BFF en "
            "Node.js, notificaciones push y WebSockets) y aterriza en un MVP medible."
        ),
        "como_responde": (
            "Pragmático y orientado a construir: piensa primero en el dispositivo y en la conectividad real del usuario. "
            "Explica con flujos de usuario y fragmentos de código cortos, y compara nativo y multiplataforma según costo, "
            "plazo y equipo."
        ),
        "ideal_para": [
            "Quien quiere crear una app móvil y no sabe qué tecnología elegir",
            "Equipos con usuarios de mala conectividad (apps que funcionan sin internet)",
            "Quien necesita definir el backend de una app y acotar un primer MVP",
        ],
        "herramienta": "consultar_mis_apuntes: nativo frente a multiplataforma o PWA, offline-first, backend en Node.js, criterios de una buena solución y un caso de referencia.",
        "skills": [
            {
                "nombre": "Desarrollo de sistemas full-stack",
                "descripcion": "Diseño y arquitectura de apps móviles y su backend (Swift, Kotlin, Node.js, JavaScript, HTML5), con pruebas y soporte.",
                "ejemplos": ["Quiero hacer una app para el celular que funcione sin internet, ¿qué me conviene?", "¿Conviene hacer la app nativa o multiplataforma?"],
            },
            {
                "nombre": "Resolución de problemas",
                "descripcion": "Analizar el problema real (usuarios, conectividad, equipo y plazo) y proponer una solución técnica acotada.",
                "ejemplos": ["Mi app gasta mucha batería y datos, ¿qué reviso primero?", "¿Cómo sincronizo datos que se editaron sin conexión?"],
            },
            {
                "nombre": "Implementación de soluciones automatizadas complejas",
                "descripcion": "Backends (API o BFF en Node.js), notificaciones push y WebSockets para automatizar flujos entre la app y el servidor.",
                "ejemplos": ["¿Cómo mando notificaciones push desde mi backend?", "¿Cuándo uso WebSockets en una app móvil?"],
            },
        ],
        "ejemplos_chat": [
            "Quiero hacer una app para el celular que funcione sin internet, ¿qué me conviene?",
            "¿Qué es offline-first y cómo se sincroniza después?",
            "¿Conviene hacer mi app nativa, multiplataforma o PWA?",
        ],
    },
}
