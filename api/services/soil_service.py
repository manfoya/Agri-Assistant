import requests
import time
from requests.exceptions import RequestException
from typing import Optional, Dict

from api.core.config import settings

class SoilService:
    def __init__(self):
        self.base_url = settings.SOILGRIDS_API_URL

    def get_soil_property(self, lat: float, lon: float, prop: str, depth="0-5cm", value="mean", retries=2, timeout=10) -> Optional[float]:
        """
        Interroge l'API SoilGrids pour une propriété, une latitude et une longitude données.
        Avec gestion robuste des erreurs et retry.
        """
        params = {
            "lat": lat,
            "lon": lon,
            "property": prop,
            "depth": depth,
            "value": value
        }

        attempt = 0
        while True:
            attempt += 1
            try:
                # print(f"--- Interrogation pour la propriété : {prop} ---")
                r = requests.get(self.base_url, params=params, timeout=timeout)
            except RequestException as e:
                print(f"Requête échouée pour '{prop}' (network): {e}")
                if attempt <= retries:
                    time.sleep(0.5 * attempt)
                    continue
                return None

            if r.status_code == 200:
                try:
                    data = r.json()
                    mean_value = data['properties']['layers'][0]['depths'][0]['values']['mean']
                    d_factor = data['properties']['layers'][0]['unit_measure']['d_factor']
                    # unit = data['properties']['layers'][0]['unit_measure']['target_units']

                    if mean_value is not None and d_factor is not None and d_factor != 0:
                        final_value = mean_value / d_factor
                        return final_value
                    else:
                        return None

                except (KeyError, IndexError, TypeError) as e:
                    print(f"Erreur en parsant la réponse JSON pour '{prop}': {e}")
                    return None
            
            if 500 <= r.status_code < 600 and attempt <= retries:
                time.sleep(0.5 * attempt)
                continue
            else:
                return None

    def get_soil_data(self, lat: float, lon: float) -> Dict[str, float]:
        """
        Récupère l'ensemble des données de sol pour une coordonnée.
        Utilise des valeurs par défaut si l'API échoue (simulation pour démo).
        """
        properties = {
            "sand": "sand",
            "clay": "clay",
            "ph": "phh2o",
            "soc": "soc",
            "nitrogen": "nitrogen", 
            "cec": "cec",
            "bdod": "bdod"
        }
        
        results = {}
        
        # Pour la démo, si l'API est HS ou lente, on peut fallback sur des valeurs typiques du Bénin
        # Mais essayons d'abord l'API
        
        for name, prop_id in properties.items():
            val = self.get_soil_property(lat, lon, prop_id)
            if val is not None:
                results[name] = val
        
        # Si résultats incomplets, on complète avec des moyennes (FALLBACK)
        # Ceci est important pour que le modèle ML ne plante pas
        defaults = {
            "sand": 68.7, "clay": 18.8, "ph": 6.2, "soc": 26.1,
            "nitrogen": 2.1, "cec": 15.3, "bdod": 1.4
        }
        
        for k, v in defaults.items():
            if k not in results or results[k] is None:
                results[k] = v
                
        return results

soil_service = SoilService()
