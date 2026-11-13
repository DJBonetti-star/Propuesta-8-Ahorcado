# La última letra — Juego del ahorcado

Aplicación web de ahorcado en español, desarrollada con Python y Flask. El
jugador elige una categoría, adivina una palabra letra por letra y dispone de
ocho intentos. El juego conserva las estadísticas de los jugadores en MongoDB.

## Contenido

- [Requisitos](#requisitos)
- [Instalación y ejecución en Windows](#instalación-y-ejecución-en-windows)
- [Cómo jugar](#cómo-jugar)
- [Estructura del proyecto](#estructura-del-proyecto)
- [Rutas de la aplicación](#rutas-de-la-aplicación)
- [Datos y persistencia](#datos-y-persistencia)
- [Personalización](#personalización)
- [Pruebas](#pruebas)
- [Solución de problemas](#solución-de-problemas)

## Requisitos

- Python 3.
- MongoDB Community Server ejecutándose en el equipo, o una instancia de
  MongoDB Atlas.
- PowerShell para seguir los comandos de esta guía.

Las dependencias Python se enumeran en `requirements.txt`: Flask, PyMongo y
Gunicorn. Flask incluye Werkzeug, que se usa para almacenar contraseñas de
forma segura.

## Instalación y ejecución en Windows

### 1. Iniciar MongoDB

Para una instalación local de MongoDB como servicio, comprueba su estado desde
PowerShell:

```powershell
Get-Service MongoDB
```

Si está detenido, abre PowerShell como administrador e inicia el servicio:

```powershell
Start-Service MongoDB
```

Si usas Atlas, prepara la cadena de conexión y asegúrate de que la dirección IP
del equipo esté autorizada en la configuración de red de Atlas.

### 2. Abrir la carpeta del proyecto

```powershell
cd "C:\Users\Estudiante\Desktop\juego_ahorcado-main"
```

Si guardaste el proyecto en otra ubicación, sustituye la ruta por la correcta.

### 3. Crear y activar un entorno virtual

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Si PowerShell bloquea la activación del entorno, puedes habilitar scripts
locales para tu usuario y volver a activar:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\.venv\Scripts\Activate.ps1
```

### 4. Instalar dependencias

```powershell
python -m pip install -r requirements.txt
```

### 5. Configurar y ejecutar

Con MongoDB local:

```powershell
$env:MONGODB_URI = "mongodb://localhost:27017/"
$env:FLASK_SECRET_KEY = "reemplaza-por-una-clave-local"
python app.py
```

Con MongoDB Atlas, usa la cadena de conexión de tu propio clúster:

```powershell
$env:MONGODB_URI = "PEGA_AQUI_LA_CADENA_DE_CONEXION_DE_ATLAS"
$env:FLASK_SECRET_KEY = "reemplaza-por-una-clave-local"
python app.py
```

No publiques ni compartas la cadena de conexión ni la clave secreta. La clave
`FLASK_SECRET_KEY` protege la sesión de Flask; define una clave privada propia,
especialmente si despliegas la aplicación. La aplicación también tiene una clave
predeterminada para facilitar el inicio local, pero no debe usarse en producción.

Deja abierta la ventana de PowerShell mientras usas el juego. Flask inicia el
servidor en modo de depuración al ejecutar `app.py`; ese modo es únicamente para
desarrollo y no debe exponerse en Internet.

### 6. Abrir el juego

En el navegador, visita [http://127.0.0.1:5000](http://127.0.0.1:5000). Esta
dirección sirve en el mismo equipo donde se está ejecutando el servidor. Para
detenerlo, vuelve a PowerShell y pulsa `Ctrl+C`.

## Cómo jugar

1. En la portada, elige **Registrarte** para crear una cuenta o **Iniciar
   sesión** para volver a un perfil existente. El registro solicita una
   contraseña de al menos ocho caracteres.
2. Desde el menú, inicia una partida o consulta el ranking.
3. Selecciona una de las cinco categorías: Comida, Industrial, Aplicaciones,
   Películas o Videojuegos.
4. Introduce una letra por turno. Las letras correctas se revelan en la palabra;
   cada letra incorrecta consume un intento. Una letra repetida no consume otro.
5. Adivina todas las letras antes de quedarte sin los ocho intentos. Al terminar,
   puedes comenzar otra palabra en la misma categoría o volver al menú.

La palabra de la ronda se elige al azar de la lista de la categoría. El estado
de la partida y el jugador actual se guardan en la sesión de Flask; las
estadísticas de victorias y derrotas se guardan en MongoDB.

## Estructura del proyecto

```text
juego_ahorcado-main/
├── app.py                       # Configuración Flask y rutas
├── categorias.py                # Categorías y selección aleatoria de palabras
├── models.py                    # Jugador, Palabra y PartidaAhorcado
├── repositories.py               # Acceso a los jugadores en MongoDB
├── requirements.txt              # Dependencias Python
├── templates/
│   ├── base.html                 # Estructura común, navegación y mensajes
│   ├── index.html                # Portada con opciones de acceso
│   ├── cuenta.html               # Formularios de registro e inicio de sesión
│   ├── menu.html                 # Menú principal
│   ├── categorias.html           # Selección de categoría
│   ├── juego.html                # Tablero y partida
│   └── ranking.html              # Clasificación de jugadores
├── static/
│   ├── styles.css                # Estilos compartidos y del juego
│   ├── escenario-comida.css      # Estilos del escenario de comida
│   ├── escenario-comida.js       # Vidas y animación de comida
│   ├── escenario-peliculas.css   # Estilos del escenario de películas
│   ├── escenario-peliculas.js    # Vidas y animación de películas
│   ├── escenario-industrial.css  # Estilos del escenario industrial
│   ├── escenario-industrial.js   # Vidas y piezas de la insignia industrial
│   ├── escenario-videojuegos.css # Escenario retro de la categoría videojuegos
│   ├── escenario-videojuegos.js  # Vidas y estados del escenario arcade
│   ├── escenario-aplicaciones.css # Escenario de la categoría aplicaciones
│   ├── escenario-aplicaciones.js  # Estados de teléfono y expresiones
│   ├── img/aplicaciones/          # Capas PNG del escenario de aplicaciones
│   └── img/industrial/           # Capas PNG del escenario industrial
└── tests/
    └── test_flujo.py              # Pruebas automatizadas del flujo
```

### Responsabilidad de los módulos

- **`app.py`** crea la aplicación con `crear_app`, conecta las rutas con las
  plantillas, coordina las partidas y maneja los mensajes de error de MongoDB.
  `crear_app` acepta un repositorio alternativo, lo que permite probar la
  aplicación sin una base de datos real.
- **`models.py`** contiene `Jugador` (estadísticas), `Palabra` (letras
  descubiertas) y `PartidaAhorcado` (intentos, letras probadas y estado de
  victoria o derrota). También permite convertir la partida a y desde el estado
  serializable guardado en la sesión.
- **`categorias.py`** define las palabras y etiquetas visuales de las categorías
  y elige una palabra al azar.
- **`repositories.py`** implementa las operaciones de persistencia de jugadores
  usando MongoDB.
- **`templates/`** contiene las páginas HTML de Jinja. `base.html` aporta el
  marco común y las demás plantillas extienden ese marco.
- **`static/`** contiene los estilos y el JavaScript de los escenarios
  temáticos. La hoja `styles.css` usa un tono oscuro para que la palabra oculta
  y las letras usadas se distingan sobre el fondo claro.
- **`tests/`** comprueba navegación, categorías, reglas de intentos y ranking
  con un repositorio en memoria.

## Rutas de la aplicación

| Método | Ruta | Función |
|---|---|---|
| `GET` | `/` | Muestra la página de inicio. |
| `GET`, `POST` | `/registrarse` | Muestra el registro y crea una cuenta con contraseña. |
| `GET`, `POST` | `/iniciar-sesion` | Muestra el acceso y valida las credenciales. |
| `GET` | `/menu` | Muestra el menú del jugador. |
| `GET` | `/categorias` | Muestra las categorías disponibles. |
| `POST` | `/categorias/<categoria>/jugar` | Selecciona categoría e inicia una partida. |
| `GET`, `POST` | `/jugar` | Muestra la partida o registra una letra. |
| `GET` | `/reiniciar` | Inicia otra palabra en la categoría elegida. |
| `GET` | `/ranking` | Muestra los primeros jugadores ordenados por resultados. |
| `POST` | `/salir` | Cierra la sesión actual. |

Las páginas de menú, categorías, juego y ranking requieren una sesión de
jugador. Si no hay sesión, la aplicación redirige al inicio.

## Datos y persistencia

La aplicación se conecta a MongoDB usando la variable de entorno `MONGODB_URI`.
Guarda jugadores en la base `juego_ahorcado`, colección `jugadores`. Cada
documento contiene el nombre, las estadísticas y el hash de la contraseña
(nunca se guarda la contraseña original):

```json
{
  "nombre": "Nombre del jugador",
  "hash_contrasena": "hash generado por Werkzeug",
  "juegos_ganados": 0,
  "juegos_perdidos": 0
}
```

Los nombres de cuenta son únicos. Si ya hay un perfil antiguo sin contraseña,
el registro con ese mismo nombre le añade una contraseña y conserva sus
estadísticas. Las estadísticas se actualizan al finalizar cada partida. El
ranking muestra hasta 20 jugadores, ordenados por victorias descendentes,
derrotas ascendentes y nombre.

La palabra, las letras intentadas y los intentos restantes viven en la sesión
del navegador, no en MongoDB. Al cerrar la sesión se elimina el jugador actual
de la sesión; sus estadísticas guardadas permanecen.

## Personalización

- Para agregar o editar palabras, modifica la lista `palabras` de la categoría
  correspondiente en `categorias.py`.
- Para agregar una categoría, define sus datos en `CATEGORIAS` y actualiza las
  vistas que presentan categorías o estilos específicos, si corresponde.
- Los colores generales y la legibilidad de la palabra y letras se ajustan en
  `static/styles.css`.
- Comida, Películas, Industrial, Aplicaciones y Videojuegos tienen escenarios
  visuales propios en sus archivos `.js` y `.css`. Las demás categorías usan el
  diseño temático general.
- El número inicial de intentos está definido por
  `PartidaAhorcado.INTENTOS_INICIALES` en `models.py`. Los escenarios visuales
  actuales usan ocho vidas.

## Pruebas

Desde la carpeta del proyecto, con las dependencias instaladas, ejecuta:

```powershell
python -m unittest discover -s tests
```

Las pruebas usan un repositorio en memoria y no necesitan conectarse a MongoDB.

## Solución de problemas

- **No se puede conectar a MongoDB:** verifica que el servicio local esté
  iniciado o que `MONGODB_URI` sea correcta. En Atlas, revisa las credenciales,
  la lista de IP permitidas y los permisos del usuario de base de datos.
- **El navegador no abre la página:** confirma que `python app.py` sigue
  ejecutándose y visita `http://127.0.0.1:5000` en el mismo equipo.
- **PowerShell bloquea la activación del entorno:** sigue el paso de
  `Set-ExecutionPolicy` de la sección de instalación.
- **No se encuentra un paquete:** activa `.venv` y vuelve a ejecutar
  `python -m pip install -r requirements.txt`.
