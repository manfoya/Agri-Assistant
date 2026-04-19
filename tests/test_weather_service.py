import pytest
from unittest.mock import patch, MagicMock
import requests
from api.services.weather_service import WeatherService

def test_get_climate_data_success():
    service = WeatherService()
    
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "properties": {
            "parameter": {
                "T2M": {"ANN": 26.5},
                "PRECTOTCORR": {"ANN": 3.0}, # 3 mm/day -> ~1095 mm/year
                "RH2M": {"ANN": 75.0}
            }
        }
    }
    
    with patch("requests.get", return_value=mock_response):
        result = service.get_climate_data(10.0, 2.0)
        
        assert result is not None
        assert result["latitude"] == 10.0
        assert result["temp_mean_c"] == 26.5
        assert result["humidity_pct"] == 75.0
        assert 1095 <= result["rainfall_annual_mm"] <= 1096

def test_get_climate_data_retries_and_fails():
    service = WeatherService()
    
    # Simuler une exception reseau
    with patch("requests.get", side_effect=requests.RequestException("API Down")) as mock_get:
        # Patch sleep to avoid waiting during tests
        with patch("time.sleep"):
            result = service.get_climate_data(10.0, 2.0)
            
            assert result is None
            assert mock_get.call_count == 3
