import pytest
from unittest.mock import patch, MagicMock
import requests
from api.services.soil_service import SoilService

def test_get_soil_data_fallback():
    service = SoilService()
    
    # Simuler une panne de l'API SoilGrids
    with patch.object(service, 'get_soil_property', return_value=None):
        result = service.get_soil_data(10.0, 2.0)
        
        # Le service doit renvoyer les valeurs par defaut du fallback
        assert result["sand"] == 68.7
        assert result["clay"] == 18.8
        assert result["ph"] == 6.2
        assert result["nitrogen"] == 2.1

def test_get_soil_data_success():
    service = SoilService()
    
    # Simuler une reponse partielle (certaines proprietes marchent, d'autres non)
    def mock_get_property(lat, lon, prop):
        if prop == "phh2o":
            return 5.5
        return None
        
    with patch.object(service, 'get_soil_property', side_effect=mock_get_property):
        result = service.get_soil_data(10.0, 2.0)
        
        # Le pH doit etre la vraie donnee (5.5) et pas le fallback (6.2)
        assert result["ph"] == 5.5
        # Le sable doit etre le fallback car il a retourne None
        assert result["sand"] == 68.7
