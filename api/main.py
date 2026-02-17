from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from typing import Dict, Any

from api.core.config import settings
from api.services.soil_service import soil_service

app = FastAPI(title=settings.PROJECT_NAME, openapi_url=f"{settings.API_V1_STR}/openapi.json")

class CropRecommendationRequest(BaseModel):
    latitude: float
    longitude: float

class CropRecommendationResponse(BaseModel):
    crop: str
    confidence: float
    soil_data: Dict[str, Any]

@app.get("/")
def root():
    return {"message": "Welcome to Agri-Assistant API"}

@app.post("/recommend", response_model=CropRecommendationResponse)
def recommend(request: CropRecommendationRequest):
    """
    Endpoint to get crop recommendations based on location.
    Fetches real soil data from SoilGrids (or fallback).
    """
    # 1. Get Soil Data
    soil_data = soil_service.get_soil_data(request.latitude, request.longitude)
    
    if not soil_data:
        raise HTTPException(status_code=404, detail="Could not fetch soil data for this location")

    # 2. Predict (Placeholder for ML Model)
    # TODO: Load trained model and predict based on soil_data + weather history
    prediction = "Maize" 
    confidence = 0.85

    return {
        "crop": prediction,
        "confidence": confidence,
        "soil_data": soil_data
    }
