import unittest
from types import SimpleNamespace

from app import crear_app
from categorias import CATEGORIAS
from pymongo.errors import DuplicateKeyError
from werkzeug.security import check_password_hash


class RepositorioEnMemoria:
    def __init__(self):
        self.jugadores = {}

    def crear_cuenta(self, nombre, hash_contrasena):
        if nombre in self.jugadores:
            jugador = self.jugadores[nombre]
            if not hasattr(jugador, "hash_contrasena"):
                jugador.hash_contrasena = hash_contrasena
                return
            raise DuplicateKeyError("duplicate key")
        self.jugadores[nombre] = SimpleNamespace(
            nombre=nombre,
            hash_contrasena=hash_contrasena,
            juegos_ganados=0,
            juegos_perdidos=0,
        )

    def obtener_hash_contrasena(self, nombre):
        jugador = self.jugadores.get(nombre)
        return jugador.hash_contrasena if jugador else None

    def buscar(self, nombre):
        return self.jugadores.get(nombre)

    def registrar_resultado(self, nombre, gano):
        campo = "juegos_ganados" if gano else "juegos_perdidos"
        jugador = self.jugadores[nombre]
        setattr(jugador, campo, getattr(jugador, campo) + 1)

    def ranking(self):
        return sorted(
            self.jugadores.values(),
            key=lambda jugador: (-jugador.juegos_ganados, jugador.juegos_perdidos, jugador.nombre),
        )


class FlujoAhorcadoTests(unittest.TestCase):
    def setUp(self):
        self.repositorio = RepositorioEnMemoria()
        self.app = crear_app(self.repositorio)
        self.app.config.update(TESTING=True, SECRET_KEY="test")
        self.cliente = self.app.test_client()

    def iniciar_sesion(self):
        respuesta = self.cliente.post(
            "/registrarse",
            data={
                "nombre": "Ana",
                "contrasena": "contrasena-segura",
                "confirmacion": "contrasena-segura",
            },
        )
        self.assertEqual(respuesta.status_code, 302)
        self.assertTrue(respuesta.location.endswith("/menu"))

    def test_login_navegacion_y_cierre_de_sesion(self):
        respuesta_inicio = self.cliente.get("/")
        self.assertEqual(respuesta_inicio.status_code, 200)
        self.assertIn("Entra al juego".encode(), respuesta_inicio.data)
        self.assertIn("Registrarte".encode(), respuesta_inicio.data)
        self.assertIn("Iniciar sesión".encode(), respuesta_inicio.data)
        self.assertIn(b'href="/registrarse"', respuesta_inicio.data)
        self.assertIn(b'href="/iniciar-sesion"', respuesta_inicio.data)

        self.iniciar_sesion()
        respuesta_menu = self.cliente.get("/menu")
        self.assertEqual(respuesta_menu.status_code, 200)
        self.assertNotIn("Configuración".encode(), respuesta_menu.data)
        self.assertEqual(self.cliente.get("/configuracion").status_code, 404)
        self.assertEqual(self.cliente.get("/ranking").status_code, 200)

        respuesta = self.cliente.get("/categorias")
        self.assertEqual(respuesta.status_code, 200)
        for categoria in CATEGORIAS.values():
            self.assertIn(categoria["nombre"].encode(), respuesta.data)

        self.cliente.post("/salir")
        self.assertEqual(self.cliente.get("/menu").status_code, 302)

    def test_registro_y_acceso_requieren_credenciales_validas(self):
        self.assertEqual(self.cliente.get("/registrarse").status_code, 200)
        self.assertEqual(self.cliente.get("/iniciar-sesion").status_code, 200)

        respuesta = self.cliente.post(
            "/registrarse",
            data={
                "nombre": "Ana",
                "contrasena": "contrasena-segura",
                "confirmacion": "otra-contrasena",
            },
        )
        self.assertTrue(respuesta.location.endswith("/registrarse"))
        self.assertIsNone(self.repositorio.buscar("Ana"))

        self.cliente.post(
            "/registrarse",
            data={
                "nombre": "Ana",
                "contrasena": "contrasena-segura",
                "confirmacion": "contrasena-segura",
            },
        )
        jugador = self.repositorio.buscar("Ana")
        self.assertNotEqual(jugador.hash_contrasena, "contrasena-segura")
        self.assertTrue(check_password_hash(jugador.hash_contrasena, "contrasena-segura"))
        self.cliente.post("/salir")

        respuesta = self.cliente.post(
            "/iniciar-sesion",
            data={"nombre": "Ana", "contrasena": "incorrecta"},
        )
        self.assertTrue(respuesta.location.endswith("/iniciar-sesion"))
        self.assertEqual(self.cliente.get("/menu").status_code, 302)

        respuesta = self.cliente.post(
            "/iniciar-sesion",
            data={"nombre": "Ana", "contrasena": "contrasena-segura"},
        )
        self.assertTrue(respuesta.location.endswith("/menu"))
        self.assertEqual(self.cliente.get("/menu").status_code, 200)

    def test_registro_agrega_contrasena_a_perfil_existente_sin_perder_estadisticas(self):
        self.repositorio.jugadores["Ana"] = SimpleNamespace(
            nombre="Ana",
            juegos_ganados=3,
            juegos_perdidos=1,
        )
        respuesta = self.cliente.post(
            "/registrarse",
            data={
                "nombre": "Ana",
                "contrasena": "contrasena-segura",
                "confirmacion": "contrasena-segura",
            },
        )

        self.assertTrue(respuesta.location.endswith("/menu"))
        jugador = self.repositorio.buscar("Ana")
        self.assertEqual(jugador.juegos_ganados, 3)
        self.assertEqual(jugador.juegos_perdidos, 1)
        self.assertTrue(check_password_hash(jugador.hash_contrasena, "contrasena-segura"))

    def test_categoria_partida_letras_y_resultado(self):
        self.iniciar_sesion()

        for clave, categoria in CATEGORIAS.items():
            respuesta = self.cliente.post(f"/categorias/{clave}/jugar")
            self.assertEqual(respuesta.status_code, 302)
            with self.cliente.session_transaction() as estado:
                palabra = estado["partida"]["palabra"]
                self.assertEqual(estado["categoria"], clave)
                self.assertIn(palabra.lower(), [item.lower() for item in categoria["palabras"]])
                self.assertEqual(estado["partida"]["intentos_iniciales"], 8)
                self.assertEqual(estado["partida"]["intentos_restantes"], 8)

            respuesta = self.cliente.get("/jugar")
            self.assertEqual(respuesta.status_code, 200)
            self.assertNotIn(palabra.encode(), respuesta.data)

            for letra in sorted(set(caracter for caracter in palabra if caracter.isalpha())):
                respuesta = self.cliente.post("/jugar", data={"letra": letra})
            self.assertEqual(respuesta.status_code, 200)
            self.assertIn("¡Felicidades!".encode(), respuesta.data)

        self.assertEqual(self.repositorio.buscar("Ana").juegos_ganados, len(CATEGORIAS))

    def test_letra_incorrecta_descuenta_una_vida_y_repetir_no_descuenta(self):
        self.iniciar_sesion()
        self.cliente.post("/categorias/comida/jugar")
        with self.cliente.session_transaction() as estado:
            palabra = estado["partida"]["palabra"].upper()
            intento = next(letra for letra in "ABCDEFGHIJKLMNOPQRSTUVWXYZ" if letra not in palabra)

        self.cliente.post("/jugar", data={"letra": intento})
        with self.cliente.session_transaction() as estado:
            self.assertEqual(estado["partida"]["intentos_restantes"], 7)
        self.cliente.post("/jugar", data={"letra": intento})
        with self.cliente.session_transaction() as estado:
            self.assertEqual(estado["partida"]["intentos_restantes"], 7)

    def test_escenario_industrial_se_conecta_a_la_partida_y_sus_assets(self):
        self.iniciar_sesion()
        self.cliente.post("/categorias/industrial/jugar")

        respuesta = self.cliente.get("/jugar")
        self.assertEqual(respuesta.status_code, 200)
        self.assertIn(b"No pierdas la insignia", respuesta.data)
        self.assertIn(b"escenario-industrial.css", respuesta.data)
        self.assertIn(b"escenario-industrial.js", respuesta.data)
        self.assertIn(b"img/industrial/calis1.png", respuesta.data)
        self.assertNotIn(b"btn-error", respuesta.data)
        for imagen in (
            "cabeza3.png", "calis1.png", "fuego4.png", "hojas6.png",
            "patas8.png", "plato2.png", "tapa5.png", "yunque7.png",
        ):
            respuesta_asset = self.cliente.get(f"/static/img/industrial/{imagen}")
            self.assertEqual(respuesta_asset.status_code, 200)
            respuesta_asset.close()

        with self.cliente.session_transaction() as estado:
            palabra = estado["partida"]["palabra"].upper()
        letra_incorrecta = next(
            letra for letra in "ABCDEFGHIJKLMNOPQRSTUVWXYZ" if letra not in palabra
        )
        self.cliente.post("/jugar", data={"letra": letra_incorrecta})
        respuesta = self.cliente.get("/jugar")
        self.assertIn(b"--errores: 1", respuesta.data)
        self.assertIn(b">7</span>", respuesta.data)

        for letra in sorted(set(caracter for caracter in palabra if caracter.isalpha())):
            respuesta = self.cliente.post("/jugar", data={"letra": letra})
        self.assertIn(b'data-ganado="1"', respuesta.data)

    def test_ranking_ordena_por_victorias(self):
        self.iniciar_sesion()
        self.repositorio.jugadores["Beto"] = SimpleNamespace(
            nombre="Beto", juegos_ganados=4, juegos_perdidos=2
        )
        self.repositorio.jugadores["Ana"].juegos_ganados = 2
        respuesta = self.cliente.get("/ranking")
        self.assertLess(respuesta.data.index(b"Beto"), respuesta.data.index(b"Ana"))


if __name__ == "__main__":
    unittest.main()