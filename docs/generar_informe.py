#!/usr/bin/env python3
"""
Genera los diagramas C4 y el Informe Técnico en PDF.

Uso (desde la raíz del proyecto):
    pip install reportlab matplotlib pillow
    python docs/generar_informe.py

Para completar el informe con TUS capturas, copia estas imágenes (PNG/JPG) a docs/capturas/
y vuelve a ejecutar el script. Si una imagen no existe, se muestra un recuadro "pendiente":
    docker-ps.png      -> salida de `docker-compose ps` (3 servicios healthy)
    docker-logs.png    -> salida de `docker-compose logs` (gateway y microservicio)
    swagger.png        -> Swagger UI (http://localhost:8080/docs) con una petición exitosa
    postman.png        -> Postman (Runner o una petición) con respuestas exitosas
"""
import os
import re
import textwrap

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle
from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    Image,
    KeepTogether,
    PageBreak,
    Paragraph,
    Preformatted,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

# ======================== DATOS DE LA PORTADA (edítalos) ========================
ESTUDIANTE = "[Nombre completo del estudiante]"
MATERIA = "[Nombre de la materia]"
DOCENTE = "[Nombre del docente]"
UNIVERSIDAD = "Universidad Católica Boliviana"
REPOSITORIO = "[URL del repositorio público en GitHub/GitLab]"
FECHA = "Octubre de 2026"
# ================================================================================

BASE = os.path.dirname(os.path.abspath(__file__))
DIAG = os.path.join(BASE, "diagramas")
EVID = os.path.join(BASE, "evidencia")
CAPT = os.path.join(BASE, "capturas")
OUT_PDF = os.path.join(BASE, "Informe_Tecnico_Herbario.pdf")
os.makedirs(DIAG, exist_ok=True)

# Paleta C4
C_PERSON, C_SYSTEM, C_CONTAINER, C_DB, C_BOUND = "#08427B", "#1168BD", "#438DD5", "#2E6F9E", "#555555"


# ------------------------------------------------------------------ diagramas C4
def _box(ax, x, y, w, h, title, kind, desc, color, wrap=24, fs=6.6):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.3,rounding_size=1.2",
                                fc=color, ec="#0b2d4f", lw=1))
    lines = [(title, "bold", fs + 1.2), (kind, "normal", fs - 0.6)]
    body = textwrap.wrap(desc, wrap)
    total = 2 + len(body)
    step = h / (total + 1)
    cy = y + h - step * 0.9
    for text, weight, size in lines:
        ax.text(x + w / 2, cy, text, ha="center", va="center", color="white",
                fontsize=size, fontweight=weight, style="italic" if weight == "normal" else "normal")
        cy -= step
    for ln in body:
        ax.text(x + w / 2, cy, ln, ha="center", va="center", color="white", fontsize=fs - 0.4)
        cy -= step * 0.9


def _arrow(ax, p1, p2, label, lx=None, ly=None):
    ax.annotate("", xy=p2, xytext=p1,
                arrowprops=dict(arrowstyle="-|>", color="#333333", lw=1.2, shrinkA=0, shrinkB=0))
    mx = lx if lx is not None else (p1[0] + p2[0]) / 2
    my = ly if ly is not None else (p1[1] + p2[1]) / 2
    ax.text(mx, my, label, ha="center", va="center", fontsize=6, color="#222222",
            bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="#bbbbbb", lw=0.5))


def diagrama_nivel1():
    fig, ax = plt.subplots(figsize=(7.4, 3.5))
    ax.set_xlim(0, 100); ax.set_ylim(0, 50); ax.axis("off")
    _box(ax, 2, 29, 24, 17, "Investigador botánico", "[Persona]",
         "Registra plantas, familias y avistamientos de campo", C_PERSON)
    _box(ax, 2, 4, 24, 17, "Cliente de la API", "[Persona / aplicación]",
         "Consulta el catálogo desde Postman, Swagger o una app", C_PERSON)
    _box(ax, 58, 14, 38, 22, "Herbario de Flora Boliviana", "[Sistema de software]",
         "API REST que centraliza el catálogo de flora: plantas, familias botánicas y "
         "avistamientos georreferenciados", C_SYSTEM, wrap=34, fs=7)
    _arrow(ax, (26.5, 38), (57.5, 28), "Registra y consulta\n[HTTP/JSON + JWT]", 42, 36)
    _arrow(ax, (26.5, 12), (57.5, 22), "Consulta\n[HTTP/JSON + JWT]", 42, 13)
    ax.text(50, 1, "C4 - Nivel 1: Diagrama de Contexto del Sistema", ha="center", fontsize=7.5,
            fontweight="bold", color="#222222")
    fig.savefig(os.path.join(DIAG, "c4-nivel1-contexto.png"), dpi=200, bbox_inches="tight")
    plt.close(fig)


def diagrama_nivel2():
    fig, ax = plt.subplots(figsize=(7.4, 3.7))
    ax.set_xlim(0, 110); ax.set_ylim(0, 56); ax.axis("off")
    _box(ax, 1, 19, 13, 18, "Cliente HTTP", "[Persona]", "Postman, cURL, Swagger o app", C_PERSON, wrap=13)
    ax.add_patch(Rectangle((21, 4), 88, 48, fill=False, ec=C_BOUND, lw=1.1, ls=(0, (5, 3))))
    ax.text(23, 49.2, "Herbario de Flora Boliviana   |   Red Docker bridge: herbario-net",
            fontsize=7, fontweight="bold", color=C_BOUND, va="center")
    _box(ax, 24, 14, 22, 28, "API Gateway", "[Node.js + Express]",
         "Único punto de entrada. Proxy inverso, CORS, logging con x-request-id, rate limiting y JWT. "
         "Puerto 8080", C_CONTAINER, wrap=21)
    _box(ax, 57, 14, 22, 28, "Microservicio", "[NestJS + TypeScript]",
         "CRUD de familias, plantas y avistamientos. DTO, Repository, DI, Swagger. Puerto 3000 (interno)",
         C_CONTAINER, wrap=21)
    _box(ax, 88, 14, 19, 28, "Base de datos", "[PostgreSQL 16]",
         "Tablas familias, plantas y avistamientos. Volumen pgdata. Puerto 5432 (interno)", C_DB, wrap=18)
    _arrow(ax, (14.4, 28), (23.6, 28), "HTTP/JSON\n:8080", 19, 35)
    _arrow(ax, (46.4, 28), (56.6, 28), "HTTP/JSON\n:3000", 51.5, 34)
    _arrow(ax, (79.4, 28), (87.6, 28), "SQL/TCP\n:5432", 83.5, 34)
    ax.text(55, 1, "C4 - Nivel 2: Diagrama de Contenedores", ha="center", fontsize=7.5,
            fontweight="bold", color="#222222")
    fig.savefig(os.path.join(DIAG, "c4-nivel2-contenedores.png"), dpi=200, bbox_inches="tight")
    plt.close(fig)


# ------------------------------------------------------------------ utilidades PDF
ss = getSampleStyleSheet()
BODY = ParagraphStyle("body", parent=ss["Normal"], fontName="Helvetica", fontSize=9.4, leading=12.6,
                      alignment=TA_JUSTIFY, spaceAfter=5)
SMALL = ParagraphStyle("small", parent=BODY, fontSize=8, leading=10, alignment=0, spaceAfter=2)
H1 = ParagraphStyle("h1", parent=ss["Heading1"], fontName="Helvetica-Bold", fontSize=15, leading=18,
                    textColor=colors.HexColor("#0b2d4f"), spaceBefore=4, spaceAfter=7)
H2 = ParagraphStyle("h2", parent=ss["Heading2"], fontName="Helvetica-Bold", fontSize=11, leading=14,
                    textColor=colors.HexColor("#1168BD"), spaceBefore=7, spaceAfter=4)
CELL = ParagraphStyle("cell", parent=BODY, fontSize=8, leading=10, alignment=0, spaceAfter=0)
CELLB = ParagraphStyle("cellb", parent=CELL, fontName="Helvetica-Bold", textColor=colors.white)
CODE = ParagraphStyle("code", fontName="Courier", fontSize=6.6, leading=8.1, textColor=colors.HexColor("#d4d4d4"))
CAPTION = ParagraphStyle("cap", parent=SMALL, fontName="Helvetica-Oblique", textColor=colors.HexColor("#555555"))
W = letter[0] - 4 * cm


def P(t, st=BODY):
    return Paragraph(t, st)


def tabla(rows, widths, header=True, zebra=True):
    data = []
    for i, r in enumerate(rows):
        data.append([Paragraph(str(c), CELLB if (header and i == 0) else CELL) for c in r])
    t = Table(data, colWidths=widths, repeatRows=1 if header else 0)
    st = [("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#b8c4d0")),
          ("VALIGN", (0, 0), (-1, -1), "TOP"),
          ("LEFTPADDING", (0, 0), (-1, -1), 4), ("RIGHTPADDING", (0, 0), (-1, -1), 4),
          ("TOPPADDING", (0, 0), (-1, -1), 2.5), ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5)]
    if header:
        st.append(("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1168BD")))
    if zebra:
        for i in range(1, len(rows)):
            if i % 2 == 0:
                st.append(("BACKGROUND", (0, i), (-1, i), colors.HexColor("#eef3f8")))
    t.setStyle(TableStyle(st))
    return t


def terminal(text, width_chars=112):
    lines = []
    for ln in text.rstrip().splitlines():
        lines.extend(textwrap.wrap(ln, width_chars, subsequent_indent="    ",
                                   break_long_words=True, replace_whitespace=False) or [""])
    pre = Preformatted("\n".join(lines), CODE)
    t = Table([[pre]], colWidths=[W])
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#1e1e1e")),
                           ("LEFTPADDING", (0, 0), (-1, -1), 6), ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                           ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5)]))
    return t


def imagen(path, max_w=W, max_h=9 * cm):
    from PIL import Image as PILImage
    with PILImage.open(path) as im:
        w, h = im.size
    ratio = min(max_w / w, max_h / h)
    return Image(path, width=w * ratio, height=h * ratio)


def captura(nombre, titulo):
    """Imagen real si existe en docs/capturas, si no un recuadro de 'pendiente'."""
    for ext in (".png", ".jpg", ".jpeg"):
        p = os.path.join(CAPT, nombre + ext)
        if os.path.exists(p):
            return KeepTogether([P(f"<b>{titulo}</b>", SMALL), imagen(p, max_h=6.0 * cm), Spacer(1, 6)])
    box = Table([[P(f"<b>Captura pendiente:</b> {titulo}<br/>"
                    f"Guarda la imagen como <font face='Courier'>docs/capturas/{nombre}.png</font> "
                    f"y vuelve a ejecutar <font face='Courier'>python docs/generar_informe.py</font>.", SMALL)]],
                colWidths=[W])
    box.setStyle(TableStyle([("BOX", (0, 0), (-1, -1), 0.8, colors.HexColor("#c0392b"), None, (3, 3)),
                             ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#fdf2f0")),
                             ("TOPPADDING", (0, 0), (-1, -1), 8), ("BOTTOMPADDING", (0, 0), (-1, -1), 8)]))
    return KeepTogether([box, Spacer(1, 6)])


def leer(nombre):
    with open(os.path.join(EVID, nombre), encoding="utf-8") as f:
        return f.read()


# ------------------------------------------------------------------ evidencia (parseo)
def parsear_smoke(txt):
    bloques = []
    for b in re.split(r"\n### ", "\n" + txt):
        b = b.strip("\n")
        if not b or b.startswith("Pruebas terminadas"):
            continue
        lines = b.splitlines()
        titulo = lines[0]
        cmd = next((l for l in lines if l.startswith("$ curl")), "")
        http = next((l for l in lines if l.startswith("HTTP ")), "")
        body = [l for l in lines[2:] if not l.startswith("HTTP ") and not l.startswith("Pruebas")]
        bloques.append(dict(titulo=titulo, cmd=cmd, http=http.replace("HTTP ", ""), body="\n".join(body)))
    return bloques


ESPERADO = {1: 200, 2: 401, 3: 401, 4: 200, 5: 200, 6: 201, 7: 409, 8: 201, 9: 400, 10: 200,
            11: 200, 12: 200, 13: 200, 14: 201, 15: 200, 16: 409, 17: 204, 18: 204, 19: 204, 20: 404}


def construir():
    smoke = parsear_smoke(leer("smoke-test.txt"))
    story = []

    # ------------------------------------------------------------ portada
    story += [Spacer(1, 3.2 * cm),
              P(f"<font size=11 color='#555555'>{UNIVERSIDAD}</font>", ParagraphStyle("c0", parent=BODY, alignment=1)),
              Spacer(1, 1.2 * cm),
              P("INFORME TÉCNICO", ParagraphStyle("c1", parent=H1, fontSize=26, leading=30, alignment=1)),
              P("Herbario de Flora Boliviana", ParagraphStyle("c2", parent=H1, fontSize=20, leading=24,
                                                              alignment=1, textColor=colors.HexColor("#1168BD"))),
              Spacer(1, 4),
              P("Arquitectura orientada a servicios: API Gateway (proxy inverso) + Microservicio NestJS "
                "+ PostgreSQL, orquestados con Docker Compose",
                ParagraphStyle("c3", parent=BODY, alignment=1, fontSize=11, leading=15)),
              Spacer(1, 2 * cm)]
    portada = [["Estudiante", ESTUDIANTE], ["Materia", MATERIA], ["Docente", DOCENTE],
               ["Tecnología asignada", "NestJS (TypeScript)"], ["Base de datos", "PostgreSQL 16"],
               ["Repositorio", REPOSITORIO], ["Fecha", FECHA]]
    t = Table([[Paragraph(f"<b>{a}</b>", CELL), Paragraph(b, CELL)] for a, b in portada],
              colWidths=[4.2 * cm, W - 4.2 * cm - 2 * cm], hAlign="CENTER")
    t.setStyle(TableStyle([("LINEBELOW", (0, 0), (-1, -1), 0.4, colors.HexColor("#b8c4d0")),
                           ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6)]))
    story += [t, PageBreak()]

    # ------------------------------------------------------------ 1. dominio
    story += [P("1. Descripción del dominio", H1),
              P("1.1 Problema de negocio", H2),
              P("Bolivia es un país megadiverso, con ecorregiones muy distintas entre sí: Altiplano, valles, Yungas, "
                "Chaco, Amazonía y Llanos. Sin embargo, la información sobre su flora suele estar dispersa en planillas, "
                "cuadernos de campo e informes aislados. Esto dificulta saber <i>qué especies existen</i>, "
                "<i>a qué familia botánica pertenecen</i>, <i>en qué rango de altitud viven</i>, <i>cuál es su estado de "
                "conservación</i> y, sobre todo, <i>dónde y cuándo fue observada</i> cada una, de modo que no hay "
                "trazabilidad ni una fuente única y consultable."),
              P("1.2 Solución propuesta", H2),
              P("Se construye un <b>herbario digital</b> expuesto como API REST. El sistema centraliza el catálogo de "
                "plantas con su familia, ecorregión, rango altitudinal y estado de conservación, y permite registrar "
                "<b>avistamientos</b> georreferenciados (localidad, departamento, coordenadas, fecha y observador). "
                "Cualquier cliente (una app web o móvil, Postman, un script de investigación) consume el servicio a "
                "través de un único punto de entrada: el API Gateway, que autentica y controla el tráfico antes de "
                "llegar al microservicio."),
              P("1.3 Actores", H2),
              tabla([["Actor", "Rol en el sistema"],
                     ["Investigador botánico", "Registra y actualiza plantas, familias y avistamientos de campo."],
                     ["Cliente de la API", "Aplicación o persona que consulta el catálogo (búsquedas y filtros)."],
                     ["Administrador", "Posee las credenciales del gateway y gestiona la configuración del despliegue."]],
                    [4.6 * cm, W - 4.6 * cm]),
              P("1.4 Entidades del dominio", H2),
              tabla([["Entidad", "Atributos principales", "Relaciones"],
                     ["Familia", "id, nombre (único), descripción", "Una familia agrupa muchas plantas (1:N)."],
                     ["Planta", "id, nombre científico (único), nombre común, descripción, ecorregión, "
                                "altitud mín./máx., estado de conservación", "Pertenece a una familia (N:1). "
                                "Tiene muchos avistamientos (1:N)."],
                     ["Avistamiento", "id, localidad, departamento, latitud, longitud, fecha, observador, notas",
                      "Pertenece a una planta (N:1)."]],
                    [2.6 * cm, 8.4 * cm, W - 11 * cm]),
              Spacer(1, 5),
              P("1.5 Reglas de negocio", H2),
              P("&bull; El nombre científico de la planta y el nombre de la familia son únicos (conflicto 409 si se repiten).<br/>"
                "&bull; Toda planta debe pertenecer a una familia existente.<br/>"
                "&bull; No se puede eliminar una familia que todavía tiene plantas asociadas (restricción <i>RESTRICT</i>, 409).<br/>"
                "&bull; Al eliminar una planta se eliminan sus avistamientos (<i>CASCADE</i>).<br/>"
                "&bull; La altitud mínima no puede ser mayor que la máxima (400).<br/>"
                "&bull; El estado de conservación pertenece a un conjunto cerrado de categorías, inspirado en la Lista Roja "
                "de la UICN: preocupación menor, casi amenazada, vulnerable, en peligro y en peligro crítico.<br/>"
                "&bull; El departamento del avistamiento debe ser uno de los nueve departamentos de Bolivia y la fecha "
                "usa el formato AAAA-MM-DD."),
              PageBreak()]

    # ------------------------------------------------------------ 2. arquitectura
    story += [P("2. Arquitectura del sistema (Modelo C4)", H1),
              P("2.1 Nivel 1 — Diagrama de Contexto", H2),
              imagen(os.path.join(DIAG, "c4-nivel1-contexto.png"), max_h=7.6 * cm),
              P("El sistema <b>Herbario de Flora Boliviana</b> es consumido por dos tipos de actores humanos o "
                "aplicaciones, siempre por HTTP/JSON y con un token JWT. No depende de sistemas externos: toda la "
                "información vive en su propia base de datos.", BODY),
              P("2.2 Nivel 2 — Diagrama de Contenedores", H2),
              imagen(os.path.join(DIAG, "c4-nivel2-contenedores.png"), max_h=8.2 * cm),
              Spacer(1, 4),
              tabla([["Contenedor", "Tecnología", "Responsabilidad", "Exposición"],
                     ["API Gateway", "Node.js 20, Express, http-proxy-middleware",
                      "Punto único de entrada; enruta /api y /docs; CORS, logging con x-request-id, rate limiting, JWT.",
                      "Puerto 8080 publicado al host"],
                     ["Microservicio", "NestJS 10, TypeScript, TypeORM, class-validator, Swagger",
                      "Lógica de negocio y CRUD de familias, plantas y avistamientos (DTO, Repository, DI).",
                      "Puerto 3000, solo red interna"],
                     ["Base de datos", "PostgreSQL 16 (imagen alpine)",
                      "Persistencia relacional con volumen <font face='Courier'>pgdata</font>.",
                      "Puerto 5432, solo red interna"]],
                    [2.5 * cm, 4.2 * cm, W - 2.5 * cm - 4.2 * cm - 3.4 * cm, 3.4 * cm]),
              PageBreak(),
              P("2.3 Decisiones de diseño", H2),
              P("&bull; <b>Gateway como única puerta:</b> solo el puerto 8080 se publica. El microservicio y PostgreSQL no son "
                "accesibles desde fuera de la red <font face='Courier'>herbario-net</font> (driver <i>bridge</i>).<br/>"
                "&bull; <b>Características transversales en el gateway:</b> CORS configurable, logging JSON con "
                "<font face='Courier'>x-request-id</font> propagado al microservicio (trazabilidad de extremo a extremo), "
                "rate limiting (100 peticiones/min por IP y 10 intentos/min en el login) y validación de JWT en todas las "
                "rutas <font face='Courier'>/api</font>.<br/>"
                "&bull; <b>Patrones en el microservicio:</b> <i>Repository</i> (servicios que inyectan "
                "<font face='Courier'>Repository&lt;Entidad&gt;</font> de TypeORM), <i>DTO</i> con validación "
                "(whitelist y forbidNonWhitelisted) e <i>inyección de dependencias</i> de NestJS.<br/>"
                "&bull; <b>Contenerización:</b> Dockerfile multi-stage para el microservicio (compila y luego copia solo lo "
                "necesario, ejecuta como usuario no root) y Dockerfile ligero para el gateway.<br/>"
                "&bull; <b>Orquestación:</b> <font face='Courier'>docker-compose.yml</font> con <font face='Courier'>depends_on</font> "
                "en condición <font face='Courier'>service_healthy</font> y healthchecks en los tres servicios: la base de datos arranca "
                "primero, luego el microservicio y al final el gateway.<br/>"
                "&bull; <b>Manejo de errores:</b> las violaciones de unicidad y de llaves foráneas de PostgreSQL se traducen a "
                "respuestas 409; si el microservicio cae, el gateway responde 502 en lugar de quedarse colgado."),
              P("2.4 Modelo de datos", H2),
              terminal("familias (id PK, nombre UNIQUE, descripcion)\n"
                       "   |  1\n"
                       "   |  N   (ON DELETE RESTRICT)\n"
                       "plantas (id PK, nombre_cientifico UNIQUE, nombre_comun, descripcion, ecorregion,\n"
                       "         altitud_min, altitud_max, estado_conservacion, familia_id FK)\n"
                       "   |  1\n"
                       "   |  N   (ON DELETE CASCADE)\n"
                       "avistamientos (id PK, planta_id FK, localidad, departamento, latitud, longitud,\n"
                       "               fecha, observador, notas)"),
              PageBreak()]

    # ------------------------------------------------------------ 3. endpoints
    story += [P("3. Documentación de endpoints", H1),
              P("Todas las rutas se consumen a través del gateway: <font face='Courier'>http://localhost:8080</font>. "
                "Las rutas <font face='Courier'>/api/*</font> exigen el encabezado "
                "<font face='Courier'>Authorization: Bearer &lt;token&gt;</font>. La documentación interactiva "
                "(Swagger UI) está en <font face='Courier'>/docs</font>.", BODY),
              tabla([["Método", "URL", "Descripción", "Respuestas"],
                     ["POST", "/auth/login", "Autentica y devuelve el JWT", "200, 401, 429"],
                     ["GET", "/health", "Estado del gateway", "200"],
                     ["GET", "/api/familias", "Lista las familias", "200"],
                     ["GET", "/api/familias/:id", "Obtiene una familia", "200, 404"],
                     ["POST", "/api/familias", "Crea una familia", "201, 400, 409"],
                     ["PATCH", "/api/familias/:id", "Actualiza una familia", "200, 400, 404, 409"],
                     ["DELETE", "/api/familias/:id", "Elimina una familia (sin plantas)", "204, 404, 409"],
                     ["GET", "/api/plantas?familiaId&ecorregion&estado&q", "Lista plantas con filtros y búsqueda", "200, 400"],
                     ["GET", "/api/plantas/:id", "Obtiene una planta (incluye su familia)", "200, 404"],
                     ["GET", "/api/plantas/:id/avistamientos", "Avistamientos de una planta", "200, 404"],
                     ["POST", "/api/plantas", "Crea una planta", "201, 400, 409"],
                     ["PATCH", "/api/plantas/:id", "Actualiza una planta", "200, 400, 404, 409"],
                     ["DELETE", "/api/plantas/:id", "Elimina una planta y sus avistamientos", "204, 404"],
                     ["GET", "/api/avistamientos?plantaId&departamento", "Lista avistamientos con filtros", "200, 400"],
                     ["GET", "/api/avistamientos/:id", "Obtiene un avistamiento", "200, 404"],
                     ["POST", "/api/avistamientos", "Registra un avistamiento", "201, 400, 409"],
                     ["PATCH", "/api/avistamientos/:id", "Actualiza un avistamiento", "200, 400, 404, 409"],
                     ["DELETE", "/api/avistamientos/:id", "Elimina un avistamiento", "204, 404"]],
                    [1.7 * cm, 6.4 * cm, W - 1.7 * cm - 6.4 * cm - 3.2 * cm, 3.2 * cm]),
              Spacer(1, 5),
              P("Cuando falta el token o es inválido el gateway responde 401; si se excede el límite de peticiones, 429; y si "
                "el microservicio no responde, 502.", SMALL),
              P("3.1 Estructuras JSON", H2),
              P("<b>Login</b> — <font face='Courier'>POST /auth/login</font>", SMALL),
              terminal('Solicitud:  {"username": "admin", "password": "herbario123"}\n'
                       'Respuesta 200: {"access_token": "<jwt>", "token_type": "Bearer", "expires_in": "1h"}'),
              Spacer(1, 4),
              P("<b>Crear planta</b> — <font face='Courier'>POST /api/plantas</font>", SMALL),
              terminal('Solicitud:\n'
                       '{ "nombreCientifico": "Echinopsis tarijensis", "nombreComun": "Cardón",\n'
                       '  "ecorregion": "Valles secos", "altitudMin": 1800, "altitudMax": 3200,\n'
                       '  "estadoConservacion": "preocupacion_menor", "familiaId": 6 }\n'
                       'Respuesta 201:\n'
                       '{ "id": 6, "nombreCientifico": "Echinopsis tarijensis", "nombreComun": "Cardón",\n'
                       '  "ecorregion": "Valles secos", "altitudMin": 1800, "altitudMax": 3200,\n'
                       '  "estadoConservacion": "preocupacion_menor", "familiaId": 6,\n'
                       '  "familia": { "id": 6, "nombre": "Cactaceae", "descripcion": "Familia de los cactus" } }'),
              Spacer(1, 4),
              P("<b>Registrar avistamiento</b> — <font face='Courier'>POST /api/avistamientos</font>", SMALL),
              terminal('Solicitud:\n'
                       '{ "plantaId": 6, "localidad": "Tarija - Tolomosa", "departamento": "Tarija",\n'
                       '  "latitud": -21.5, "longitud": -64.8, "fecha": "2026-10-10",\n'
                       '  "observador": "Estudiante UCB", "notas": "Ejemplar adulto" }\n'
                       'Respuesta 201: el avistamiento creado, con "id" y la "planta" asociada.'),
              Spacer(1, 4),
              P("<b>Errores</b>", SMALL),
              terminal('400: {"message": ["nombreCientifico should not be empty", ...], "error": "Bad Request", "statusCode": 400}\n'
                       '401: {"error": "Unauthorized", "message": "Falta el token Bearer."}\n'
                       '409: {"message": "Ya existe un registro con esos datos únicos.", "error": "Conflict", "statusCode": 409}\n'
                       '502: {"error": "Bad Gateway", "message": "El microservicio no responde."}'),
              PageBreak()]

    # ------------------------------------------------------------ 4. pruebas
    story += [P("4. Evidencia de pruebas", H1),
              P("Las pruebas se ejecutan con el script <font face='Courier'>scripts/smoke-test.sh</font> (20 casos de punta a "
                "punta contra el gateway) y con la colección de Postman incluida en el repositorio. Las secciones 4.1 a 4.4 "
                "muestran la salida real de esa ejecución sobre el gateway, el microservicio y PostgreSQL 16 "
                "(procesos locales durante el desarrollo); la sección 4.5 reúne las capturas de la ejecución con Docker "
                "Compose.", BODY),
              P("4.1 Resultados de la batería de pruebas", H2)]
    filas = [["#", "Caso de prueba", "Petición", "Esperado", "Obtenido"]]
    for b in smoke:
        m = re.match(r"(\d+)\.\s*(.*)", b["titulo"])
        if not m or int(m.group(1)) not in ESPERADO:
            continue
        n = int(m.group(1)); caso = re.sub(r"\s*\(.*?\)\s*$", "", m.group(2))
        pet = re.sub(r"^\$ curl -X (\w+) https?://[^/]+(\S*).*", r"\1 \2", b["cmd"])
        esp, obt = ESPERADO[n], int(b["http"])
        filas.append([n, caso, pet.replace("&", "&amp;"), esp, f"{obt} {'OK' if esp == obt else 'ERROR'}"])
    story += [tabla(filas, [0.8 * cm, 6.0 * cm, W - 0.8 * cm - 6.0 * cm - 4.4 * cm, 1.9 * cm, 2.5 * cm]),
              P("4.2 Ejemplos de salida", H2)]

    def bloque(n):
        b = next(x for x in smoke if x["titulo"].startswith(f"{n}."))
        cmd = b["cmd"].replace("$ curl", "$ curl -s")
        body = b["body"]
        if n == 4:
            body = re.sub(r'("access_token":")[^"]{25,}(")', r"\1eyJhbGciOiJIUzI1NiIs...(recortado)\2", body)
        return f"{cmd}\n{body}\nHTTP {b['http']}"

    story += [terminal("\n\n".join(bloque(n) for n in (2, 4, 8, 7, 16)), 118),
              P("4.3 Trazabilidad: el mismo x-request-id en gateway y microservicio", H2)]

    gw = [l for l in leer("gateway.log").splitlines() if l.startswith('{"time"')]
    ms = leer("microservicio.log").splitlines()
    pares = []
    for metodo, url in (("POST", "/api/plantas"), ("DELETE", "/api/familias/")):
        g = next((l for l in gw if f'"method":"{metodo}"' in l and url in l), None)
        if g:
            rid = re.search(r'"requestId":"([^"]+)"', g).group(1)
            mline = next((l for l in ms if rid in l), "")
            pares.append(("[gateway]       " + g, "[microservicio] " + re.sub(r"^\[Nest\][^\[]*\s*LOG\s*", "", mline)))
    story += [terminal("\n".join(f"{a}\n{b}\n" for a, b in pares).rstrip(), 118),
              P("4.4 Rate limiting y error 502", H2),
              terminal(leer("rate-limit.txt").replace('\\"', '"'), 118),
              Spacer(1, 4),
              terminal(leer("bad-gateway.txt"), 118),
              P("4.5 Capturas en Docker, Swagger y Postman", H2),
              captura("docker-ps", "docker-compose ps — los tres servicios en estado healthy"),
              captura("docker-logs", "docker-compose logs — arranque y peticiones en gateway y microservicio"),
              captura("swagger", "Swagger UI — petición exitosa a través del gateway"),
              captura("postman", "Postman — ejecución exitosa de la colección"),
              P("Conclusión", H2),
              P("La arquitectura cumple los objetivos: un gateway que centraliza el acceso con cuatro mecanismos transversales "
                "(CORS, logging con trazabilidad, rate limiting y JWT), un microservicio NestJS con CRUD completo y patrones "
                "Repository/DTO/DI sobre PostgreSQL, y una orquestación reproducible con un solo comando "
                "(<font face='Courier'>docker-compose up</font>).")]
    return story


def pie(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(colors.HexColor("#777777"))
    if doc.page > 1:
        canvas.drawString(2 * cm, 1.2 * cm, "Herbario de Flora Boliviana — Informe Técnico")
        canvas.drawRightString(letter[0] - 2 * cm, 1.2 * cm, f"Página {doc.page}")
    canvas.restoreState()


if __name__ == "__main__":
    diagrama_nivel1()
    diagrama_nivel2()
    doc = SimpleDocTemplate(OUT_PDF, pagesize=letter, leftMargin=2 * cm, rightMargin=2 * cm,
                            topMargin=1.8 * cm, bottomMargin=1.9 * cm,
                            title="Informe Técnico - Herbario de Flora Boliviana", author=ESTUDIANTE)
    doc.build(construir(), onFirstPage=pie, onLaterPages=pie)
    print("PDF generado:", OUT_PDF)
