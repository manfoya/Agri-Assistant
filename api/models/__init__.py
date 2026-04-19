"""Modeles SQLAlchemy -- representent les tables de la base de donnees."""

from api.models.soil import SoilData
from api.models.weather import WeatherData
from api.models.recommendation import RecommendationLog
from api.models.crop_requirement import CropRequirement

__all__ = ["SoilData", "WeatherData", "RecommendationLog", "CropRequirement"]
