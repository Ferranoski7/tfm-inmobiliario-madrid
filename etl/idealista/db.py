import os
import rdata
import urllib.request



class IdealistaDB:
    """
    Class to handle the Idealista database operations.
    It includes methods to download the data files and read them into a dictionary.
    """
    AVALIL_CITIES = ["Barcelona", "Madrid", "Valencia"]
    FILE_TYPES = ["POIS", "Polygons", "Sale"]

    def __init__(self, output_folder="data"):
        self.output_folder = output_folder
        self.FILE_NAMES = [
            f"{city}_{file_type}.rda" for city in self.AVALIL_CITIES for file_type in self.FILE_TYPES
        ]
        if not os.path.exists(self.output_folder):
            os.mkdir(self.output_folder, exist_ok=True)
        print("Downloading Idealista data files...")
        # Download the .rda files if they do not exist in the output folder
        self.download_rdata()
        self.results = {}

    def download_rdata(self):
        """
        Downloads the .rda files from the Idealista repository if they do not already exist in the output folder.
        """
        for rda_file in self.FILE_NAMES:
            file_path = os.path.join(self.output_folder, rda_file)
            if not os.path.isfile(file_path):
                urllib.request.urlretrieve("https://github.com/paezha/idealista18/raw/master/data/" + rda_file, file_path)
            else:
                continue

    def read_data(self, city=None) -> dict:
        """
        Reads the data files from the output folder and returns a dictionary containing the data.
        """
        results = {}

        if city is None:
            file_names = self.FILE_NAMES
        else:
            file_names = [f"{city}_{file_type}.rda" for file_type in self.FILE_TYPES if f"{city}_{file_type}.rda" in self.FILE_NAMES]
        for file in os.listdir(self.output_folder):
            if file in file_names and file.endswith(".rda"):
                file_path = os.path.join(self.output_folder, file)
                results[file.replace(".rda", "")] = rdata.read_rda(file_path, default_encoding="utf8")[file.replace(".rda", "")]
        self.results = results
        return results
    
    def data_structure(self,data = None, root = True, depth = 0):
        """
        Function to print the structure of the data dictionary.
        """
        if data is None:
            data = self.results
        if data is None:
            print("No data available.")
            return
        if isinstance(data, dict):
            if root:
                print("Data Structure:")
            for key, value in data.items():
                print("  " * (depth) + f"{key}:")
                self.data_structure(value, root=False, depth=depth + 1)
        else:
            print("  " * (depth) + f"{type(data).__name__} with {len(data)} entries" if hasattr(data, '__len__') else f"{type(data).__name__}")






if __name__ == '__main__':
    db = IdealistaDB(output_folder="data")
    db.read_data(city="Madrid")
    db.data_structure()
    
    for name, dataframe in  db.results["Madrid_POIS"].items():
        print(f"DataFrame Name: {name}, shape: {dataframe.shape}")
        print(dataframe.head())
        
    print("\nDataFrames in the IdealistaDB:")
    print("Madrid_Polygons:")
    print(db.results["Madrid_Polygons"].keys())
    print(db.results["Madrid_Polygons"].head())
    print("Madrid_Sale:")
    print(db.results["Madrid_Sale"].keys())
    print(db.results["Madrid_Sale"].head())
