from pymongo.collection import Collection

from models import Jugador


class RepositorioJugadores:
    def __init__(self, coleccion: Collection):
        self.coleccion = coleccion

    def crear_si_no_existe(self, nombre):
        self.coleccion.update_one(
            {"nombre": nombre},
            {
                "$setOnInsert": {
                    "nombre": nombre,
                    "juegos_ganados": 0,
                    "juegos_perdidos": 0,
                }
            },
            upsert=True,
        )
        return self.buscar(nombre)

    def buscar(self, nombre):
        documento = self.coleccion.find_one({"nombre": nombre})
        return Jugador.desde_documento(documento) if documento else None

    def registrar_resultado(self, nombre, gano):
        campo = "juegos_ganados" if gano else "juegos_perdidos"
        self.coleccion.update_one(
            {"nombre": nombre},
            {"$inc": {campo: 1}},
        )

    def ranking(self, limite=20):
        documentos = self.coleccion.find().sort(
            [
                ("juegos_ganados", -1),
                ("juegos_perdidos", 1),
                ("nombre", 1),
            ]
        ).limit(limite)
        return [Jugador.desde_documento(documento) for documento in documentos]
