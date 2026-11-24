from pymongo.collection import Collection

from models import Jugador


class RepositorioJugadores:
    def __init__(self, coleccion: Collection):
        self.__coleccion = coleccion

    def crear_cuenta(self, nombre, hash_contrasena):
        self.__coleccion.create_index("nombre", unique=True)
        self.__coleccion.insert_one(
            {
                "nombre": nombre,
                "hash_contrasena": hash_contrasena,
                "juegos_ganados": 0,
                "juegos_perdidos": 0,
            }
        )

    def obtener_hash_contrasena(self, nombre):
        documento = self.__coleccion.find_one(
            {"nombre": nombre},
            {"hash_contrasena": 1},
        )
        return documento.get("hash_contrasena") if documento else None

    def buscar(self, nombre):
        documento = self.__coleccion.find_one({"nombre": nombre})
        return Jugador.desde_documento(documento) if documento else None

    def registrar_resultado(self, nombre, gano):
        campo = "juegos_ganados" if gano else "juegos_perdidos"
        self.__coleccion.update_one(
            {"nombre": nombre},
            {"$inc": {campo: 1}},
        )

    def ranking(self, limite=20):
        documentos = self.__coleccion.find().sort(
            [
                ("juegos_ganados", -1),
                ("juegos_perdidos", 1),
                ("nombre", 1),
            ]
        ).limit(limite)
        return [Jugador.desde_documento(documento) for documento in documentos]

    def eliminar(self, nombre):
        resultado = self.__coleccion.delete_one({"nombre": nombre})
        return resultado.deleted_count > 0
