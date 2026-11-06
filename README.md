# Juego del ahorcado

Aplicación web en Python con Flask. La lógica está organizada con programación
orientada a objetos:

- `Jugador` representa al jugador y sus estadísticas.
- `Palabra` y `PartidaAhorcado` administran las reglas y el estado de cada
  partida.
- `categorias.py` centraliza las palabras y la ambientación de las cinco
  categorías, y selecciona una palabra al azar.
- `RepositorioJugadores` concentra las operaciones de MongoDB.
- `crear_app` configura Flask y conecta las rutas con los objetos anteriores.

MongoDB guarda cada jugador en `juego_ahorcado.jugadores`, con los campos
`nombre`, `juegos_ganados` y `juegos_perdidos`.

## Instrucciones para ejecutar en Windows

### 1. Instala los programas necesarios

Instala Python 3 y MongoDB Community Server. Durante la instalación de MongoDB,
deja habilitada la opción de instalarlo como servicio de Windows.

### 2. Inicia MongoDB

Abre PowerShell. Si instalaste MongoDB como servicio, comprueba su estado:

```powershell
Get-Service MongoDB
```

Si aparece detenido, inicia PowerShell como administrador y ejecuta:

```powershell
Start-Service MongoDB
```

También puedes usar una instancia de MongoDB Atlas; en ese caso, ten a mano su
cadena de conexión.

### 3. Abre la carpeta del proyecto

En PowerShell, cambia la ruta por la ubicación donde guardaste el proyecto:

```powershell
cd "C:\Users\Estudiante\Desktop\juego_ahorcado-main"
```

### 4. Crea y activa un entorno virtual

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Si PowerShell impide activar el entorno, ejecuta una vez:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Luego vuelve a ejecutar el comando de activación.

### 5. Instala las dependencias

```powershell
python -m pip install -r requirements.txt
```

### 6. Configura la conexión y ejecuta la aplicación

Para MongoDB instalado en tu computadora:

```powershell
$env:MONGODB_URI = "mongodb://localhost:27017/"
$env:FLASK_SECRET_KEY = "escribe-aqui-una-clave-local"
python app.py
```

Para MongoDB Atlas, usa la cadena proporcionada por Atlas en lugar de la
dirección local:

```powershell
$env:MONGODB_URI = "mongodb+srv://USUARIO:CLAVE@TU_CLUSTER/"
$env:FLASK_SECRET_KEY = "escribe-aqui-una-clave-local"
python app.py
```

Mantén abierta esa ventana de PowerShell mientras uses la aplicación.

### 7. Abre el juego en el navegador

Visita [http://127.0.0.1:5000](http://127.0.0.1:5000), escribe el nombre del
jugador y selecciona **Continuar**. Desde el menú principal puedes iniciar una
partida, elegir entre Comida, Industrial, Aplicaciones, Películas o Videojuegos,
consultar el ranking y jugar con ocho intentos por ronda. Cada ronda elige una
palabra al azar de su categoría. Al terminar, MongoDB actualiza las victorias o derrotas;
**Otra palabra** inicia una nueva ronda dentro de la misma categoría.

La base de datos y la colección se crean automáticamente al registrar el primer
jugador. Para detener el servidor, vuelve a PowerShell y pulsa `Ctrl+C`.
