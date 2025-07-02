# 🏙️ TFM - Plataforma de análisis del mercado inmobiliario en Madrid

Este proyecto es el Trabajo Fin de Máster (TFM) de análisis del mercado inmobiliario en Madrid. Su objetivo es recopilar, transformar, almacenar y exponer datos inmobiliarios de la ciudad, facilitando su consulta y análisis desde un frontend o herramientas externas.

## Descripción general

El sistema conecta con una API externa de un proveedor de datos inmobiliarios (Idealista), descarga información relevante sobre inmuebles en Madrid, la procesa mediante procesos ETL y la almacena en una base de datos relacional. Posteriormente, expone una API REST propia para que los datos puedan ser consultados de forma sencilla y eficiente.

## Estructura del proyecto

- `api/`: Implementación de la API REST (FastAPI), incluyendo endpoints para consultar y añdir los datos almacenados.
- `etl/`: Procesos ETL para extracción, transformación y carga de datos desde la API externa a la base de datos. Incluye lógica específica para Idealista.
- `db/`: Inicialización y utilidades para la conexión y gestión de la base de datos.
- `data/`: Ficheros de datos de ejemplo y resultados de pruebas, en formato `.rda` y `.json`.
- `scripts/`: Scripts auxiliares para comprobaciones, carga de datos y utilidades varias.

## Principales funcionalidades

- Conexión y autenticación con la API de Idealista para obtener datos de inmuebles en Madrid.
- Procesos automáticos de limpieza y transformación de datos (ETL).
- Almacenamiento eficiente en una base de datos PostgreSQL.
- Exposición de los datos mediante una API REST con filtros avanzados (precio, ubicación, superficie, habitaciones, etc.).
- Documentación automática de la API mediante Swagger (FastAPI).

## Tecnologías utilizadas

- **Lenguaje:** Python 3.10+
- **API REST:** FastAPI
- **Base de Datos:** PostgreSQL
- **ORM:** SQLAlchemy (opcional)
- **Cliente HTTP:** requests / httpx
- **Entorno virtual:** venv
- **Documentación automática:** Swagger (FastAPI)

## Ejecución rápida

1. Clona el repositorio y accede al directorio del proyecto.
2. Crea y activa un entorno virtual:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```
4. Configura las variables de entorno necesarias (API keys, credenciales de la base de datos, etc.).
5. Ejecuta los scripts ETL para cargar los datos iniciales:
   ```bash
   python scripts/load_idealista_db.py
   ```
6. Lanza la API:
   ```bash
  sh scripts/launch_api.sh
   ```

## Notas

- Los datos de ejemplo se encuentran en la carpeta `data/`.
- La documentación interactiva de la API estará disponible en `/docs` una vez lanzada la API.
- Para pruebas y comprobaciones adicionales, revisa los scripts en la carpeta `scripts/`.

---

Desarrollado como parte del TFM. Para dudas o sugerencias, contactar con el autor.

