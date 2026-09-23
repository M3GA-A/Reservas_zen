# Reservas Zen

Aplicación web para un centro de bienestar. Permite consultar tratamientos, comprobar la disponibilidad semanal, crear reservas y gestionarlas desde un panel privado de administración.

## Funcionalidades

- Página de inicio con servicios destacados, reseñas, ubicación y horarios.
- Catálogo de tratamientos corporales y faciales.
- Calendario de disponibilidad con vista semanal y diaria.
- Formulario de reserva con validación de los campos obligatorios.
- Panel privado protegido mediante una clave de acceso.
- Cambio de estado de las reservas: pendiente, confirmada o cancelada.
- Eliminación de reservas desde el panel.
- Exportación de las reservas filtradas a un archivo CSV compatible con Excel.
- Protección de formularios mediante tokens CSRF.
- Diseño adaptable a ordenadores, tabletas y móviles.

## Tecnologías utilizadas

- **Python y Flask:** servidor, rutas, sesiones y lógica de la aplicación.
- **MongoDB y PyMongo:** almacenamiento de servicios y reservas.
- **Jinja:** generación de las páginas HTML desde Flask.
- **HTML y CSS:** estructura, estilos y diseño responsive.
- **python-dotenv:** permite que Flask lea la configuración de `.env`, como la clave de acceso al panel y la clave utilizada para proteger las sesiones, sin escribir esos valores directamente en `app.py`.
- **Google Fonts:** Playfair Display para títulos y Montserrat para el resto de la interfaz.
- **CSV:** exportación ligera de reservas para abrirlas en Excel.

## Estructura del proyecto

```text
Reservas_zen/
├── app.py                       # Aplicación Flask y lógica principal
├── requirements.txt            # Dependencias de Python
├── .env                         # Configuración privada (no se sube a Git)
├── .env.example                 # Ejemplo de las variables necesarias
├── .gitignore                   # Archivos que Git debe ignorar
├── README.md                    # Documentación del proyecto
├── templates/
│   ├── base.html                # Estructura común, navegación y pie de página
│   ├── inicio.html              # Página de inicio
│   ├── servicios.html           # Catálogo de servicios
│   ├── reservas.html            # Calendario y formulario de reserva
│   ├── admin_login.html         # Acceso privado de administración
│   ├── panel.html               # Gestión y exportación de reservas
│   └── _contacto_final.html     # Bloque reutilizable de contacto y mapa
└── static/
    ├── css/
    │   └── styles.css           # Estilos generales y responsive
    └── img/                     # Logotipo e imágenes del sitio
```

## Requisitos

- Python 3.10 o superior.
- MongoDB instalado y ejecutándose en `localhost:27017`.
- Conexión a internet para cargar las fuentes de Google Fonts y el mapa.

## Instalación

Abre una terminal dentro de la carpeta del proyecto y crea un entorno virtual:

```bash
python3 -m venv venv
source venv/bin/activate
```

En Windows, la activación se realiza con:

```powershell
venv\Scripts\activate
```

Instala las dependencias:

```bash
pip install -r requirements.txt
```

## Configuración

La configuración privada se guarda fuera del código principal. Al iniciar la aplicación, `python-dotenv` lee el archivo `.env` y carga sus valores para que `app.py` pueda utilizarlos.

### Diferencia entre `.env` y `.env.example`

- **`.env`:** contiene los valores que utiliza esta copia de la aplicación, incluida la clave real de acceso al panel. Es un archivo privado y está incluido en `.gitignore` para evitar subirlo accidentalmente a Git.
- **`.env.example`:** muestra qué variables necesita el proyecto, pero contiene valores de ejemplo. Sirve como plantilla para crear un `.env` nuevo y puede compartirse con el profesor o incluirse en un repositorio.

Los comentarios que comienzan con `#` son únicamente explicaciones: Python los ignora y no afectan al funcionamiento.

Crea el archivo privado `.env` a partir del ejemplo:

```bash
cp .env.example .env
```

Después, edita `.env` y configura sus valores. No deben añadirse espacios alrededor del signo `=`:

```env
SECRET_KEY=escribe-una-clave-interna-larga-y-privada
ADMIN_ACCESS_KEY=escribe-la-clave-para-entrar-al-panel
COOKIE_SECURE=false
FLASK_DEBUG=false
```

| Variable | Función | Configuración actual recomendada |
| --- | --- | --- |
| `SECRET_KEY` | Firma y protege la sesión de Flask y el token CSRF. No es la contraseña del panel. | Una cadena larga, aleatoria y privada. |
| `ADMIN_ACCESS_KEY` | Es la clave que se introduce para acceder al panel de administración. | Una clave de demostración para la tarea; una clave fuerte y única si se publica. |
| `COOKIE_SECURE` | Decide si el navegador solo puede enviar la cookie de sesión mediante HTTPS. | `false` en `localhost`; `true` en una web publicada con HTTPS. |
| `FLASK_DEBUG` | Activa mensajes detallados y la recarga automática durante el desarrollo. | `false` para la entrega y para producción. |

`SECRET_KEY` no se consulta ni se escribe en la web. Si se cambia, las sesiones que estuvieran abiertas dejan de ser válidas y el administrador tendrá que iniciar sesión nuevamente. Para cambiar la contraseña del panel, modifica `ADMIN_ACCESS_KEY`, guarda el archivo y reinicia la aplicación.

Esta solución evita escribir las claves directamente en `app.py`, pero no cifra el contenido de `.env`: cualquier persona que tenga acceso al archivo puede leerlo. Por eso no deben utilizarse contraseñas personales ni reutilizadas.

### Configuración para esta entrega

Como el proyecto se entregará en una carpeta comprimida y la clave es únicamente de demostración, se puede incluir el archivo `.env` para que el profesor ejecute la aplicación sin tener que configurarlo. También debe incluirse `.env.example` para mostrar la forma correcta de preparar el proyecto.

En un proyecto real, `.env` no se comparte ni se sube a GitHub. La persona que instala la aplicación copia `.env.example`, lo renombra como `.env` y establece sus propias claves privadas.

## Iniciar MongoDB

Si MongoDB fue instalado con Homebrew en macOS:

```bash
brew services start mongodb-community@8.0
```

También puede iniciarse directamente con el comando correspondiente a la instalación:

```bash
mongod
```

La aplicación utiliza la base de datos `reservas_zen` y crea las colecciones `servicios` y `reservas` cuando son necesarias.

Si MongoDB no está conectado, la web permite navegar y consultar los servicios de ejemplo, pero no puede guardar reservas.

## Ejecutar la aplicación

Con el entorno virtual activado y MongoDB en funcionamiento:

```bash
python app.py
```

Abre en el navegador:

```text
http://127.0.0.1:5000
```

Para detener el servidor, pulsa `Ctrl + C` en la terminal.

## Panel de administración

El enlace **Acceso administración** aparece en el pie de la página de inicio. También se puede acceder directamente desde:

```text
http://127.0.0.1:5000/admin/login
```

La clave utilizada es el valor de `ADMIN_ACCESS_KEY` definido en `.env`. Después de iniciar sesión, el administrador puede consultar, filtrar, actualizar, eliminar y exportar las reservas.

Para cambiar la clave de acceso, modifica `ADMIN_ACCESS_KEY` y reinicia el servidor.

La sesión del administrador dura como máximo 8 horas. Los formularios de administración están protegidos con un token CSRF para impedir que otro sitio envíe acciones en nombre del administrador.

## Exportación para Excel

El botón **Exportar a Excel** del panel genera un archivo `.csv`. La descarga respeta el filtro seleccionado y contiene el nombre, teléfono, servicio, fecha, hora, preferencias, estado y fecha de creación de cada reserva.

CSV es un formato ligero de filas y columnas que puede abrirse directamente con Microsoft Excel, LibreOffice Calc o Google Sheets.



## Adaptación futura a un negocio real

La aplicación puede reutilizarse cambiando los textos, servicios, precios, horarios, dirección y datos de contacto. Antes de publicarla también será necesario generar una `SECRET_KEY` nueva, cambiar `ADMIN_ACCESS_KEY`, utilizar HTTPS, proteger MongoDB con credenciales y preparar copias de seguridad. Cambiar únicamente la contraseña del panel no sería suficiente para una publicación real.
