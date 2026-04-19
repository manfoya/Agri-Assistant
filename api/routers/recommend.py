"""Router /recommend et /sowing-window -- coeur du systeme.

Contient la logique de recommandation de cultures
et de prediction de fenetre de semis.

Pour l'instant, les predictions utilisent des regles agronomiques simples.
Le vrai modele ML sera branche en Phase 3.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from api.core.database import get_db
from api.services.soil_service import soil_service
from api.schemas.recommendation import (
    RecommendationRequest,
    RecommendationResponse,
    SowingWindowRequest,
    SowingWindowResponse,
    CropRecommendation,
    LocationInfo,
    SoilSummary,
    SowingWindow,
)

router = APIRouter(prefix="/api/v1", tags=["Recommandation"])


# ========================================================================
# Donnees de reference : zones agro-ecologiques du Benin
# ========================================================================

BENIN_ZONES = [
    {"name": "Cotonou (Sud cotier)", "lat": 6.37, "lon": 2.43, "climate": "Subequatorial", "rainfall": "1200-1500mm"},
    {"name": "Abomey-Calavi (Sud)", "lat": 7.15, "lon": 2.05, "climate": "Subequatorial", "rainfall": "1100-1400mm"},
    {"name": "Save (Centre)", "lat": 8.03, "lon": 2.49, "climate": "Soudano-guineen", "rainfall": "1000-1200mm"},
    {"name": "Parakou (Centre-Nord)", "lat": 9.35, "lon": 2.63, "climate": "Soudanien", "rainfall": "1000-1300mm"},
    {"name": "Natitingou (Nord-Ouest)", "lat": 10.31, "lon": 1.38, "climate": "Soudanien", "rainfall": "1100-1400mm"},
    {"name": "Kandi (Extreme Nord)", "lat": 11.13, "lon": 2.94, "climate": "Soudano-sahelien", "rainfall": "800-1000mm"},
    {"name": "Djougou (Centre-Ouest)", "lat": 9.70, "lon": 1.67, "climate": "Soudanien", "rainfall": "1100-1300mm"},
    {"name": "Nikki (Est)", "lat": 9.94, "lon": 3.21, "climate": "Soudanien", "rainfall": "1000-1200mm"},
]


# ========================================================================
# Fonctions utilitaires
# ========================================================================

def find_nearest_zone(lat: float, lon: float) -> dict:
    """Trouve la zone agro-ecologique la plus proche du point GPS donne.

    On utilise la distance euclidienne simple (suffisant pour le Benin
    car le pays est petit et les distorsions de projection sont faibles).
    """
    best_zone = BENIN_ZONES[0]
    best_distance = float("inf")

    for zone in BENIN_ZONES:
        distance = (zone["lat"] - lat) ** 2 + (zone["lon"] - lon) ** 2
        if distance < best_distance:
            best_distance = distance
            best_zone = zone

    return best_zone


def classify_soil_type(sand: float, clay: float) -> str:
    """Determine le type de sol a partir du sable et de l'argile.

    Classification simplifiee basee sur le triangle textural.
    """
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
    """Evalue la fertilite du sol selon le pH, le carbone et l'azote.

    Chaque critere dans la bonne plage ajoute 1 point.
    3 points = Bonne, 2 = Moyenne, sinon Faible.
    """
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
# Recommandation par regles (placeholder pour le modele ML)
# ========================================================================

def rule_based_recommendation(
    zone: dict,
    soil_data: dict,
    soil_type: str,
) -> list[CropRecommendation]:
    """Genere des recommandations basees sur des regles agronomiques.

    C'est un placeholder. En Phase 3, cette fonction sera
    remplacee par un appel au modele ML entraine.
    Les regles ici sont basees sur la litterature agronomique du Benin.
    """
    climate = zone["climate"]

    # Regles pour le sud (deux saisons de pluie)
    if climate == "Subequatorial":
        return [
            CropRecommendation(
                rank=1, crop="Mais", confidence=0.85,
                sowing_window=SowingWindow(start="Mars-15", end="Avril-15"),
                reasons=[
                    "Climat humide favorable",
                    f"Sol {soil_type} adapte",
                    "Deux saisons de culture possibles",
                ],
            ),
            CropRecommendation(
                rank=2, crop="Manioc", confidence=0.80,
                sowing_window=SowingWindow(start="Mars-01", end="Avril-30"),
                reasons=[
                    "Culture principale du Sud-Benin",
                    "Tolere les sols pauvres",
                    "Cycle long adapte au climat",
                ],
            ),
            CropRecommendation(
                rank=3, crop="Niebe", confidence=0.72,
                sowing_window=SowingWindow(start="Juillet-15", end="Aout-15"),
                reasons=[
                    "Fixe l'azote dans le sol",
                    "Bonne rotation avec le mais",
                    "Adapte a la deuxieme saison",
                ],
            ),
        ]

    # Regles pour le centre et le nord (une saison de pluie)
    if climate in ("Soudanien", "Soudano-guineen"):
        return [
            CropRecommendation(
                rank=1, crop="Sorgho", confidence=0.82,
                sowing_window=SowingWindow(start="Juin-01", end="Juin-30"),
                reasons=[
                    "Resistant a la secheresse",
                    "Adapte au climat soudanien",
                    f"Sol {soil_type} convenable",
                ],
            ),
            CropRecommendation(
                rank=2, crop="Mais", confidence=0.78,
                sowing_window=SowingWindow(start="Mai-15", end="Juin-15"),
                reasons=[
                    "Bon rendement dans la zone",
                    "Temperature optimale",
                    "Pluviometrie suffisante",
                ],
            ),
            CropRecommendation(
                rank=3, crop="Arachide", confidence=0.70,
                sowing_window=SowingWindow(start="Juin-15", end="Juillet-15"),
                reasons=[
                    "Sols legers favorables",
                    "Bonne valeur marchande",
                    "Enrichit le sol en azote",
                ],
            ),
        ]

    # Regles pour l'extreme nord (secheresse plus marquee)
    return [
        CropRecommendation(
            rank=1, crop="Mil", confidence=0.88,
            sowing_window=SowingWindow(start="Juin-15", end="Juillet-15"),
            reasons=[
                "Tres resistant a la secheresse",
                "Culture traditionnelle du Nord",
                "Faibles besoins en eau",
            ],
        ),
        CropRecommendation(
            rank=2, crop="Sorgho", confidence=0.83,
            sowing_window=SowingWindow(start="Juin-01", end="Juin-30"),
            reasons=[
                "Adapte aux conditions arides",
                "Cycle court disponible",
                f"Sol {soil_type} adapte",
            ],
        ),
        CropRecommendation(
            rank=3, crop="Niebe", confidence=0.75,
            sowing_window=SowingWindow(start="Juillet-01", end="Juillet-30"),
            reasons=[
                "Resistant a la chaleur",
                "Culture vivriere essentielle",
                "Court cycle de croissance",
            ],
        ),
    ]


# ========================================================================
# Endpoints
# ========================================================================

@router.post("/recommend", response_model=RecommendationResponse)
def recommend_crops(
    request: RecommendationRequest,
    db: Session = Depends(get_db),
):
    """Recommande les meilleures cultures pour un point GPS au Benin.

    Etapes :
    1. Trouver la zone agro-ecologique la plus proche.
    2. Recuperer les donnees de sol via SoilGrids.
    3. Classifier le sol et evaluer la fertilite.
    4. Generer les recommandations (regles pour l'instant, ML plus tard).
    """
    # Etape 1 : trouver la zone
    zone = find_nearest_zone(request.latitude, request.longitude)

    # Etape 2 : donnees de sol
    soil_data = soil_service.get_soil_data(request.latitude, request.longitude)
    if not soil_data:
        raise HTTPException(
            status_code=404,
            detail="Impossible de recuperer les donnees de sol pour cette localisation.",
        )

    # Etape 3 : classifier le sol
    soil_type = classify_soil_type(
        soil_data.get("sand", 50),
        soil_data.get("clay", 20),
    )
    fertility = evaluate_fertility(
        soil_data.get("ph", 6.0),
        soil_data.get("soc", 15),
        soil_data.get("nitrogen", 1.5),
    )

    # Etape 4 : recommandations
    recommendations = rule_based_recommendation(zone, soil_data, soil_type)

    return RecommendationResponse(
        location=LocationInfo(
            latitude=request.latitude,
            longitude=request.longitude,
            nearest_zone=zone["name"],
            climate_type=zone["climate"],
        ),
        recommendations=recommendations,
        soil_summary=SoilSummary(
            soil_type=soil_type,
            ph=round(soil_data.get("ph", 6.0), 1),
            fertility=fertility,
        ),
    )


@router.post("/sowing-window", response_model=SowingWindowResponse)
def get_sowing_window(
    request: SowingWindowRequest,
    db: Session = Depends(get_db),
):
    """Predit la fenetre de semis optimale pour une culture et un lieu donnes.

    Basee sur l'analyse historique des precipitations.
    Le vrai algorithme de detection d'onset sera en Phase 3.
    """
    zone = find_nearest_zone(request.latitude, request.longitude)

    # Debut moyen des pluies selon la zone (valeurs approximatives)
    onset_par_climat = {
        "Subequatorial": ("Mars-15", "Mars-01"),
        "Soudano-guineen": ("Mai-15", "Mai-01"),
        "Soudanien": ("Juin-01", "Mai-20"),
        "Soudano-sahelien": ("Juin-20", "Juin-10"),
    }
    climate = zone["climate"]
    window_start, onset = onset_par_climat.get(climate, ("Juin-01", "Mai-20"))

    return SowingWindowResponse(
        location=LocationInfo(
            latitude=request.latitude,
            longitude=request.longitude,
            nearest_zone=zone["name"],
            climate_type=climate,
        ),
        crop=request.crop,
        sowing_window=SowingWindow(start=window_start, end="a calculer"),
        historical_onset=onset,
        confidence=0.75,
        advice=(
            f"Pour le {request.crop} dans la zone de {zone['name']}, "
            "semez dans les 2 semaines suivant les premieres pluies significatives."
        ),
    )
