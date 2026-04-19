"""Schemas Pydantic pour les requetes et reponses de recommandation.

Ces classes definissent la forme exacte des donnees
qui entrent et sortent de l'API. FastAPI s'en sert aussi
pour generer la doc Swagger automatiquement.
"""

from pydantic import BaseModel, Field


# ========================================================================
# REQUETES (ce que l'utilisateur envoie)
# ========================================================================

class RecommendationRequest(BaseModel):
    """Demande de recommandation de culture a partir d'un point GPS."""

    latitude: float = Field(
        ...,
        ge=6.0,
        le=12.5,
        description="Latitude du champ. Doit etre dans les limites du Benin (6.0 a 12.5).",
        examples=[9.35],
    )
    longitude: float = Field(
        ...,
        ge=0.7,
        le=3.9,
        description="Longitude du champ. Doit etre dans les limites du Benin (0.7 a 3.9).",
        examples=[2.63],
    )


class SowingWindowRequest(BaseModel):
    """Demande de fenetre de semis pour une culture donnee."""

    latitude: float = Field(..., ge=6.0, le=12.5, examples=[9.35])
    longitude: float = Field(..., ge=0.7, le=3.9, examples=[2.63])
    crop: str = Field(
        ...,
        description="Nom de la culture, par exemple : Mais, Sorgho, Niebe",
        examples=["Mais"],
    )


# ========================================================================
# REPONSES (ce que l'API renvoie)
# ========================================================================

class SowingWindow(BaseModel):
    """Intervalle de dates pour semer une culture."""

    start: str = Field(..., description="Date de debut, format YYYY-MM-DD ou Mois-JJ")
    end: str = Field(..., description="Date de fin")


class CropRecommendation(BaseModel):
    """Detail d'une culture recommandee."""

    rank: int = Field(..., description="Classement : 1 = la meilleure")
    crop: str = Field(..., description="Nom de la culture")
    confidence: float = Field(..., ge=0, le=1, description="Score de confiance entre 0 et 1")
    sowing_window: SowingWindow | None = Field(None, description="Fenetre de semis optimale")
    reasons: list[str] = Field(default_factory=list, description="Raisons de la recommandation")


class LocationInfo(BaseModel):
    """Informations sur la zone geographique detectee."""

    latitude: float
    longitude: float
    nearest_zone: str = Field(..., description="Zone agro-ecologique la plus proche")
    climate_type: str = Field(..., description="Type de climat (ex: Soudanien)")


class SoilSummary(BaseModel):
    """Resume simplifie des proprietes du sol."""

    soil_type: str = Field(..., description="Type de sol (ex: Argilo-sableux)")
    ph: float
    fertility: str = Field(..., description="Niveau de fertilite : Faible, Moyenne, ou Bonne")


class RecommendationResponse(BaseModel):
    """Reponse complete pour une demande de recommandation."""

    location: LocationInfo
    recommendations: list[CropRecommendation]
    soil_summary: SoilSummary
    confidence_note: str = Field(
        default="Confiance basee sur les donnees historiques 2020-2024.",
        description="Note sur la fiabilite des resultats",
    )


class SowingWindowResponse(BaseModel):
    """Reponse pour une demande de fenetre de semis."""

    location: LocationInfo
    crop: str
    sowing_window: SowingWindow
    historical_onset: str = Field(..., description="Debut moyen de la saison des pluies")
    confidence: float = Field(..., ge=0, le=1)
    advice: str = Field(..., description="Conseil pratique pour le semis")
