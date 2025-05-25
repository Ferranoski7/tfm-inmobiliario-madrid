import os
import rdata
import urllib.request

file_names = ["Barcelona_POIS.rda", "Barcelona_Polygons.rda", "Barcelona_Sale.rda", "Madrid_POIS.rda",
              "Madrid_Polygons.rda",  "Madrid_Sale.rda", "Valencia_POIS.rda", "Valencia_Polygons.rda",
              "Valencia_Sale.rda", "properties_by_district.rda"]


def download_rdata(output_folder="data"):
    """
    Function that downloads the .rda files from Idealista repository.
    For each file, it is verified beforehand if the file is already in the /data folder in order to
    avoid unnecessary downloads
    """
    for rda_file in file_names:
        file_path = os.path.join(output_folder, rda_file)
        if not os.path.isfile(file_path):
            urllib.request.urlretrieve("https://github.com/paezha/idealista18/raw/master/data/" + rda_file, file_path)
        else:
            continue


def read_data(output_folder="data")-> dict:
    """
    For each file located in output_folder, extract the information as a dataframe or a dictionary containing data
    During the execution of this function UserWarning related with rdata package may appear but can be ignored
    """
    results = {}
    for file_name in os.listdir(output_folder):
        if file_name.endswith(".rda"):
            file_path = os.path.join(output_folder, file_name)
            results[file_name.replace(".rda", "")] = rdata.read_rda(file_path, default_encoding="utf8")
    return results



if __name__ == '__main__':
    madrid_pois = rdata.read_rda("data/Madrid_POIS.rda")
    madrid_polygons = rdata.read_rda("data/Madrid_Polygons.rda", default_encoding="utf8")
    madrid_sale = rdata.read_rda("data/Madrid_Sale.rda")

    print("Madrid_POIS")
    print(madrid_pois['Madrid_POIS'].keys())
    madrid_city_center = madrid_pois["Madrid_POIS"]["City_Center"]
    madrid_metro = madrid_pois["Madrid_POIS"]["Metro"]
    madrid_castellana = madrid_pois["Madrid_POIS"]["Castellana"]
    print(madrid_city_center)
    print(madrid_metro.iloc[0])
    print(madrid_castellana)
    print("\n")

    print("Madrid_Polygons")
    print(madrid_polygons['Madrid_Polygons'].iloc[0])
    print("\n")

    print("Madrid_Sale")
    print(madrid_sale['Madrid_Sale'].iloc[0])
    print("\n")
