"""Service pour recuperer les donnees climatiques exactes.

Ce service interroge l'API NASA POWER (Climatology) pour obtenir
les moyennes historiques d'un point GPS precis, sans utiliser d'approximation
par zone. Cela garantit une precision maximale pour la prediction.
"""

import requests
import logging
from typing import Dict, Any

from api.core.config import settings

logger = logging.getLogger(__name__)

class WeatherService:
    """Gere la recuperation des donnees climatiques."""

    def __init__(self):
        # On utilise l'endpoint climatology pour avoir les moyennes historiques
        # directement, ce qui est tres rapide.
        self.base_url = "https://power.larc.nasa.gov/api/temporal/climatology/point"

    def get_climate_data(self, latitude: float, longitude: float) -> Dict[str, Any] | None:
        """Recupere les moyennes climatiques pour un GPS exact.

        Args:
            latitude: Latitude du champ.
            longitude: Longitude du champ.

        Returns:
            Dictionnaire contenant les donnees climatiques formatees, ou None en cas d'erreur.
        """
        # Parametres :
        # T2M = Temperature moyenne
        # PRECTOTCORR = Precipitations (mm/jour)
        # RH2M = Humidite relative
        params = {
            "parameters": "T2M,PRECTOTCORR,RH2M",
            "community": "AG",
            "longitude": longitude,
            "latitude": latitude,
            "format": "JSON"
        }

        try:
            logger.info(f"Interrogation NASA POWER pour GPS: {latitude}, {longitude}")
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            properties = data.get("properties", {}).get("parameter", {})
            
            if not properties:
                logger.error("Format de reponse inattendu de NASA POWER.")
                return None

            # Les valeurs "ANN" sont les moyennes annuelles.
            # PRECTOTCORR est en mm/jour. Il faut multiplier par 365 pour le total annuel.
            avg_daily_precip = properties.get("PRECTOTCORR", {}).get("ANN", 0)
            annual_rainfall = avg_daily_precip * 365.25

            return {
                "latitude": latitude,
                "longitude": longitude,
                "temp_mean_c": properties.get("T2M", {}).get("ANN", 25.0),
                "rainfall_annual_mm": annual_rainfall,
                "humidity_pct": properties.get("RH2M", {}).get("ANN", 70.0),
                # On garde aussi les donnees mensuelles pour le calcul du cycle exact de la plante
                "monthly_temp": properties.get("T2M", {}),
                "monthly_precip": properties.get("PRECTOTCORR", {}),
                "monthly_humidity": properties.get("RH2M", {})
            }

        except requests.RequestException as error:
            logger.error(f"Erreur lors de l'appel NASA POWER : {error}")
            return None


# Instance globale pour etre utilisee dans les routers
weather_service = WeatherService()
