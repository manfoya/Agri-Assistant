"""Router pour la consultation des donnees brutes.

Permet d'acceder aux donnees de sol, au resume meteo,
au catalogue de cultures, et aux zones agro-ecologiques du Benin.
"""

from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session
from sqlalchemy import text

from api.core.database import get_db
from api.services.soil_service import soil_service
from api.schemas.weather import SoilDataResponse, WeatherSummary, CropInfo, ZoneInfo

router = APIRouter(prefix="/api/v1", tags=["Donnees"])


# ========================================================================
# Catalogue des cultures supportees
# ========================================================================

SUPPORTED_CROPS = [
    CropInfo(
        name="Mais", scientific_name="Zea mays", category="Cereale",
        water_needs_mm="500-800mm", optimal_temp_c="25-30", cycle_days="90-120",
    ),
    CropInfo(
        name="Sorgho", scientific_name="Sorghum bicolor", category="Cereale",
        water_needs_mm="400-600mm", optimal_temp_c="25-35", cycle_days="100-140",
    ),
    CropInfo(
        name="Mil", scientific_name="Pennisetum glaucum", category="Cereale",
        water_needs_mm="300-500mm", optimal_temp_c="28-35", cycle_days="75-100",
    ),
    CropInfo(
        name="Riz", scientific_name="Oryza sativa", category="Cereale",
        water_needs_mm="900-1200mm", optimal_temp_c="22-30", cycle_days="120-150",
    ),
    CropInfo(
        name="Manioc", scientific_name="Manihot esculenta", category="Tubercule",
        water_needs_mm="500-1000mm", optimal_temp_c="25-29", cycle_days="240-365",
    ),
    CropInfo(
        name="Igname", scientific_name="Dioscorea spp.", category="Tubercule",
        water_needs_mm="1000-1500mm", optimal_temp_c="25-30", cycle_days="240-300",
    ),
    CropInfo(
        name="Niebe", scientific_name="Vigna unguiculata", category="Legumineuse",
        water_needs_mm="300-500mm", optimal_temp_c="25-35", cycle_days="60-90",
    ),
    CropInfo(
        name="Arachide", scientific_name="Arachis hypogaea", category="Legumineuse",
        water_needs_mm="500-700mm", optimal_temp_c="25-30", cycle_days="90-130",
    ),
    CropInfo(
        name="Coton", scientific_name="Gossypium hirsutum", category="Culture de rente",
        water_needs_mm="700-1300mm", optimal_temp_c="25-35", cycle_days="150-180",
    ),
    CropInfo(
        name="Soja", scientific_name="Glycine max", category="Legumineuse",
        water_needs_mm="450-900mm", optimal_temp_c="20-30", cycle_days="100-130",
    ),
]


# ========================================================================
# Zones agro-ecologiques du Benin
# ========================================================================

BENIN_ZONES_INFO = [
    ZoneInfo(
        name="Cotonou (Sud cotier)", latitude=6.37, longitude=2.43,
        climate_type="Subequatorial", annual_rainfall_mm="1200-1500",
        main_crops=["Mais", "Manioc", "Niebe", "Tomate"],
    ),
    ZoneInfo(
        name="Abomey-Calavi (Sud)", latitude=7.15, longitude=2.05,
        climate_type="Subequatorial", annual_rainfall_mm="1100-1400",
        main_crops=["Mais", "Manioc", "Niebe", "Arachide"],
    ),
    ZoneInfo(
        name="Save (Centre)", latitude=8.03, longitude=2.49,
        climate_type="Soudano-guineen", annual_rainfall_mm="1000-1200",
        main_crops=["Igname", "Mais", "Sorgho", "Coton"],
    ),
    ZoneInfo(
        name="Parakou (Centre-Nord)", latitude=9.35, longitude=2.63,
        climate_type="Soudanien", annual_rainfall_mm="1000-1300",
        main_crops=["Sorgho", "Mais", "Coton", "Arachide"],
    ),
    ZoneInfo(
        name="Natitingou (Nord-Ouest)", latitude=10.31, longitude=1.38,
        climate_type="Soudanien", annual_rainfall_mm="1100-1400",
        main_crops=["Sorgho", "Mil", "Igname", "Riz"],
    ),
    ZoneInfo(
        name="Kandi (Extreme Nord)", latitude=11.13, longitude=2.94,
        climate_type="Soudano-sahelien", annual_rainfall_mm="800-1000",
        main_crops=["Mil", "Sorgho", "Niebe", "Coton"],
    ),
    ZoneInfo(
        name="Djougou (Centre-Ouest)", latitude=9.70, longitude=1.67,
        climate_type="Soudanien", annual_rainfall_mm="1100-1300",
        main_crops=["Igname", "Sorgho", "Mais", "Riz"],
    ),
    ZoneInfo(
        name="Nikki (Est)", latitude=9.94, longitude=3.21,
        climate_type="Soudanien", annual_rainfall_mm="1000-1200",
        main_crops=["Coton", "Sorgho", "Mais", "Arachide"],
    ),
]


# ========================================================================
# Endpoints
# ========================================================================

@router.get("/crops", response_model=list[CropInfo])
def list_crops():
    """Renvoie la liste des cultures supportees avec leurs caracteristiques."""
    return SUPPORTED_CROPS


@router.get("/zones", response_model=list[ZoneInfo])
def list_zones():
    """Renvoie les zones agro-ecologiques du Benin."""
    return BENIN_ZONES_INFO


@router.get("/soil/{lat}/{lon}", response_model=SoilDataResponse)
def get_soil_data(
    lat: float = Path(..., ge=6.0, le=12.5, description="Latitude"),
    lon: float = Path(..., ge=0.7, le=3.9, description="Longitude"),
):
    """Recupere les proprietes du sol depuis l'API SoilGrids."""
    data = soil_service.get_soil_data(lat, lon)
    if not data:
        raise HTTPException(
            status_code=404,
            detail="Donnees de sol non disponibles pour cette localisation.",
        )

    return SoilDataResponse(
        latitude=lat,
        longitude=lon,
        sand_pct=data.get("sand"),
        clay_pct=data.get("clay"),
        ph=data.get("ph"),
        soc_g_kg=data.get("soc"),
        nitrogen_g_kg=data.get("nitrogen"),
        cec_cmol_kg=data.get("cec"),
        bulk_density_kg_m3=data.get("bdod"),
    )


@router.get("/weather/{lat}/{lon}", response_model=WeatherSummary)
def get_weather_summary(
    lat: float = Path(..., ge=6.0, le=12.5, description="Latitude"),
    lon: float = Path(..., ge=0.7, le=3.9, description="Longitude"),
    db: Session = Depends(get_db),
):
    """Calcule un resume climatique a partir des donnees historiques en BDD.

    Cherche la localite la plus proche dans la base de donnees
    et renvoie les moyennes sur toute la periode disponible.
    """
    row = db.execute(text("""
        SELECT
            latitude, longitude,
            ROUND(AVG(temp_mean_c), 1)   AS avg_temp,
            ROUND(MIN(temp_min_c), 1)    AS min_temp,
            ROUND(MAX(temp_max_c), 1)    AS max_temp,
            ROUND(AVG(precipitation_mm), 2) AS avg_precip,
            ROUND(AVG(precipitation_mm) * 365, 0) AS annual_precip,
            ROUND(AVG(humidity_pct), 1)  AS avg_humidity,
            ROUND(AVG(solar_radiation), 2) AS avg_solar,
            COUNT(CASE WHEN precipitation_mm >= 1.0 THEN 1 END) AS rainy_days_total,
            MIN(date) AS min_date,
            MAX(date) AS max_date,
            COUNT(DISTINCT substr(date, 1, 4)) AS num_years
        FROM weather_data
        GROUP BY latitude, longitude
        ORDER BY (
            (latitude - :lat) * (latitude - :lat)
            + (longitude - :lon) * (longitude - :lon)
        )
        LIMIT 1
    """), {"lat": lat, "lon": lon}).fetchone()

    if not row:
        raise HTTPException(status_code=404, detail="Aucune donnee meteo en base.")

    num_years = row[12] if row[12] > 0 else 1

    return WeatherSummary(
        latitude=row[0],
        longitude=row[1],
        period=f"{row[10][:4]}-{row[11][:4]}",
        avg_temp_c=row[2],
        min_temp_c=row[3],
        max_temp_c=row[4],
        avg_precipitation_mm=row[5],
        total_annual_precipitation_mm=row[6],
        avg_humidity_pct=row[7],
        avg_solar_radiation=row[8],
        rainy_days_per_year=int(row[9] / num_years),
    )
