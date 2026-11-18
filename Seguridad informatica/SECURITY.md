# Seguridad - La última letra

## Alcance y arquitectura revisada

El proyecto es una aplicación web escrita en Python con Flask. Las rutas y reglas del juego están en `app.py`; la persistencia de jugadores se implementa en `repositories.py`; las entidades del juego están en `models.py`; la interfaz usa plantillas Jinja2 en `templates/`. La aplicación construye su conexión con PyMongo a partir de `MONGODB_URI` y guarda jugadores, hashes de contraseñas y estadísticas en MongoDB.

El código puede conectarse a MongoDB Atlas y ejecutarse en Render, pero no se inspeccionaron las variables de entorno ni la configuración de red de esos servicios. Por ello, este documento no afirma que la instancia desplegada tenga una configuración insegura.

## Hallazgos verificados en el código

Los siguientes problemas estaban presentes en el código fuente antes de los cambios de esta actividad y se corrigieron:

### 1. Clave de sesión predeterminada

- **Amenaza comprobada:** Flask usaba `clave-juego-ahorcado` como `SECRET_KEY` si no estaba definida `FLASK_SECRET_KEY`.
- **Impacto:** Una clave conocida podría permitir falsificar cookies de sesión y suplantar jugadores.
- **Mitigación aplicada:** La aplicación ahora requiere `FLASK_SECRET_KEY` no vacía al iniciar y no contiene una clave predeterminada. Se documentó la configuración local y en Render sin publicar ningún valor.
- **Estado:** Corregido en `app.py`; hay una prueba que comprueba el rechazo si la variable falta o está vacía.

### 2. Apropiación pública de perfiles antiguos sin hash

- **Amenaza comprobada:** El registro podía asignar una contraseña nueva a un documento existente que no tuviera `hash_contrasena`, sin verificar que quien se registraba fuera dueño de ese perfil.
- **Impacto:** Una persona podía tomar el control de una cuenta preexistente y sus estadísticas.
- **Mitigación aplicada:** El repositorio ya no actualiza perfiles duplicados; la creación intenta insertar una cuenta nueva y la unicidad del nombre rechaza perfiles existentes. No se eliminan ni modifican registros.
- **Estado:** Corregido en `repositories.py`; una prueba confirma que el registro público no puede apropiarse de un perfil sin hash y que sus estadísticas se conservan.

### 3. Depurador de Flask habilitado al ejecutar el archivo

- **Amenaza comprobada:** `app.py` iniciaba Flask con `debug=True`.
- **Impacto:** Si el servidor de desarrollo se expusiera, el depurador podría revelar información interna y aumentar el impacto de errores.
- **Mitigación aplicada:** La configuración de la aplicación y `app.run()` mantienen depuración desactivada. En Render se debe ejecutar con Gunicorn.
- **Estado:** Corregido en `app.py`.

## Controles de desarrollo seguro

### XSS y validación de entradas

- El nombre se recorta y se limita a 80 caracteres; se rechazan valores vacíos.
- La letra del juego debe ser un único carácter alfabético.
- La categoría se valida contra las categorías permitidas por la aplicación.
- Las plantillas Jinja2 muestran los datos con escape automático; no se usa `|safe` para los nombres.
- La prueba automatizada envía una etiqueta `<script>` y verifica que se representa escapada tanto en el menú como en el ranking.

**Prueba manual:** Registrar un nombre como `<script>alert(1)</script>`, abrir el menú y el ranking y verificar que se muestra como texto escapado y que no se ejecuta JavaScript.

### Hashing de contraseñas y recuperación de perfiles

- El registro guarda el resultado de `werkzeug.security.generate_password_hash`, no la contraseña original.
- El inicio de sesión usa `check_password_hash` para verificar la contraseña.
- Las pruebas existentes verifican que el valor persistido sea distinto del texto ingresado y que el hash valide la contraseña correcta.
- No se encontró en el código actual una ruta de migración que lea contraseñas en texto plano. No se consultó la base Atlas, así que no se afirma que la colección remota esté libre de datos históricos en texto plano.
- Los perfiles antiguos sin hash se conservan y no pueden ser reclamados desde el registro público. Si una revisión autorizada de la base confirmara contraseñas históricas en texto plano, la migración debe realizarse fuera del flujo público: verificar la propiedad de cada cuenta, generar un hash con Werkzeug, reemplazar el campo de contraseña de forma controlada y conservar nombre y estadísticas. No se ejecutó ninguna migración ni se modificaron datos.

**Pruebas manuales:** Crear una cuenta y revisar, con acceso autorizado, que MongoDB almacena un hash y no la contraseña; iniciar sesión con la contraseña correcta y luego con una incorrecta.

### Manejo de errores de MongoDB

- Las operaciones de acceso a MongoDB capturan `PyMongoError` y muestran mensajes genéricos al usuario.
- El servidor registra el tipo de operación y de excepción, sin escribir el texto de la excepción, la URI ni credenciales en el log.
- Una prueba simula un error de base de datos y verifica tanto el mensaje genérico como la ausencia de detalles internos en la respuesta y el log.

**Prueba manual:** Con una instancia de pruebas o una URI inválida, comprobar que la interfaz muestra un mensaje general y que no expone una traza, URI o credenciales.

## Riesgos hipotéticos pendientes de verificación

- **Configuración de MongoDB Atlas:** Una lista de IP demasiado amplia, credenciales con privilegios excesivos o ausencia de TLS podría exponer datos. No se verificó la configuración del proyecto Atlas. Revisarla desde la consola, sin publicar la URI; permitir únicamente las conexiones necesarias y usar un usuario de mínimo privilegio.
- **Variables de Render:** No se inspeccionó el entorno desplegado. Confirmar en el panel privado que `FLASK_SECRET_KEY` y `MONGODB_URI` están configuradas como secretos y que el servicio usa HTTPS y Gunicorn. No copiar sus valores a logs, tickets ni código.

## Verificación local

Desde la raíz del proyecto:

```powershell
python -m unittest discover -s tests -v
```

La aplicación requiere que `FLASK_SECRET_KEY` esté definida antes de iniciar. Los tests configuran una clave exclusiva de prueba y usan un repositorio en memoria; no necesitan conectarse a Atlas.
