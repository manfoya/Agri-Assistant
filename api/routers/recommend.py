"""Router /recommend -- coeur du systeme.

Contient la logique de recommandation de cultures.
Utilise l'algorithme de Matching Agronomique pour croiser les
donnees GPS exactes (Sol + Climat) avec les exigences des plantes.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from api.core.database import get_db
from api.models.crop_requirement import CropRequirement
from api.services.soil_service import soil_service
from api.services.weather_service import weather_service
from api.services.matching_service import run_matching

from api.schemas.recommendation import (
    RecommendationRequest,
    RecommendationResponse,
    LocationInfo,
    SoilSummary,
)

router = APIRouter(prefix="/api/v1", tags=["Recommandation"])

# ========================================================================
# Fonctions utilitaires
# ========================================================================

def classify_soil_type(sand: float, clay: float) -> str:
    """Determine le type de sol a partir du sable et de l'argile."""
    if sand > 70:
        return "Sableux"
    elif clay > 40:
        return "Argileux"
    elif sand > 50 and clay > 15:
        return "Argilo-sableux"
    elif clay > 25:
        return "Argilo-limoneux"
    else:
        return "Limoneux"

def evaluate_fertility(ph: float, soc: float, nitrogen: float) -> str:
    """Evalue la fertilite du sol selon le pH, le carbone et l'azote."""
    score = 0
    if 5.5 <= ph <= 7.5:
        score += 1
    if soc > 20:
        score += 1
    if nitrogen > 1.5:
        score += 1

    if score >= 3:
        return "Bonne"
    elif score >= 2:
        return "Moyenne"
    return "Faible"


# ========================================================================
# Endpoints
# ========================================================================

@router.post("/recommend", response_model=RecommendationResponse)
def recommend_crops(
    request: RecommendationRequest,
    db: Session = Depends(get_db),
):
    """Recommande les meilleures cultures pour un point GPS precis.

    Etapes :
    1. Recuperer les donnees exactes de sol (SoilGrids).
    2. Recuperer la climatologie exacte (NASA POWER).
    3. Recuperer les exigences des plantes (DB).
    4. Executer l'algorithme de Matching.
    """
    
    # Etape 1 : Donnees de sol
    soil_data = soil_service.get_soil_data(request.latitude, request.longitude)
    if not soil_data:
        raise HTTPException(
            status_code=404,
            detail="Impossible de recuperer les donnees de sol pour cette localisation.",
        )

    # Etape 2 : Donnees climatiques
    climate_data = weather_service.get_climate_data(request.latitude, request.longitude)
    if not climate_data:
        raise HTTPException(
            status_code=503,
            detail="Service meteo indisponible pour ce point GPS.",
        )

    # Etape 3 : Exigences des cultures
    all_crops = db.query(CropRequirement).all()
    if not all_crops:
        raise HTTPException(
            status_code=500,
            detail="Base de donnees des cultures vide. Executez le script de seeding.",
        )

    # Classifier le sol pour le resume utilisateur
    soil_type = classify_soil_type(
        soil_data.get("sand", 50),
        soil_data.get("clay", 20),
    )
    fertility = evaluate_fertility(
        soil_data.get("ph", 6.0),
        soil_data.get("soc", 15),
        soil_data.get("nitrogen", 1.5),
    )

    # Etape 4 : L'algorithme fait le matching
    recommendations = run_matching(soil_data, climate_data, all_crops)

    return RecommendationResponse(
        location=LocationInfo(
            latitude=request.latitude,
            longitude=request.longitude,
            nearest_zone="Donnees exactes GPS", # Plus d'approximation
            climate_type="Local",
        ),
        recommendations=recommendations,
        soil_summary=SoilSummary(
            soil_type=soil_type,
            ph=round(soil_data.get("ph", 6.0), 1),
            fertility=fertility,
        ),
        confidence_note="Compatibilite basee sur le sol et la climatologie historique."
    )
