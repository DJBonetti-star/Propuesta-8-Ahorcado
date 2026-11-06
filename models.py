class Jugador:
    def __init__(self, nombre, juegos_ganados=0, juegos_perdidos=0):
        self.nombre = nombre
        self.juegos_ganados = juegos_ganados
        self.juegos_perdidos = juegos_perdidos

    @classmethod
    def desde_documento(cls, documento):
        return cls(
            nombre=documento["nombre"],
            juegos_ganados=documento.get("juegos_ganados", 0),
            juegos_perdidos=documento.get("juegos_perdidos", 0),
        )


class Palabra:
    def __init__(self, palabra, letras_correctas=None):
        self.palabra = palabra.upper()
        self.letras_correctas = letras_correctas or []

    def adivinar(self, letra):
        letra = letra.upper()
        if letra in self.palabra:
            if letra not in self.letras_correctas:
                self.letras_correctas.append(letra)
            return True
        return False

    def mostrar(self):
        return "".join(
            letra if not letra.isalpha() or letra in self.letras_correctas else "_"
            for letra in self.palabra
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
        self.palabra = palabra
        self.intentos_restantes = intentos_restantes
        self.letras_intentadas = letras_intentadas or []
        self.intentos_iniciales = intentos_iniciales or self.INTENTOS_INICIALES

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
            "letras_correctas": self.palabra.letras_correctas,
            "intentos_restantes": self.intentos_restantes,
            "intentos_iniciales": self.intentos_iniciales,
            "letras_intentadas": self.letras_intentadas,
        }

    def comprobar_letra(self, letra):
        letra = letra.upper()
        if letra in self.letras_intentadas:
            return "repetida"
        self.letras_intentadas.append(letra)
        if self.palabra.adivinar(letra):
            return True
        self.intentos_restantes -= 1
        return False

    @property
    def gano(self):
        return all(
            not letra.isalpha() or letra in self.palabra.letras_correctas
            for letra in self.palabra.palabra
        )

    @property
    def perdio(self):
        return self.intentos_restantes <= 0

    @property
    def terminada(self):
        return self.gano or self.perdio
