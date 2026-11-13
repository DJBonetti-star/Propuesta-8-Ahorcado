import random


CATEGORIAS = {
    "comida": {
        "nombre": "Comida",
        "tema": "comida",
        "escenas": ["🍳 Cocina", "🥑 Ingredientes", "🍰 Gastronomía"],
        "palabras": [
            "albondigas", "melocoton", "sandia", "asado", "chocotorta",
            "helado", "tacos", "lasaña", "hamburguesa", "milanesa", "pizza",
            "salchipapa", "champiñones", "chocolatina", "langostinos",
        ],
    },
    "industrial": {
        "nombre": "Industrial",
        "tema": "industrial",
        "escenas": ["⚙ Taller", "📐 Planos", "🔧 Herramientas"],
        "palabras": [
            "Araujo", "Bermuller", "Kolb", "computadora", "Vazquez", "mecanica",
            "estatica", "proyecto", "maqueteria", "electronica", "placa madre",
            "carpinteria", "AutoCAD", "matematicas", "cuadernillo", "calculadora",
        ],
    },
    "aplicaciones": {
        "nombre": "Aplicaciones",
        "tema": "aplicaciones",
        "escenas": ["▦ Apps", "◎ Comunidad", "⌁ Conexión"],
        "palabras": [
            "tiktok", "character AI", "chatgpt", "wattpad", "temu", "classroom",
            "discord", "pinterest", "instagram", "twitter", "youtube", "spotify",
            "whatsapp", "facebook", "messenger", "IbisPaint", "netflix", "canva",
            "linkedin", "crunchyroll", "claude", "capcut", "roblox",
        ],
    },
    "peliculas": {
        "nombre": "Películas",
        "tema": "peliculas",
        "escenas": ["▰ Sala de cine", "✦ Estrenos", "◉ Proyector"],
        "palabras": [
            "avatar", "backrooms", "obsession", "ratatouille", "interstellar",
            "beetlejuice", "transformers", "batman", "spiderman", "scream",
            "scary movie", "shrek", "titanic", "toy story", "star wars", "iron man",
        ],
    },
    "videojuegos": {
        "nombre": "Videojuegos",
        "tema": "videojuegos",
        "escenas": ["⌘ Arcade", "▣ Consola", "✣ Nivel nuevo"],
        "palabras": [
            "Sally Face", "Undertale", "OneShot", "Fortnite", "Cyberpunk",
            "Overwatch", "Minecraft", "Terraria", "Granny", "Deltarune",
            "Mine Souls", "Valorant", "Cuphead", "Among Us", "Persona", "Solitario",
            "Halo", "Doom", "Celeste", "Ultrakill", "Angry Birds", "Candy Crush",
            "Buscaminas", "Snake", "Plague Inc.", "Sonic", "Mario", "God of War",
            "Portal", "Dark Souls", "Silksong", "Devil May Cry", "Miside", "Factorio",
        ],
    },
}


def palabra_aleatoria(categoria):
    return random.choice(CATEGORIAS[categoria]["palabras"])