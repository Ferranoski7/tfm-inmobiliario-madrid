import sys
sys.path.append("..")  # Para importar desde el directorio padre

from etl.idealista.db import IdealistaDB
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import osmnx as ox
from shapely.geometry import MultiPolygon, Polygon
import numpy as np

# Cargar datos de ventas
db = IdealistaDB(output_folder="../data")
db.read_data(city="Madrid")
df_raw = db.results["Madrid_Sale"]
print('Columnas disponibles en df_raw:', df_raw.columns)
# Usar df_raw directamente si ya es un DataFrame
sale_df = df_raw if isinstance(df_raw, pd.DataFrame) else df_raw[list(df_raw.keys())[0]]

# Cargar polígonos de barrios desde archivo local
polygons_raw = db.results["Madrid_Polygons"]
print('Columnas disponibles en barrios_gdf:', polygons_raw.columns)
print(polygons_raw.head())

# Función para convertir geometría anidada a MultiPolygon

def convert_to_multipolygon(geom_list):
    # geom_list: lista de polígonos (cada uno es una lista de coordenadas)
    if isinstance(geom_list, (list, np.ndarray)):
        return MultiPolygon([Polygon(polygon[0]) for polygon in geom_list])
    return geom_list

# Convertir la columna geometry
polygons_raw['geometry'] = polygons_raw['geometry'].apply(convert_to_multipolygon)
barrios_gdf = gpd.GeoDataFrame(polygons_raw, geometry='geometry')

# Convertir sale_df a GeoDataFrame si tiene columnas de lat/lon
if 'LONGITUDE' in sale_df.columns and 'LATITUDE' in sale_df.columns:
    sale_gdf = gpd.GeoDataFrame(
        sale_df,
        geometry=gpd.points_from_xy(sale_df.LONGITUDE, sale_df.LATITUDE),
        crs=barrios_gdf.crs
    )
else:
    raise ValueError('sale_df debe tener columnas LONGITUDE y LATITUDE para asignar barrio')

# Asignar barrio a cada entrada usando spatial join
sale_gdf = gpd.sjoin(sale_gdf, barrios_gdf[['LOCATIONNAME', 'geometry']], how='left', predicate='within')

# Calcular precio medio por barrio
mean_prices = sale_gdf.groupby('LOCATIONNAME')['PRICE'].mean().reset_index()
barrios_gdf = barrios_gdf.merge(mean_prices, on='LOCATIONNAME', how='left')

# Crear identificador de barrio de 2 letras
barrios_gdf['BARRIO_ID'] = barrios_gdf['LOCATIONNAME'].str[:].str.upper()

# Seleccionar los 5 barrios más caros y los 5 más baratos
sorted_barrios = barrios_gdf.dropna(subset=['PRICE']).sort_values('PRICE', ascending=False)
barrios_mas_caros = sorted_barrios.head(5)
barrios_mas_baratos = sorted_barrios.tail(10)
barrios_gdf_filtrado = sorted_barrios

# Asignar el orden de precio (solo para los seleccionados)
barrios_gdf_filtrado = barrios_gdf_filtrado.copy()
barrios_gdf_filtrado['ORDEN'] = range(1, len(barrios_gdf_filtrado)+1)

# Graficar todos los barrios
fig, ax = plt.subplots(1, 1, figsize=(12, 8))
barrios_gdf.plot(column='PRICE', ax=ax, legend=True, cmap='OrRd', edgecolor='black')

# Añadir identificador solo a los seleccionados
for idx, row in barrios_gdf_filtrado.iterrows():
    if row['geometry'] and hasattr(row['geometry'], 'centroid'):
        x, y = row['geometry'].centroid.x, row['geometry'].centroid.y
        ax.text(x, y, str(row['ORDEN']), fontsize=8, ha='center', va='center', color='black', weight='bold')

print('Barrios más caros:')
for idx, row in barrios_gdf_filtrado.iterrows():
    print(f"{idx+1}. {row['LOCATIONNAME']} - Precio medio: {row['PRICE']}")

# Exportar lista de barrios más caros a archivo
with open('barrios_mas_caros.txt', 'w', encoding='utf-8') as f:
    f.write('Barrios más caros (Madrid):\n')
    for idx, row in barrios_gdf_filtrado.iterrows():
        f.write(f"{idx+1}. {row['LOCATIONNAME']} - Precio medio: {row['PRICE']}\n")
ax.set_title('Precio medio por barrio en Madrid en €')
plt.axis('off')
plt.tight_layout()
plt.savefig('precio_medio_barrios_madrid.png', dpi=300)
plt.show()
