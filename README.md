# Impacto de la vacuna en Chile

Este dashboard recoge varias implementaciones de como medir el impacto de la vacuna, las ideas en general vienen de https://ourworldindata.org/vaccination-israel-impact y del estudio de La Tercera.

# Estructura de la app
La estructura del repo es:

```
root
└── assets
└── local_postprocessed_data
    app.py
    components.py
    graphs_config.py
    install.sh
    process_data.ipynb
    process_data.py
    requirements-process.txt
    requirements.txt
```

La carpeta assets contiene los archivos CSS aplicados al dashboard, y la carpeta local_postprocessed_data es una versión local de los archivos de datos procesados.

# Variables de entorno
Tanto como el script que descarga los datos como el dashboard ocupan las variables de entorno `BUCKET_LOCATION` y `BUCKET_DASH_LOCATION`, por lo que estas pueden ser seteadas localmente usando (LINUX):

    $ export BUCKET_LOCATION=location
    $ export BUCKET_DASH_LOCATION=location

O creando un archivo `.env` en el root del repositorio:

    BUCKET_LOCATION=location
    BUCKET_DASH_LOCATION=location

# Dashboard
El archivo `app.py` contiene el dashboard y junta todo para levantar el servidor. Para ejecutar de modo local es necesario utilizar:

    $ python app.py

Este módulo importa `components.py` y `graphs.config.py`, que contienen componentes y la configuración de los gráficos.
La fuente de datos es la carpeta que haya sido seteada en la variable de entorno BUCKET_DASH_LOCATION.

# Fuentes de datos
La fuente de datos es el github oficial del MinCiencia https://github.com/MinCiencia/Datos-COVID19, por lo que es necesario que donde se ejecute se tenga una copia local del repositorio, que luego es procesado.

Se incorpora el script `install.sh`, que hace un checkout sparse de modo de no tener que bajar todo el repositorio.

Luego, es necesario ejecutar el script `process_data.py` que hace algunas transformaciones y los deja en la carpeta de salida (BUCKET_LOCATION).