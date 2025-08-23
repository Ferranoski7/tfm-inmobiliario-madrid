"""
Store in excel files all the data contained in the rda files if they are not already stored.
Add to the excel files the results of ETL jsons that are found in the data/etl_jsons folder.
Store the processed data in a local folder called data/processed.
"""
import os
import pandas as pd
import json
import sys
sys.path.append("..")  # Para importar desde el directorio padre
from etl.idealista.db import IdealistaDB
from etl.idealista.api import DatabaseDataTransformer
root_dir = os.path.abspath(os.path.join(__file__,"..",".."))
print(f"Root directory: {root_dir}")
data_dir = os.path.join(root_dir, "data")
json_dir = os.path.join(data_dir, "etl_jsons")
processed_dir = os.path.join(data_dir, "processed")
if not os.path.exists(data_dir):
    os.makedirs(processed_dir)
if not os.path.exists(processed_dir):
    os.makedirs(processed_dir)
if not os.path.exists(json_dir):
    os.makedirs(json_dir)
data_files = os.listdir(data_dir)

db = IdealistaDB(output_folder=data_dir)
db.read_data(city="Madrid")
results = db.results

file_names = list(results.keys())

for file_name in file_names:
    if os.path.exists(os.path.join(processed_dir, f"{file_name}.xlsx")):
        print(f"El archivo {file_name}.xlsx ya existe. Se omite la creación.")
        continue
    df = results[file_name]
    if isinstance(df, dict):
        for key, value in df.items():
            if isinstance(value, pd.DataFrame):
                value.to_excel(os.path.join(processed_dir, f"{file_name}_{key}.xlsx"), index=False)
                print(f"Archivo {file_name}_{key}.xlsx creado con éxito.")
            else:
                print(f"El valor asociado a la clave {key} en {file_name} no es un DataFrame. Se omite.")
    elif isinstance(df, pd.DataFrame):
        df.to_excel(os.path.join(processed_dir, f"{file_name}.xlsx"), index=False)
        print(f"Archivo {file_name}.xlsx creado con éxito.")
    else:
        print(f"El resultado para {file_name} no es un DataFrame ni un diccionario. Se omite.")
# Procesar archivos JSON en la carpeta etl_jsons

transformer = DatabaseDataTransformer()
json_files = [f for f in os.listdir(json_dir) if f.endswith('.json')]

if len(json_files) == 0:
    print(f"No se encontraron archivos JSON en {json_dir}.")
    exit(0)
madrid_sale_path = os.path.join(processed_dir, "Madrid_Sale.xlsx")
madrid_sale_df = pd.read_excel(madrid_sale_path) if os.path.exists(madrid_sale_path) else pd.DataFrame()

def load_json_data(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)
for json_file in json_files:
    json_path = os.path.join(json_dir, json_file)
    data = load_json_data(json_path)

    for entry in data:
        transformed_entry = transformer.transform(entry)
        #Add this entry to the Madrid_Sale.xlsx file
        madrid_sale_df = pd.concat([madrid_sale_df, pd.DataFrame([transformed_entry])], ignore_index=True)
if not madrid_sale_df.empty:
    madrid_sale_df.to_excel(madrid_sale_path, index=False)
    print(f"Archivo {madrid_sale_path} actualizado con éxito.")
else:
    print(f"No se encontraron datos para actualizar en {madrid_sale_path}.")