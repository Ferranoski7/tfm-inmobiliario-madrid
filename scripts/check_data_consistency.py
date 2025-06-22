
from etl.idealista.api import DatabaseDataTransformer


if __name__ == '__main__':
    import os


    # Comprobar si los datos obtenidos de la query tienen todos los campos necesarios
    def load_json_data(file_path):
        import json
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    
    data_path = os.path.abspath(os.path.join(__file__,"..","..","data/resultados_test.json"))
    data = load_json_data(data_path)
    
    transformer = DatabaseDataTransformer()
    
    for entry in data.get("elementList"):
        print(entry)
        print(transformer.transform(entry))
        exit(1)