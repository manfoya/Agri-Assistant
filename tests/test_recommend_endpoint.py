import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from api.main import app

client = TestClient(app)

@patch("api.routers.recommend.weather_service.get_climate_data")
@patch("api.routers.recommend.soil_service.get_soil_data")
def test_recommend_endpoint_success(mock_soil, mock_weather):
    # Simuler des donnees parfaites pour que l'algo renvoie un resultat
    mock_soil.return_value = {
        "sand": 60.0, "clay": 20.0, "ph": 6.5, "soc": 25.0, 
        "nitrogen": 2.0, "cec": 15.0, "bdod": 1.2
    }
    
    mock_weather.return_value = {
        "latitude": 9.0,
        "longitude": 2.0,
        "temp_mean_c": 27.0,
        "rainfall_annual_mm": 1100.0,
        "humidity_pct": 75.0,
        "monthly_temp": {},
        "monthly_precip": {},
        "monthly_humidity": {}
    }
    
    response = client.post("/api/v1/recommend", json={"latitude": 9.0, "longitude": 2.0})
    
    assert response.status_code == 200
    data = response.json()
    assert "recommendations" in data
    assert "location" in data
    assert data["location"]["latitude"] == 9.0

@patch("api.routers.recommend.weather_service.get_climate_data")
@patch("api.routers.recommend.soil_service.get_soil_data")
def test_recommend_endpoint_weather_failure(mock_soil, mock_weather):
    mock_soil.return_value = {"sand": 60.0}
    # Simuler l'echec du fallback NASA
    mock_weather.return_value = None
    
    response = client.post("/api/v1/recommend", json={"latitude": 9.0, "longitude": 2.0})
    
    assert response.status_code == 503
    data = response.json()
    assert "inaccessible" in data["detail"]
