"""Point d'entree de l'API Agri-Assistant.

Lance le serveur FastAPI, enregistre les routers,
et cree les tables manquantes dans la BDD au demarrage.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from api.core.config import settings
from api.core.database import engine, Base

# On importe les modeles pour que SQLAlchemy les connaisse
# et puisse creer les tables au demarrage.
from api.models import SoilData, WeatherData, RecommendationLog  # noqa: F401

# Routers
from api.routers import health, recommend, data


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Actions au demarrage et a l'arret du serveur."""

    # Demarrage : creer les tables si elles n'existent pas.
    # Les tables existantes (weather_data, soil_data) ne seront pas ecrasees.
    Base.metadata.create_all(bind=engine)
    print(f"[Agri-Assistant v{settings.VERSION}] API demarree.")
    yield
    # Arret
    print(f"[Agri-Assistant] API arretee.")


app = FastAPI(
    title=settings.PROJECT_NAME,
    description=(
        "Systeme intelligent de recommandation de cultures "
        "et de prediction de fenetres de semis pour le Benin. "
        "Utilise les donnees de sol (SoilGrids), meteo (NASA POWER) "
        "et un modele de Machine Learning."
    ),
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
)

# -- CORS : autorise toutes les origines pour le developpement.
# A restreindre en production.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -- Enregistrement des routers --
app.include_router(health.router)
app.include_router(recommend.router)
app.include_router(data.router)


@app.get("/", tags=["UI"])
async def serve_index():
    """Sert l'application Web PWA au chemin racine."""
    return FileResponse("static/index.html")

# On monte le reste du dossier static (css, js, images) a la racine
app.mount("/", StaticFiles(directory="static"), name="static")
