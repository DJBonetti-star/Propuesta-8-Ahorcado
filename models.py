class Jugador:
    def __init__(self, nombre, juegos_ganados=0, juegos_perdidos=0):
        self.__nombre = nombre
        self.__juegos_ganados = juegos_ganados
        self.__juegos_perdidos = juegos_perdidos

    @property
    def nombre(self):
        return self.__nombre

    @property
    def juegos_ganados(self):
        return self.__juegos_ganados

    @property
    def juegos_perdidos(self):
        return self.__juegos_perdidos

    @classmethod
    def desde_documento(cls, documento):
        return cls(
            nombre=documento["nombre"],
            juegos_ganados=documento.get("juegos_ganados", 0),
            juegos_perdidos=documento.get("juegos_perdidos", 0),
        )


class Palabra:
    def __init__(self, palabra, letras_correctas=None):
        self.__palabra = palabra.upper()
        self.__letras_correctas = list(letras_correctas or [])

    @property
    def palabra(self):
        return self.__palabra

    @property
    def letras_correctas(self):
        return tuple(self.__letras_correctas)

    def adivinar(self, letra):
        letra = letra.upper()
        if letra in self.__palabra:
            if letra not in self.__letras_correctas:
                self.__letras_correctas.append(letra)
            return True
        return False

    def mostrar(self):
        return "".join(
            letra if not letra.isalpha() or letra in self.__letras_correctas else "_"
            for letra in self.__palabra
        )


class PartidaAhorcado:
    INTENTOS_INICIALES = 8

    def __init__(
        self,
        palabra,
        intentos_restantes=INTENTOS_INICIALES,
        letras_intentadas=None,
        intentos_iniciales=None,
    ):
        self.__palabra = palabra
        self.__intentos_restantes = intentos_restantes
        self.__letras_intentadas = list(letras_intentadas or [])
        self.__intentos_iniciales = (
            intentos_iniciales
            if intentos_iniciales is not None
            else self.INTENTOS_INICIALES
        )

    @property
    def palabra(self):
        return self.__palabra

    @property
    def intentos_restantes(self):
        return self.__intentos_restantes

    @property
    def letras_intentadas(self):
        return tuple(self.__letras_intentadas)

    @property
    def intentos_iniciales(self):
        return self.__intentos_iniciales

    @classmethod
    def desde_estado(cls, estado):
        palabra = Palabra(
            estado["palabra"],
            estado.get("letras_correctas", []),
        )
        return cls(
            palabra,
            estado.get("intentos_restantes", cls.INTENTOS_INICIALES),
            estado.get("letras_intentadas", []),
            estado.get("intentos_iniciales", cls.INTENTOS_INICIALES),
        )

    def a_estado(self):
        return {
            "palabra": self.palabra.palabra,
            "letras_correctas": list(self.palabra.letras_correctas),
            "intentos_restantes": self.intentos_restantes,
            "intentos_iniciales": self.intentos_iniciales,
            "letras_intentadas": list(self.letras_intentadas),
        }

    def comprobar_letra(self, letra):
        letra = letra.upper()
        if letra in self.__letras_intentadas:
            return "repetida"
        self.__letras_intentadas.append(letra)
        if self.palabra.adivinar(letra):
            return True
        self.__intentos_restantes -= 1
        return False

    @property
    def gano(self):
        return all(
            not letra.isalpha() or letra in self.palabra.letras_correctas
            for letra in self.palabra.palabra
        )

    @property
    def perdio(self):
        return self.__intentos_restantes <= 0

    @property
    def terminada(self):
        return self.gano or self.perdio
