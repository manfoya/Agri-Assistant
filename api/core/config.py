"""Configuration centralisee de l'application.

Toutes les constantes et URLs externes sont rassemblees ici
pour eviter de les eparpiller dans le code.
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Parametres globaux du projet, chargeables depuis un .env."""

    PROJECT_NAME: str = "Agri-Assistant"
    VERSION: str = "0.2.0"
    API_V1_STR: str = "/api/v1"

    # -- Base de donnees --
    DATABASE_URL: str = "sqlite:///./data/agridata.sqlite"

    # -- API SoilGrids (donnees de sol) --
    SOILGRIDS_API_URL: str = "https://rest.isric.org/soilgrids/v2.0/properties/query"

    # -- API NASA POWER (donnees meteo) --
    NASA_POWER_API_URL: str = "https://power.larc.nasa.gov/api/temporal/daily/point"

    class Config:
        case_sensitive = True


settings = Settings()
