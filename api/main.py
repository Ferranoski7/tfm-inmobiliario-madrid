from db import engine

from fastapi import FastAPI, HTTPException, Query
from typing import List, Optional
from pydantic import BaseModel
from sqlalchemy import create_engine, text
import os
import math

app = FastAPI()


# Esquema de respuesta
class Listing(BaseModel):
    ASSETID: str
    PERIOD: int
    PRICE: float
    UNITPRICE: float
    CONSTRUCTEDAREA: float
    ROOMNUMBER: Optional[int]
    BATHNUMBER: Optional[int]
    HASLIFT: Optional[bool]
    HASAIRCONDITIONING: Optional[bool]
    # ... puedes añadir todos los campos que desees

@app.get("/")
def root():
    return {"message": "Inmuebles API activa"}

@app.get("/listings", response_model=List[Listing])
def get_all_listings(limit: int = 100, offset: int = 0):
    if limit == -1:
        query = text("SELECT * FROM madrid_sale OFFSET :offset")
        params = {"offset": offset}
    else:
        query = text("SELECT * FROM madrid_sale LIMIT :limit OFFSET :offset")
        params = {"limit": limit, "offset": offset}
    with engine.connect() as conn:
        result = conn.execute(query, params)
        return [row for row in result]

@app.get("/listings/nearby", response_model=List[Listing])
def get_listings_nearby(lat: float, lon: float, radius: float):
    # Haversine en km usando subconsulta para alias 'distance'
    haversine_sql = """
    SELECT * FROM (
        SELECT *, (
            6371 * acos(
                cos(radians(:lat)) * cos(radians(latitude)) *
                cos(radians(longitude) - radians(:lon)) +
                sin(radians(:lat)) * sin(radians(latitude))
            )
        ) AS distance
        FROM madrid_sale
        WHERE latitude IS NOT NULL AND longitude IS NOT NULL
    ) AS subquery
    WHERE distance <= :radius
    ORDER BY distance ASC
    LIMIT 100;
    """
    with engine.connect() as conn:
        result = conn.execute(text(haversine_sql), {"lat": lat, "lon": lon, "radius": radius})
        return [row for row in result]

@app.get("/listings/{asset_id}", response_model=Listing)
def get_listing_by_id(asset_id: str):
    query = text('SELECT * FROM madrid_sale WHERE "ASSETID" = :id')
    with engine.connect() as conn:
        result = conn.execute(query, {"id": asset_id}).fetchone()
        if result is None:
            raise HTTPException(status_code=404, detail="Listing not found")
        return result
