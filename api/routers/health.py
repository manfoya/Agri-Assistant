"""Router /health -- verification de l'etat du systeme.

Permet de savoir rapidement si la BDD repond
et si le modele ML est charge.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from api.core.database import get_db
from api.core.config import settings
from api.schemas.weather import HealthResponse

router = APIRouter(tags=["Sante"])


@router.get("/health", response_model=HealthResponse)
def health_check(db: Session = Depends(get_db)):
    """Verifie la BDD, compte les enregistrements, et l'etat du modele ML."""

    db_status = "disconnected"
    weather_count = 0
    soil_count = 0

    try:
        weather_count = db.execute(text("SELECT COUNT(*) FROM weather_data")).scalar()
        soil_count = db.execute(text("SELECT COUNT(*) FROM soil_data")).scalar()
        db_status = "connected"
    except Exception:
        db_status = "error"

    # Le modele ML sera charge plus tard (Phase 3).
    ml_loaded = False

    return HealthResponse(
        status="ok" if db_status == "connected" else "degraded",
        version=settings.VERSION,
        database=db_status,
        weather_records=weather_count,
        soil_records=soil_count,
        ml_model_loaded=ml_loaded,
    )
