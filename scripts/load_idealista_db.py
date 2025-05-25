from etl.idealista.db import IdealistaDB
from shapely.geometry import MultiPolygon, Polygon
import geopandas as gpd
from shapely import wkt
import numpy as np

from db import engine
def convert_to_multipolygon(geom_list):
    # Convierte listas anidadas en MultiPolygon
    return MultiPolygon([Polygon(polygon[0]) for polygon in geom_list])

if __name__ == '__main__':
    data = IdealistaDB(output_folder="data")
    data.read_data(city="Madrid")

    Madrid_Polygons = data.results["Madrid_Polygons"]
    Madrid_Sale = data.results["Madrid_Sale"]
    City_Center = data.results["Madrid_POIS"]["City_Center"]
    Metro = data.results["Madrid_POIS"]["Metro"]
    Castellana = data.results["Madrid_POIS"]["Castellana"]
    Madrid_Polygons['geometry'] = Madrid_Polygons['geometry'].apply(convert_to_multipolygon)

    # Convertir a GeoDataFrame
    gdf_polygons = gpd.GeoDataFrame(Madrid_Polygons, geometry='geometry')
    gdf_polygons.set_crs(epsg=4326, inplace=True)  # Asumimos coordenadas WGS84

    # Exportar a PostgreSQL (requiere extensión PostGIS habilitada)
    gdf_polygons.to_postgis('madrid_polygons', engine, if_exists='replace', index=False)

    # -----------------------------
    # EXPORTAR MADRID_SALE
    # -----------------------------
    def flatten_geometry_column(df):
        if 'geometry' in df.columns:
            df['longitude'] = df['geometry'].apply(lambda x: float(x[0]) if isinstance(x, (list, np.ndarray)) else None)
            df['latitude'] = df['geometry'].apply(lambda x: float(x[1]) if isinstance(x, (list, np.ndarray)) else None)
            df = df.drop(columns=['geometry'])
        return df

    Madrid_Sale = flatten_geometry_column(Madrid_Sale)
    Madrid_Sale.to_sql('madrid_sale', engine, if_exists='replace', index=False)

    # -----------------------------
    # EXPORTAR MADRID_POIS (3 tablas)
    # -----------------------------


    City_Center = flatten_geometry_column(City_Center)
    Metro = flatten_geometry_column(Metro)
    Castellana = flatten_geometry_column(Castellana)
    City_Center.to_sql('city_center', engine, if_exists='replace', index=False)
    Metro.to_sql('metro', engine, if_exists='replace', index=False)
    Castellana.to_sql('castellana', engine, if_exists='replace', index=False)

    print("✅ Exportación completada con éxito.")
