# Proyecto de IA

Este proyecto es un ejemplo de un recomendador de películas utilizando MongoDB, Rasa y Python.

## Estructura del proyecto

El proyecto contiene los siguientes archivos y carpetas importantes:

- `.devcontainer/`: Carpeta con la configuración del Devcontainer.
- `app/`: Carpeta con el código de la aplicación.
- `app/index.py`: Archivo principal de la aplicación.
- `app/templates/`: Carpeta con las plantillas HTML de la aplicación.
- `app/static/`: Carpeta con los archivos estáticos de la aplicación.
- `app/asistente/`: Carpeta con el código del asistente virtual Rasa. 
- `app/asistente/data/`: Carpeta con los datos de entrenamiento del asistente.
- `app/asistente/actions/actions.py`: Archivo con las acciones personalizadas del asistente.
- `sprint1/`: Carpeta con el código del sprint 1.
- `data/`: Carpeta con los datos de las películas, usuarios y valoraciones. La applicación utiliza MongoDB para almacenar estos datos, por lo que es necesario tener un servidor de MongoDB en ejecución y tener los datos cargados en la base de datos.

## Requisitos

Para ejecutar este proyecto, necesitas tener instalado lo siguiente:

- [Docker](https://www.docker.com/)
- [Visual Studio Code](https://code.visualstudio.com/)
- [Visual Studio Code Remote - Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)

## Instalación

### Instalación con Devcontainer

1. Clona el repositorio y abre la carpeta del proyecto en VS Code.
2. Asegúrate de tener instalado el Devcontainer y crea y configura un archivo `.env` con las variables necesarias, se incluye un ejemplo `example.env`el cual puedes renombrar a `.env` y modificar según tus necesidades.
3. Selecciona la opción "Reopen in Container" en la parte inferior derecha de VS Code para abrir el proyecto en el Devcontainer.
4. El Devcontainer instalará automáticamente las dependencias necesarias y configurará el ambiente de desarrollo en un contenedor Docker.

### Instalación de dependencias manual

Para instalar las dependencias necesarias manualmente, ejecuta los siguientes comandos en tu ambiente de desarrollo:

```bash
pip install -r requirements.txt
```
También necesitas configurar la variable de entorno MONGO_CONNECTIONSTRING en tu ambiente de desarrollo. Por ejemplo en Linux, puedes hacerlo de la siguiente manera:

```bash
export MONGO_CONNECTIONSTRING="your_mongo_connection_string"
```

### Inicialización de la aplicación

Para inicializar y ejecutar la aplicación, utiliza los siguientes comandos:

```bash
cd app
python index.py
```


### Inicialización de Rasa

Para inicializar y entrenar Rasa, utiliza los siguientes comandos en una nueva terminal para correr las acciones personalizadas:

```bash
cd app/asistente
rasa run actions
```

En otra terminal, ejecuta el siguiente comando para correr el servidor de Rasa:

```bash
cd app/asistente
rasa run -m models --enable-api --cors "*" --debug
```

## Uso

### Acceso a la aplicación

Una vez que la aplicación y el servidor de Rasa estén en ejecución, puedes acceder a la aplicación en tu navegador web en la dirección `http://localhost:5000/`.

### Login 

Para acceder a la aplicación, puedes utilizar las siguientes credenciales en caso de haber cargado los datos de ejemplo:

- Usuario: `pantolin`
- Contraseña: `pantolin`

### Listado de películas y recomendacion

Una vez que hayas iniciado sesión, podrás ver un listado de películas y recibir recomendaciones personalizadas en base a tus valoraciones.

### Uso del asistente virtual

En la parte inferior derecha de la pantalla, puedes interactuar con el asistente virtual para recibir recomendaciones de películas y realizar otras consultas.