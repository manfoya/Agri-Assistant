"""Schemas Pydantic pour les donnees brutes : sol, meteo, cultures, zones.

Utilises par les endpoints de consultation directe des donnees.
"""

from pydantic import BaseModel, Field


class SoilDataResponse(BaseModel):
    """Donnees de sol renvoyees par l'API pour un point GPS."""

    latitude: float
    longitude: float
    sand_pct: float | None = Field(None, description="Sable, en pourcent")
    clay_pct: float | None = Field(None, description="Argile, en pourcent")
    ph: float | None = Field(None, description="pH du sol")
    soc_g_kg: float | None = Field(None, description="Carbone organique, g/kg")
    nitrogen_g_kg: float | None = Field(None, description="Azote, g/kg")
    cec_cmol_kg: float | None = Field(None, description="CEC, cmol/kg")
    bulk_density_kg_m3: float | None = Field(None, description="Densite apparente, kg/m3")


class WeatherSummary(BaseModel):
    """Resume climatique pour un point GPS, calcule sur plusieurs annees."""

    latitude: float
    longitude: float
    period: str = Field(..., description="Periode couverte, par ex. 2020-2024")
    avg_temp_c: float = Field(..., description="Temperature moyenne, degres C")
    min_temp_c: float = Field(..., description="Temperature minimale absolue, degres C")
    max_temp_c: float = Field(..., description="Temperature maximale absolue, degres C")
    avg_precipitation_mm: float = Field(..., description="Precipitations moyennes par jour, mm")
    total_annual_precipitation_mm: float = Field(..., description="Precipitations annuelles moyennes, mm")
    avg_humidity_pct: float = Field(..., description="Humidite relative moyenne, pourcent")
    avg_solar_radiation: float = Field(..., description="Rayonnement solaire moyen, MJ/m2/jour")
    rainy_days_per_year: int = Field(..., description="Jours de pluie par an (>=1mm)")


class CropInfo(BaseModel):
    """Fiche descriptive d'une culture supportee par le systeme."""

    name: str
    scientific_name: str
    category: str = Field(..., description="Categorie : Cereale, Legumineuse, Tubercule, etc.")
    water_needs_mm: str = Field(..., description="Besoins en eau, par ex. 500-800mm")
    optimal_temp_c: str = Field(..., description="Temperature optimale, par ex. 25-30 degres C")
    cycle_days: str = Field(..., description="Duree du cycle, par ex. 90-120 jours")


class ZoneInfo(BaseModel):
    """Zone agro-ecologique du Benin."""

    name: str
    latitude: float
    longitude: float
    climate_type: str
    annual_rainfall_mm: str
    main_crops: list[str]


class HealthResponse(BaseModel):
    """Reponse du endpoint /health pour verifier l'etat du systeme."""

    status: str = "ok"
    version: str
    database: str = Field(..., description="Etat de la connexion BDD")
    weather_records: int = Field(..., description="Nombre d'enregistrements meteo")
    soil_records: int = Field(..., description="Nombre d'enregistrements sol")
    ml_model_loaded: bool = Field(..., description="Le modele ML est-il charge en memoire ?")
