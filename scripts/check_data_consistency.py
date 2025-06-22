



if __name__ == '__main__':
    import os
    from db import engine
    from sqlalchemy import inspect


    # Comprobar si los datos obtenidos de la query tienen todos los campos necesarios
    def load_json_data(file_path):
        import json
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    
    data_path = os.path.abspath(os.path.join(__file__,"..","..","data/resultados_test.json"))
    data = load_json_data(data_path)
    
    #Check the columns in madrid_sale table
    inspector = inspect(engine)
    columns = inspector.get_columns('madrid_sale')
    column_names = [col['name'] for col in columns]
    
    # Cross-check which columns are missing
    data_columns = [key.upper() for key in data["elementList"][0].keys()]
    missing_columns = [col for col in data_columns if col not in column_names]
    existing_columns = [col for col in data_columns if col in column_names]
    if missing_columns:
        print(f"Missing columns in 'madrid_sale' table: {missing_columns}")
    else:
        print("All columns are present in 'madrid_sale' table.")
        
    if existing_columns:
        print(f"Existing columns in 'madrid_sale' table: {existing_columns}")
    else:
        print("No existing columns found in 'madrid_sale' table.")