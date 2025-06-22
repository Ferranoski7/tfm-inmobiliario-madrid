import requests
import json
import base64
import json

from typing import Optional, Dict, Any
import os
from datetime import datetime


def generate_token(API_KEY, API_SECRET, destination = ".credentials/idealista_access_token.json") -> str:
    # Concatenate and base64 encode
    credentials = f"{API_KEY}:{API_SECRET}"
    b64_credentials = base64.b64encode(credentials.encode()).decode()
    print(f"Base64 Encoded Credentials: {b64_credentials}")
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

def load_token(credentials_path: str = os.path.abspath(".credentials/idealista_access_token.json")) -> str:
    """
    Load the access token from a credentials JSON file.
    
    Args:
        credentials_path (str): Path to the credentials JSON file.
    
    Returns:
        str: Access token.
    """
    if not os.path.exists(credentials_path):
        os.makedirs(os.path.dirname(credentials_path), exist_ok=True)
    with open(credentials_path, "r", encoding="utf-8") as cred_file:
        credentials = json.load(cred_file)
    return credentials["access_token"]

def search_by_location(token: str, location_id: str, max_items: int = 50, page: int = 1) -> Dict:
    url = "https://api.idealista.com/3.5/es/search"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "locationId": location_id,
        "operation": "sale",
        "propertyType": "homes",
        "maxItems": max_items,
        "numPage": page
    }
    resp = requests.post(url, headers=headers, data=data)
    resp.raise_for_status()
    return resp.json()

def run_queries(token: str, location_ids: list[str]) -> list[Dict]:
    seen = set()
    all_items = []
    for loc in location_ids:
        try:
            resp = search_by_location(token, loc)
            for item in resp.get("elementList", []):
                prop_id = item.get("propertyCode")
                if prop_id not in seen:
                    seen.add(prop_id)
                    all_items.append(item)
            print(f"✅ {loc}: {len(resp.get('elementList', []))} anuncios, {len(all_items)} únicos acumulados")
        except Exception as e:
            print(f"⚠️ Error en {loc}: {e}")
    return all_items

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


def normalize_floor(value):
    if isinstance(value, int):
        return value
    try:
        if value.lower() in ["bj", "entresuelo", "bajo"]:
            return 0
        elif value.lower() in ["suelo", "planta baja"]:
            return 0
        elif value.lower() in ["ático", "ático dúplex"]:
            return 10
        else:
            return int(value)
    except:
        return None

class DatabaseDataTransformer:
    from etl.idealista.text_extraction import (
    has_terrace, has_boxroom, has_wardrobe, has_doorman, has_garden,
    has_orientation, extract_construction_year, extract_max_building_floors,
    extract_dwelling_count
)

    """
    Transformador para adaptar los datos de la API de Idealista al esquema de la base de datos.
    """

    def __init__(self):
        self.db_columns_entries = {
            "ASSETID": lambda x: x.get("propertyCode"),
            "PERIOD": lambda x: datetime.now().strftime("%Y%m"),
            "PRICE": lambda x: x.get("price"),
            "UNITPRICE": lambda x: x.get("price") / x["size"] if x.get("price") and x.get("size") else None,
            "CONSTRUCTEDAREA": lambda x: x.get("size"),
            "ROOMNUMBER": lambda x: x.get("rooms"),
            "BATHNUMBER": lambda x: x.get("bathrooms"),
            "HASLIFT": lambda x: int(x.get("hasLift", False)),
            "HASAIRCONDITIONING": lambda x: int(x.get("hasAirConditioning", False)),
            "HASPARKINGSPACE": lambda x: int(x.get("parkingSpace", {}).get("hasParkingSpace", False)),
            "ISPARKINGSPACEINCLUDEDINPRICE": lambda x: int(x.get("parkingSpace", {}).get("isParkingSpaceIncludedInPrice", False)),
            "PARKINGSPACEPRICE": lambda x: x.get("parkingSpace", {}).get("price"),
            "ISDUPLEX": lambda x: int(x.get("detailedType", {}).get("subTypology", "") == "duplex"),
            "ISSTUDIO": lambda x: int(x.get("detailedType", {}).get("subTypology", "") == "studio"),
            "ISINTOPFLOOR": lambda x: int(x.get("isInTopFloor", False)), #TODO extraer de descripción
            "FLOORCLEAN": lambda x: normalize_floor(x.get("floor")), #TODO extraer de descripción
            "FLATLOCATIONID": lambda x: f"{x.get('province', '')}|{x.get('municipality', '')}|{x.get('district', '')}|{x.get('neighborhood', '')}",
            "BUILTTYPEID_1": lambda x: int(x.get("detailedType", {}).get("typology", "") == "flat"),
            "BUILTTYPEID_2": lambda x: int(x.get("detailedType", {}).get("typology", "") == "chalet"),
            "BUILTTYPEID_3": lambda x: int(x.get("detailedType", {}).get("typology", "") == "penthouse"),
            "DISTANCE_TO_CITY_CENTER": lambda x: None,  # TODO A partir de Polygons y/o POIS
            "DISTANCE_TO_METRO": lambda x: None,        # TODO A partir de Polygons y/o POIS
            "DISTANCE_TO_CASTELLANA": lambda x: None,   # TODO A partir de Polygons y/o POIS
            "LATITUDE": lambda x: x.get("latitude"),
            "LONGITUDE": lambda x: x.get("longitude"),
            "HASTERRACE": lambda x: int(x.get("hasTerrace", False) or has_terrace(x.get("description", ""))),
            "HASBOXROOM": lambda x: int(x.get("hasBoxRoom", False) or has_boxroom(x.get("description", ""))),
            "HASWARDROBE": lambda x: int(x.get("hasWardrobe", False) or has_wardrobe(x.get("description", ""))),
            "HASDOORMAN": lambda x: int(x.get("hasDoorman", False) or has_doorman(x.get("description", ""))),
            "HASGARDEN": lambda x: int(x.get("hasGarden", False) or has_garden(x.get("description", ""))),
            "HASNORTHORIENTATION": lambda x: has_orientation(x.get("description", ""), "norte"),
            "HASSOUTHORIENTATION": lambda x: has_orientation(x.get("description", ""), "sur"),
            "HASEASTORIENTATION": lambda x: has_orientation(x.get("description", ""), "este"),
            "HASWESTORIENTATION": lambda x: has_orientation(x.get("description", ""), "oeste"),
            "CADCONSTRUCTIONYEAR": lambda x: x.get("cadConstructionYear") or extract_construction_year(x.get("description", "")),
            "CADMAXBUILDINGFLOOR": lambda x: x.get("cadMaxBuildingFloor") or extract_max_building_floors(x.get("description", "")),
            "CADDWELLINGCOUNT": lambda x: x.get("cadDwellingCount") or extract_dwelling_count(x.get("description", "")),
            "HASSWIMMINGPOOL": lambda x: has_pool(x.get("description","")),

        }

    def transform(self, data) -> dict:
        return {
            column: transform_func(data)
            for column, transform_func in self.db_columns_entries.items()
        }



# Example usage
if __name__ == "__main__":
    
    token = load_token()
    results = search_properties(
        token=token,
        center="40.430,-3.702",
        propertyType="homes",
        operation="sale",
        distance="15000"
    )
    print("Datos obtenidos correctamente:")
    print(results)
    with open("resultados.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=4)
    print("Datos guardados en 'resultados.json'")

