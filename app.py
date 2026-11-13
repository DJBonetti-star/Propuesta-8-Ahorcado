import os

from flask import Flask, flash, redirect, render_template, request, session, url_for
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError, PyMongoError
from werkzeug.security import check_password_hash, generate_password_hash

from categorias import CATEGORIAS, palabra_aleatoria
from models import PartidaAhorcado, Palabra
from repositories import RepositorioJugadores


def crear_app(repositorio_jugadores=None):
    app = Flask(__name__)
    app.secret_key = os.environ.get(
        "FLASK_SECRET_KEY",
        "clave-juego-ahorcado",
    )

    if repositorio_jugadores is None:
        cliente_mongo = MongoClient(
            os.environ.get("MONGODB_URI", "mongodb://localhost:27017/"),
            serverSelectionTimeoutMS=5000,
        )
        coleccion = cliente_mongo["juego_ahorcado"]["jugadores"]
        repositorio_jugadores = RepositorioJugadores(coleccion)

    app.config["REPOSITORIO_JUGADORES"] = repositorio_jugadores

    @app.route("/", methods=["GET"])
    def inicio():
        jugador = None
        if "jugador" in session:
            try:
                jugador = repositorio_jugadores.buscar(session["jugador"])
            except PyMongoError:
                flash("No se pudieron consultar los datos del jugador en MongoDB.", "error")
        return render_template("index.html", jugador=jugador)

    @app.route("/registrarse", methods=["GET", "POST"])
    def registrarse():
        if request.method == "GET":
            return render_template("cuenta.html", modo="registro")

        nombre = request.form.get("nombre", "").strip()
        contrasena = request.form.get("contrasena", "")
        confirmacion = request.form.get("confirmacion", "")
        if not nombre or len(nombre) > 80:
            flash("Ingresa un nombre de hasta 80 caracteres.", "error")
            return redirect(url_for("registrarse"))
        if len(contrasena) < 8 or len(contrasena) > 128:
            flash("La contraseña debe tener entre 8 y 128 caracteres.", "error")
            return redirect(url_for("registrarse"))
        if contrasena != confirmacion:
            flash("Las contraseñas no coinciden.", "error")
            return redirect(url_for("registrarse"))

        try:
            repositorio_jugadores.crear_cuenta(
                nombre,
                generate_password_hash(contrasena),
            )
        except DuplicateKeyError:
            flash("Ese nombre ya está registrado. Inicia sesión o elige otro.", "error")
            return redirect(url_for("registrarse"))
        except PyMongoError:
            flash("No se pudo crear la cuenta. Verifica la conexión con MongoDB.", "error")
            return redirect(url_for("registrarse"))

        session["jugador"] = nombre
        return redirect(url_for("menu"))

    @app.route("/iniciar-sesion", methods=["GET", "POST"])
    def iniciar_sesion():
        if request.method == "GET":
            return render_template("cuenta.html", modo="inicio-sesion")

        nombre = request.form.get("nombre", "").strip()
        contrasena = request.form.get("contrasena", "")
        try:
            hash_guardado = repositorio_jugadores.obtener_hash_contrasena(nombre)
        except PyMongoError:
            flash("No se pudo iniciar sesión. Verifica la conexión con MongoDB.", "error")
            return redirect(url_for("iniciar_sesion"))

        if not hash_guardado or not check_password_hash(hash_guardado, contrasena):
            flash("El nombre o la contraseña son incorrectos.", "error")
            return redirect(url_for("iniciar_sesion"))

        session.clear()
        session["jugador"] = nombre
        return redirect(url_for("menu"))

    @app.route("/menu")
    def menu():
        if "jugador" not in session:
            return redirect(url_for("inicio"))
        return render_template("menu.html", jugador=buscar_jugador())

    @app.route("/categorias")
    def categorias():
        if "jugador" not in session:
            return redirect(url_for("inicio"))
        return render_template("categorias.html", categorias=CATEGORIAS)

    @app.route("/categorias/<categoria>/jugar", methods=["POST"])
    def seleccionar_categoria(categoria):
        if "jugador" not in session:
            return redirect(url_for("inicio"))
        if categoria not in CATEGORIAS:
            flash("La categoría seleccionada no existe.", "error")
            return redirect(url_for("categorias"))
        session["categoria"] = categoria
        iniciar_partida()
        return redirect(url_for("jugar"))

    @app.route("/ranking")
    def ranking():
        if "jugador" not in session:
            return redirect(url_for("inicio"))
        try:
            jugadores = repositorio_jugadores.ranking()
        except PyMongoError:
            jugadores = []
            flash("No se pudo consultar el ranking en MongoDB.", "error")
        return render_template("ranking.html", jugadores=jugadores)

    @app.route("/salir", methods=["POST"])
    def salir():
        session.clear()
        flash("Sesión cerrada.", "success")
        return redirect(url_for("inicio"))

    @app.route("/jugar", methods=["GET", "POST"])
    def jugar():
        if "jugador" not in session:
            return redirect(url_for("inicio"))
        categoria = session.get("categoria")
        if categoria not in CATEGORIAS:
            return redirect(url_for("categorias"))

        partida = obtener_partida()
        vida_perdida = False
        if request.method == "POST":
            letra = request.form.get("letra", "").strip().upper()
            if len(letra) == 1 and letra.isalpha() and not partida.terminada:
                intentos_antes = partida.intentos_restantes
                partida.comprobar_letra(letra)
                vida_perdida = partida.intentos_restantes < intentos_antes
            session["partida"] = partida.a_estado()

        gano = partida.gano
        perdio = partida.perdio
        mensaje = ""
        if gano:
            mensaje = "¡Felicidades! ¡Adivinaste la palabra!"
        elif perdio:
            mensaje = "¡Se terminaron los intentos!"

        if partida.terminada and not session.get("resultado_registrado"):
            try:
                repositorio_jugadores.registrar_resultado(
                    session["jugador"],
                    gano,
                )
            except PyMongoError:
                flash("No se pudo actualizar el resultado en MongoDB. Inténtalo de nuevo.", "error")
            else:
                session["resultado_registrado"] = True

        return render_template(
            "juego.html",
            jugador=buscar_jugador(),
            categoria=CATEGORIAS[categoria],
            categoria_clave=categoria,
            palabra_mostrada=partida.palabra.mostrar(),
            intentos=partida.intentos_restantes,
            intentos_iniciales=partida.intentos_iniciales,
            letras_intentadas=partida.letras_intentadas,
            mensaje=mensaje,
            partida_terminada=partida.terminada,
            palabra_resuelta=partida.palabra.palabra if partida.perdio else None,
            vida_perdida=vida_perdida,
        )

    @app.route("/reiniciar")
    def reiniciar():
        if "jugador" not in session:
            return redirect(url_for("inicio"))
        if session.get("categoria") not in CATEGORIAS:
            return redirect(url_for("categorias"))
        iniciar_partida()
        return redirect(url_for("jugar"))

    def iniciar_partida():
        categoria = session.get("categoria")
        if categoria not in CATEGORIAS:
            return
        partida = PartidaAhorcado(
            Palabra(palabra_aleatoria(categoria)),
        )
        session["partida"] = partida.a_estado()
        session.pop("resultado_registrado", None)

    def obtener_partida():
        estado = session.get("partida")
        if estado is None:
            iniciar_partida()
            estado = session["partida"]
        return PartidaAhorcado.desde_estado(estado)

    def buscar_jugador():
        try:
            return repositorio_jugadores.buscar(session["jugador"])
        except PyMongoError:
            flash("No se pudieron consultar los datos del jugador en MongoDB.", "error")
            return None

    return app


app = crear_app()


if __name__ == "__main__":
    app.run(debug=True)
