import requests, re, time, json
from bs4 import BeautifulSoup
from etl.idealista.api import load_token
import random
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}


BASE_URL = "https://www.idealista.com/venta-viviendas/madrid/{}/"
def get_location_ids(district_slug: str) -> list[str]:
    url = BASE_URL.format(district_slug)
    HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Connection": "keep-alive",
    "DNT": "1",
    "Upgrade-Insecure-Requests": "1",
}

    response = requests.get(url, headers=HEADERS, timeout=10)
    if response.status_code != 200:
        raise Exception(f"❌ Error al acceder a {url} → Codigo {response.status_code}")
    soup = BeautifulSoup(response.text, "html.parser")
    matches = set(re.findall(r'locationId=(0-EU-ES-28-[0-9\-]+)"', response.text))
    if not matches:
        matches = set(re.findall(r'"locationId"\s*:\s*"?(0-EU-ES-28-[0-9\-]+)"?', response.text))
    return list(matches)


def validate_location_id(token: str, location_id: str) -> bool:
    # Llamada minima para comprobar que existe
    url = "https://api.idealista.com/3.5/es/search"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/x-www-form-urlencoded"}
    data = {"locationId": location_id, "operation": "sale", "propertyType": "homes", "maxItems": 1}
    resp = requests.post(url, headers=headers, data=data)
    return resp.status_code == 200 and resp.json().get("elementList")


def main():
    token = load_token()  # Usa tu funcion existente
    district_slugs = {
        "arganzuela":[
            "palos-de-la-frontera",
            "imperial",
            "acacias",
            "delicias",
            "chopera",
            "legazpi",
        ],
        "barajas":[
            "alameda-de-osuna",
            "timon",
            "casco-historico-de-barajas",
            "campo-de-las-naciones-corralejos",
            "aeropuerto",
        ],
        "barrio-de-salamanca": [
            "guindalera",
            "goya",
            "lista",
            "fuente-del-berro",
            "recoletos",
            "castellana",
        ],
        "carabanchel":[
            "puerta-bonita",
            "san-isidro",
            "vista-alegre",
            "buena-vista",
            "opanel",
            "abrantes",
            "comillas",
            "pau-de-carabanchel",
        ],
        "centro": [
            "malasana-justicia",
            "lavapies-embajadores",
            "chueca-justicia",
            "palacio",
            "huertas-cortes"
            "sol",
        ],
        "chamartin":[
            "el-viso",
            "bernabeu-hispanoamerica",
            "nueva-españa",
            "prosperidad",
            "castilla",
            "ciudad-jardin",
        ],
        "chamberi":[
            "nuevos-ministerios-rios-rosas",
            "vallehermoso",
            "gaztambide",
            "arapiles",
            "trafalgar",
            "almagro",
        ],
        "ciudad-lineal":[
            "pueblo-nuevo",
            "ventas",
            "concepcion",
            "quintana",
            "costillares",
            "colina",
            "san-juan-bautista",
            "san-pascual",
            "atalaya",
        ],
        "fuencarral":[
            "penagrande",
            "las-tablas",
            "tres-olivos",
            "pilar",
            "montecarmelo",
            "mirasierra",
            "fuentelarreina",
            "arroyo-de-fresno",
            "el-pardo",
        ],
        "hortaleza":[
            "conde-de-orgaz-piovera",
            "pinar-del-rey",
            "sanchinarro",
            "canillas",
            "valdebebas-valdefuentes",
            "palomas",
            "virgen-del-cortijo-manoteras",
            "apostol-santiago",
        ],
        "latina":[
            "puerta-del-angel",
            "aluche",
            "lucero",
            "aguilas"
            "los-carmenes",
            "campamento",
            "cuatro-vientos",
        ],
        "moncloa":[
            "arguelles",
            "aravaca",
            "valdemarin",
            "ciudad-universitaria",
            "el-plantio",
            "valdezarza",
            "casa-de-campo",
        ],
        "moratalaz":[
            "fontarron",
            "vinateros",
            "media-legua",
            "marroquina",
            "horcajo",
            "pavones",
        ],
        "puente-de-vallecas":[
            "san-diego",
            "numancia",
            "entrevias",
            "palomeras-bajas",
            "palomeras-sureste",
            "portazgo"
        ],
        "retiro":[
            "ibiza",
            "jeronimos",
            "nino-jesus",
            "pacifico",
            "adelfas",
            "estrella",
        ],
        "san-blas":[
            "simancas",
            "canillejas",
            "rejas",
            "arcos",
            "amposta",
            "salvador",
            "rosas",
            "hellin"
        ],
        "tetuan":[
            "cuatro-caminos",
            "valdeacederas",
            "berruguete",
            "bellas-vistas",
            "cuzco-castillejos",
            "ventilla-almenara"
        ],
        "usera":[
            "moscardo",
            "12-de-octubre-orcasur",
            "pradolongo",
            "almendrales",
            "san-fermin",
            "orcasitas",
            "zofio"
        ],
        "vicalvaro":[
            "los-berrocales",
            "el-canaveral",
            "ambroz",
            "los-cerros",
            "casco-historico-de-vicalvaro",
            "los-ahijones",
            "valdebernardo-valderrivas",
        ],
        "villa-de-vallecas":[
            "casco-historico-de-vallecas",
            "ensanche-de-vallecas-la-gavia",
            "santa-eugenia",
            "valdecarros"
        ],
        "villaverde":[
            "villaverde-alto",
            "los-rosales",
            "san-cristobal",
            "butarque",
            "los-angeles"
        ],
    }

    valid_ids = []
    for distrito in district_slugs:
        for barrio in district_slugs[distrito]:
            slug = f"{distrito}/{barrio}"
            print(f"🔍 Buscando locationIds en el barrio: {slug}")
            try:
                ids = get_location_ids(slug)
                print(ids)
                for lid in ids:
                    if lid not in valid_ids:
                        valid_ids.append(lid)
                        print("✅ Valido:", lid)
                        if len(valid_ids) >= 100:
                            break
                    else:
                        print("❌ No valido:", lid)
                if len(valid_ids) >= 100:
                    break
            except Exception as e:
                print("⚠️ Error en", slug, e)
            time.sleep(random.uniform(1, 3))
        


    print(f"\n📊 Encontrados {len(valid_ids)} locationId validos:")
    print(json.dumps(valid_ids, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
    # [
    # "0-EU-ES-28-07-001-079-01",
    # "0-EU-ES-28-07-001-079-09-007",
    # "0-EU-ES-28-07-001-079-05",
    # "0-EU-ES-28-07-001-079-06",
    # "0-EU-ES-28-07-001-079-07",
    # "0-EU-ES-28-07-001-079-02",
    # "0-EU-ES-28-07-001-079-03",
    # "0-EU-ES-28-07-001-079-10",
    # "0-EU-ES-28-07-001-079-11",
    # "0-EU-ES-28-07-001-079-12",
    # "0-EU-ES-28-07-001-079-14",
    # "0-EU-ES-28-07-001-079-13",
    # "0-EU-ES-28-07-001-079-18",
    # "0-EU-ES-28-07-001-079-16",
    # "0-EU-ES-28-07-001-079-19",
    # "0-EU-ES-28-07-001-079-17"
    # ]