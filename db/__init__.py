from sqlalchemy import create_engine
import json
# Datos de conexión

def load_credentials():
    """
    Cargar las credenciales de la base de datos desde un archivo de configuración.
    """
    # Aquí podrías implementar la lógica para cargar las credenciales desde un archivo
    # o variables de entorno. Por simplicidad, se definen directamente en el código.
    return json.load(open(".credentials/posgres_credentials.json", "r", encoding="utf-8"))


credentials = load_credentials()
db_host = credentials["host"]
db_port = credentials["port"]
db_name = credentials["database"]
db_user = credentials["username"]
db_password = credentials["password"]

engine = create_engine(f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}")
