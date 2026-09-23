import os
import csv
from io import StringIO
from functools import wraps
from hmac import compare_digest
from secrets import token_urlsafe
from datetime import datetime, timedelta
from bson import ObjectId
from dotenv import load_dotenv
from flask import Flask, Response, abort, flash, redirect, render_template, request, session, url_for
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError

load_dotenv()
app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "solo-desarrollo-cambia-esta-clave")
app.config["ADMIN_ACCESS_KEY"] = os.environ.get("ADMIN_ACCESS_KEY", "")
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_SECURE"] = os.environ.get("COOKIE_SECURE", "false").lower() == "true"
app.permanent_session_lifetime = timedelta(hours=8)

MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "reservas_zen"

client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=1200)
db = client[DB_NAME]
servicios_col = db["servicios"]
reservas_col = db["reservas"]

HORARIOS_LABORABLES = [
    "10:00", "10:30", "11:00", "11:30",
    "15:30", "16:00", "16:30", "17:00", "17:30",
    "18:00", "18:30", "19:00", "19:30",
]
HORARIOS_SABADO = ["10:00", "10:30", "11:00", "11:30", "12:00", "12:30"]
DIAS_SEMANA = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]

GOOGLE_REVIEWS_URL = "https://share.google/BkCpwzwjJURx1NCxx"

RESENAS_GOOGLE = [
    {
        "nombre": "Esther R.",
        "iniciales": "ER",
        "fecha": "Hace 2 meses",
        "valoracion": 5,
        "texto": "Una experiencia maravillosa.",
    },
    {
        "nombre": "Veronica Ojeda",
        "iniciales": "VO",
        "fecha": "Hace 4 meses",
        "valoracion": 5,
        "texto": "El masaje fue súper relajador y el ambiente divino.",
    },
    {
        "nombre": "Sara Camargo Cortés",
        "iniciales": "SC",
        "fecha": "Hace un mes",
        "valoracion": 5,
        "texto": "100% recomendable, trato cercano y personalizado.",
    },
    {
        "nombre": "Montse Peinado",
        "iniciales": "MP",
        "fecha": "Hace 6 meses",
        "valoracion": 5,
        "texto": "Jimena tiene muy buenas manos.",
    },
]

SERVICIOS_INICIALES = [
    {"nombre": "Masaje craneal", "categoria": "Corporales", "duracion": 20, "precio": 20, "descripcion": "Alivia el estrés, la tensión cervical y favorece un descanso profundo."},
    {"nombre": "Masaje descontracturante", "categoria": "Corporales", "duracion": 40, "precio": 35, "descripcion": "Libera la tensión acumulada en espalda, cuello y hombros."},
    {"nombre": "Masaje relajante", "categoria": "Corporales", "duracion": 60, "precio": 50, "descripcion": "Relajación profunda para cuerpo y mente, ideal para desconectar del estrés."},
    {"nombre": "Masaje reductor", "categoria": "Corporales", "duracion": 60, "precio": 60, "descripcion": "Mejora la circulación, ayuda a reducir la celulitis y moldea la silueta."},
    {"nombre": "Piedras calientes", "categoria": "Corporales", "duracion": 60, "precio": 60, "descripcion": "Combina masaje manual con el calor terapéutico de piedras volcánicas."},
    {"nombre": "Drenaje linfático manual", "categoria": "Corporales", "duracion": 50, "precio": 50, "descripcion": "Tratamiento suave para aliviar la retención de líquidos y las piernas cansadas."},
    {"nombre": "Manicura spa", "categoria": "Corporales", "duracion": 40, "precio": 25, "descripcion": "Cuidado completo de manos y uñas con exfoliación e hidratación."},
    {"nombre": "Pedicura spa", "categoria": "Corporales", "duracion": 45, "precio": 30, "descripcion": "Cuidado completo de pies con exfoliación, hidratación y esmaltado."},
    {"nombre": "Ritual zen", "categoria": "Corporales", "duracion": 90, "precio": 70, "descripcion": "Experiencia completa con masaje, aromaterapia y descanso guiado."},
    {"nombre": "Limpieza facial", "categoria": "Faciales", "duracion": 50, "precio": 38, "descripcion": "Limpia, renueva e hidrata la piel para devolverle su luminosidad natural."},
    {"nombre": "Limpieza facial profunda", "categoria": "Faciales", "duracion": 60, "precio": 50, "descripcion": "Higiene intensiva con exfoliación y extracción para purificar la piel."},
    {"nombre": "Hidratación facial intensa", "categoria": "Faciales", "duracion": 45, "precio": 42, "descripcion": "Aporta confort y elasticidad a las pieles secas o deshidratadas."},
    {"nombre": "Ritual facial antiedad", "categoria": "Faciales", "duracion": 70, "precio": 58, "descripcion": "Tratamiento nutritivo que suaviza líneas de expresión y revitaliza el rostro."},
    {"nombre": "Masaje facial kobido", "categoria": "Faciales", "duracion": 50, "precio": 48, "descripcion": "Masaje japonés que tonifica el rostro y estimula la circulación."},
    {"nombre": "Higiene facial", "categoria": "Faciales", "duracion": 30, "precio": 38, "descripcion": "Limpieza profunda de la piel para un rostro luminoso y sano."},
    {"nombre": "Higiene + exfoliación", "categoria": "Faciales", "duracion": 50, "precio": 45, "descripcion": "Limpieza profunda más exfoliación para renovar la piel."},
    {"nombre": "Higiene + exfoliación + mascarilla", "categoria": "Faciales", "duracion": 60, "precio": 50, "descripcion": "Tratamiento facial completo con limpieza, exfoliación y mascarilla nutritiva."},
    {"nombre": "Máscara de luz LED", "categoria": "Faciales", "duracion": 20, "precio": 20, "descripcion": "Estimula el colágeno y la elastina, oxigena y nutre la piel desde dentro."},
    {"nombre": "LED + masaje facial", "categoria": "Faciales", "duracion": 50, "precio": 50, "descripcion": "Combina los beneficios de la luz LED con un masaje facial relajante."},
    {"nombre": "Microneedling facial", "categoria": "Faciales", "duracion": 70, "precio": 70, "descripcion": "Incluye limpieza profunda y estimula la regeneración natural de la piel."},
]


def mongo_disponible():
    try:
        client.admin.command("ping")
        return True
    except ServerSelectionTimeoutError:
        return False


def inicializar_datos():
    if not mongo_disponible():
        return
    for servicio in SERVICIOS_INICIALES:
        servicios_col.update_one(
            {"nombre": servicio["nombre"]},
            {"$set": servicio},
            upsert=True,
        )


def obtener_servicios():
    if not mongo_disponible():
        return SERVICIOS_INICIALES
    servicios = list(servicios_col.find().sort("nombre", 1))
    for servicio in servicios:
        if servicio.get("categoria") not in {"Corporales", "Faciales"}:
            nombre = servicio.get("nombre", "").lower()
            servicio["categoria"] = "Faciales" if "facial" in nombre else "Corporales"
    return servicios


def obtener_reservas():
    if not mongo_disponible():
        return []
    return list(reservas_col.find().sort("fecha", 1).sort("hora", 1))


def horarios_para_fecha(fecha):
    if fecha.weekday() < 5:
        return HORARIOS_LABORABLES
    if fecha.weekday() == 5:
        return HORARIOS_SABADO
    return []


def construir_semana(fecha_inicio):
    hoy = datetime.now().date()
    ocupados = {
        (reserva.get("fecha"), reserva.get("hora"))
        for reserva in obtener_reservas()
        if reserva.get("estado") != "cancelada"
    }
    semana = []

    for desplazamiento in range(7):
        fecha = fecha_inicio + timedelta(days=desplazamiento)
        fecha_iso = fecha.isoformat()
        pasado = fecha < hoy
        horarios = horarios_para_fecha(fecha)
        semana.append({
            "fecha": fecha_iso,
            "dia": DIAS_SEMANA[fecha.weekday()],
            "dia_corto": DIAS_SEMANA[fecha.weekday()][:3],
            "numero": fecha.day,
            "mes": MESES[fecha.month - 1][:3],
            "pasado": pasado,
            "cerrado": not horarios,
            "horarios": [
                {
                    "hora": hora,
                    "disponible": not pasado and (fecha_iso, hora) not in ocupados,
                }
                for hora in horarios
            ],
        })

    return semana


def admin_requerido(vista):
    @wraps(vista)
    def vista_protegida(*args, **kwargs):
        if not session.get("admin_autenticado"):
            flash("Inicia sesión para acceder al panel.", "error")
            return redirect(url_for("admin_login"))
        return vista(*args, **kwargs)

    return vista_protegida


def obtener_token_csrf():
    if "csrf_token" not in session:
        session["csrf_token"] = token_urlsafe(32)
    return session["csrf_token"]


@app.before_request
def validar_token_csrf():
    if request.method == "POST":
        esperado = session.get("csrf_token", "")
        recibido = request.form.get("csrf_token", "")
        if not esperado or not compare_digest(esperado, recibido):
            abort(400)


@app.context_processor
def contexto_global():
    return {
        "mongo_ok": mongo_disponible(),
        "csrf_token": obtener_token_csrf(),
    }


@app.route("/")
def inicio():
    servicios = obtener_servicios()[:3]
    reservas_count = reservas_col.count_documents({}) if mongo_disponible() else 0
    return render_template(
        "inicio.html",
        servicios=servicios,
        reservas_count=reservas_count,
        resenas=RESENAS_GOOGLE,
        google_reviews_url=GOOGLE_REVIEWS_URL,
    )


@app.route("/servicios")
def servicios():
    categoria = request.args.get("categoria", "todos").lower()
    categorias_validas = {"todos", "corporales", "faciales"}
    if categoria not in categorias_validas:
        categoria = "todos"

    servicios_filtrados = obtener_servicios()
    if categoria != "todos":
        servicios_filtrados = [
            servicio for servicio in servicios_filtrados
            if servicio.get("categoria", "").lower() == categoria
        ]

    return render_template(
        "servicios.html",
        servicios=servicios_filtrados,
        categoria_actual=categoria,
    )


@app.route("/reservas", methods=["GET", "POST"])
def reservas():
    servicios = obtener_servicios()
    hoy = datetime.now().date()
    vista = request.args.get("vista", "cuadricula").lower()
    if vista not in {"lista", "cuadricula", "dia"}:
        vista = "cuadricula"

    try:
        fecha_inicio = datetime.strptime(request.args.get("inicio", ""), "%Y-%m-%d").date()
    except ValueError:
        fecha_inicio = hoy - timedelta(days=hoy.weekday())
    fecha_inicio -= timedelta(days=fecha_inicio.weekday())
    semana = construir_semana(fecha_inicio)

    try:
        fecha_dia = datetime.strptime(request.args.get("dia", ""), "%Y-%m-%d").date()
    except ValueError:
        fecha_dia = hoy
    fechas_semana = {dia["fecha"] for dia in semana}
    if fecha_dia.isoformat() not in fechas_semana:
        fecha_dia = next(
            (datetime.strptime(dia["fecha"], "%Y-%m-%d").date() for dia in semana if not dia["cerrado"]),
            fecha_inicio,
        )
    dia_seleccionado = next(dia for dia in semana if dia["fecha"] == fecha_dia.isoformat())

    if request.method == "POST":
        if not mongo_disponible():
            flash("MongoDB no está conectado. Actívalo antes de guardar reservas.", "error")
            return redirect(url_for("reservas"))

        turno = request.form.get("turno", "").strip()
        try:
            fecha, hora = turno.split("|", 1)
            fecha_reserva = datetime.strptime(fecha, "%Y-%m-%d").date()
        except (ValueError, TypeError):
            fecha_reserva = None
            fecha = ""
            hora = ""

        if (
            not fecha_reserva
            or fecha_reserva < datetime.now().date()
            or hora not in horarios_para_fecha(fecha_reserva)
        ):
            flash("Elige una fecha y una hora que estén disponibles.", "error")
            return redirect(url_for("reservas"))
        servicio_elegido = request.form.get("servicio", "").strip()
        nombres_servicios = {servicio.get("nombre") for servicio in servicios}

        if servicio_elegido not in nombres_servicios:
            flash("Elige uno de los servicios disponibles.", "error")
            return redirect(url_for("reservas"))

        if reservas_col.find_one({"fecha": fecha, "hora": hora, "estado": {"$ne": "cancelada"}}):
            flash("Ese horario acaba de ocuparse. Elige otro disponible.", "error")
            return redirect(url_for("reservas"))

        nueva_reserva = {
            "nombre": request.form.get("nombre", "").strip(),
            "telefono": request.form.get("telefono", "").strip(),
            "servicio": servicio_elegido,
            "fecha": fecha,
            "hora": hora,
            "comentario": request.form.get("comentario", "").strip(),
            "estado": "pendiente",
            "creada_en": datetime.now(),
        }

        campos_obligatorios = ["nombre", "telefono", "servicio", "fecha", "hora"]
        if not all(nueva_reserva[campo] for campo in campos_obligatorios):
            flash("Completa todos los campos obligatorios para crear la reserva.", "error")
            return redirect(url_for("reservas"))

        reservas_col.insert_one(nueva_reserva)
        flash("Reserva creada correctamente.", "ok")
        return redirect(url_for("reservas"))

    return render_template(
        "reservas.html",
        servicios=servicios,
        semana=semana,
        vista=vista,
        fecha_inicio=fecha_inicio,
        fecha_anterior=(fecha_inicio - timedelta(days=7)).isoformat(),
        fecha_siguiente=(fecha_inicio + timedelta(days=7)).isoformat(),
        numero_semana=fecha_inicio.isocalendar().week,
        fin_semana=fecha_inicio + timedelta(days=6),
        dia_seleccionado=dia_seleccionado,
    )


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if session.get("admin_autenticado"):
        return redirect(url_for("panel"))

    if request.method == "POST":
        access_key = app.config["ADMIN_ACCESS_KEY"]
        submitted_key = request.form.get("access_key", "")
        if access_key and compare_digest(access_key, submitted_key):
            session.clear()
            session["admin_autenticado"] = True
            session.permanent = True
            flash("Sesión de administración iniciada.", "ok")
            return redirect(url_for("panel"))
        flash("La clave de acceso no es correcta.", "error")

    return render_template("admin_login.html")


@app.post("/admin/logout")
@admin_requerido
def admin_logout():
    session.clear()
    flash("Sesión cerrada correctamente.", "ok")
    return redirect(url_for("inicio"))


@app.route("/panel")
@admin_requerido
def panel():
    estado = request.args.get("estado", "todas")
    reservas = obtener_reservas()
    if estado != "todas":
        reservas = [reserva for reserva in reservas if reserva.get("estado") == estado]
    return render_template("panel.html", reservas=reservas, estado_actual=estado)


def preparar_valor_csv(valor):
    texto = str(valor or "")
    if texto.startswith(("=", "+", "-", "@")):
        return f"'{texto}"
    return texto


@app.route("/panel/exportar.csv")
@admin_requerido
def exportar_reservas():
    estado = request.args.get("estado", "todas")
    if estado not in {"todas", "pendiente", "confirmada", "cancelada"}:
        estado = "todas"

    reservas = obtener_reservas()
    if estado != "todas":
        reservas = [reserva for reserva in reservas if reserva.get("estado") == estado]

    archivo = StringIO()
    escritor = csv.writer(archivo, delimiter=";", lineterminator="\n")
    escritor.writerow(["Nombre", "Teléfono", "Servicio", "Fecha", "Hora", "Preferencias", "Estado", "Creada"])

    for reserva in reservas:
        creada = reserva.get("creada_en", "")
        if isinstance(creada, datetime):
            creada = creada.strftime("%d/%m/%Y %H:%M")
        escritor.writerow([
            preparar_valor_csv(reserva.get("nombre")),
            preparar_valor_csv(reserva.get("telefono")),
            preparar_valor_csv(reserva.get("servicio")),
            preparar_valor_csv(reserva.get("fecha")),
            preparar_valor_csv(reserva.get("hora")),
            preparar_valor_csv(reserva.get("comentario")),
            preparar_valor_csv(reserva.get("estado")),
            preparar_valor_csv(creada),
        ])

    nombre_archivo = f"reservas_zen_{datetime.now():%Y-%m-%d}.csv"
    return Response(
        "\ufeff" + archivo.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{nombre_archivo}"'},
    )


@app.route("/reservas/<reserva_id>/estado", methods=["POST"])
@admin_requerido
def cambiar_estado(reserva_id):
    if mongo_disponible():
        nuevo_estado = request.form.get("estado", "pendiente")
        reservas_col.update_one({"_id": ObjectId(reserva_id)}, {"$set": {"estado": nuevo_estado}})
        flash("Estado actualizado.", "ok")
    return redirect(url_for("panel"))


@app.route("/reservas/<reserva_id>/eliminar", methods=["POST"])
@admin_requerido
def eliminar_reserva(reserva_id):
    if mongo_disponible():
        reservas_col.delete_one({"_id": ObjectId(reserva_id)})
        flash("Reserva eliminada.", "ok")
    return redirect(url_for("panel"))


if __name__ == "__main__":
    inicializar_datos()
    modo_debug = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    app.run(debug=modo_debug)
