import unittest
from types import SimpleNamespace

from app import crear_app
from categorias import CATEGORIAS


class RepositorioEnMemoria:
    def __init__(self):
        self.jugadores = {}

    def crear_si_no_existe(self, nombre):
        self.jugadores.setdefault(
            nombre,
            SimpleNamespace(nombre=nombre, juegos_ganados=0, juegos_perdidos=0),
        )

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
        respuesta = self.cliente.post("/jugador", data={"nombre": "Ana"})
        self.assertEqual(respuesta.status_code, 302)
        self.assertTrue(respuesta.location.endswith("/menu"))

    def test_login_navegacion_y_cierre_de_sesion(self):
        respuesta_inicio = self.cliente.get("/")
        self.assertEqual(respuesta_inicio.status_code, 200)
        self.assertIn("Entra al juego".encode(), respuesta_inicio.data)

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