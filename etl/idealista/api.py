import requests
import json
import base64
import json

from typing import Optional, Dict, Any

def generate_token(API_KEY, API_SECRET, destination = ".credentials/idealista_access_token.json") -> str:
    # Concatenate and base64 encode
    credentials = f"{API_KEY}:{API_SECRET}"
    b64_credentials = base64.b64encode(credentials.encode()).decode()

    headers = {
        "Authorization": f"Basic {b64_credentials}",
        "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8"
    }

    data = {
        "grant_type": "client_credentials",
        "scope": "read"  # or "write" if needed
    }

    url = "https://api.idealista.com/oauth/token"

    response = requests.post(url, headers=headers, data=data, verify=True)

    if response.status_code == 200:
        token_data = response.json()
        # Store token in credentials.json
        with open(destination, "w") as f:
            json.dump(token_data, f, indent=4)
        return token_data["access_token"]
    else:
        print("Error:", response.status_code, response.text)
        return response.text

def load_token(credentials_path: str = ".credentials/idealista_access_token.json") -> str:
    """
    Load the access token from a credentials JSON file.
    
    Args:
        credentials_path (str): Path to the credentials JSON file.
    
    Returns:
        str: Access token.
    """
    with open(credentials_path, "r", encoding="utf-8") as cred_file:
        credentials = json.load(cred_file)
    return credentials["access_token"]

def search_properties(
    token: str,
    center: str,
    propertyType: str,
    operation: str,
    distance: Optional[str] = None,
    maxItems: Optional[int] = None,
    numPage: Optional[int] = None,
    locale: Optional[str] = None,
    country: str = "es",
    **kwargs
) -> Dict[str, Any]:
    """
    Search for properties using the Idealista API.

    Args:
        token (str): Bearer access token.
        center (str): Center coordinates as "longitude, latitude".
        propertyType (str): Type of property (e.g., "homes", "offices").
        operation (str): Operation type ("sale" or "rent").
        distance (str, optional): Search radius in meters.
        maxItems (int, optional): Maximum number of items per page.
        numPage (int, optional): Page number.
        locale (str, optional): Language code (e.g., "es", "en").
        country (str, optional): Country code (default "es").
        **kwargs: Additional parameters supported by the API.

    Returns:
        dict: API response as a dictionary.

    Raises:
        requests.HTTPError: If the request fails.
    """
    url = f"https://api.idealista.com/3.5/{country}/search"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data: dict[str, Any] = {
        "center": center,
        "propertyType": propertyType,
        "operation": operation
    }
    if distance:
        data["distance"] = distance
    if maxItems:
        data["maxItems"] = maxItems
    if numPage:
        data["numPage"] = numPage
    if locale:
        data["locale"] = locale
    data.update(kwargs)
    response = requests.post(url, headers=headers, data=data)
    if response.status_code == 200:
        return response.json()
    else:
        raise requests.HTTPError(f"Error {response.status_code}: {response.text}")

class DatabaseDataTransformer:
    """
    Class to handle data transformation for Idealista API responses.
    This class can be extended to include methods for transforming the data
    into a format suitable for database insertion or further processing.
    """

    def __init__(self):
        self.db_columns_entries = {
            "AMENITYID":
            "ASSETID":
            "BATHNUMBER":
            "BUILTTYPEID_1":
            "BUILTTYPEID_2":
            "BUILTTYPEID_3":
            "CADASTRALQUALITYID":
            "CADCONSTRUCTIONYEAR":
            "CADDWELLINGCOUNT":
            "CADMAXBUILDINGFLOOR":
            "CONSTRUCTEDAREA":
            "CONSTRUCTIONYEAR":
            "DISTANCE_TO_CASTELLANA":
            "DISTANCE_TO_CITY_CENTER":
            "DISTANCE_TO_METRO":
            "FLATLOCATIONID":
            "FLOORCLEAN":
            "HASAIRCONDITIONING":
            "HASBOXROOM":
            "HASDOORMAN":
            "HASEASTORIENTATION":
            "HASGARDEN":
            "HASLIFT":
            "HASNORTHORIENTATION":
            "HASPARKINGSPACE":
            "HASSOUTHORIENTATION":
            "HASSWIMMINGPOOL":
            "HASTERRACE":# 1 if haas terrace, 0 otherwise
            "HASWARDROBE": # 1 if has wardrobe, 0 otherwise
            "HASWESTORIENTATION":# 1 if has west orientation, 0 otherwise
            "ISDUPLEX": # 1 if is duplex, 0 otherwise
            "ISINTOPFLOOR":# 1 if is top floor, 0 otherwise
            "ISPARKINGSPACEINCLUDEDINPRICE": # 1 if parking space is included in price, 0 otherwise
            "ISSTUDIO":# 1 if is studio, 0 otherwise
            "latitude":
            "LATITUDE":
            "longitude":
            "LONGITUDE":
            "PARKINGSPACEPRICE":
            "PERIOD":
            "PRICE":
            "ROOMNUMBER":
            "UNITPRICE":
        } 


    def transform(self, data) -> Dict[str, Any]:
        """
        Transform the data into a desired format.
        
        Returns:
            dict: Transformed data.
        """
        # Implement transformation logic here
        return data  # Placeholder for actual transformation logic


# Example usage
if __name__ == "__main__":
    token = load_token()
    try:
        results = search_properties(
            token=token,
            center="40.123,-3.242",
            propertyType="homes",
            operation="sale",
            distance="15000"
        )
        print("Datos obtenidos correctamente:")
        print(results)
        with open("resultados.json", "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=4)
        print("Datos guardados en 'resultados.json'")
    except Exception as e:
        print(f"Error en la solicitud: {e}")
