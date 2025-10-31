from fastapi import FastAPI

app = FastAPI()


@app.get("/recommend")
def recommend(lat: float, lon: float):
    """
    Endpoint to get crop recommendations based on location.
    
    Args:
        lat: Latitude coordinate
        lon: Longitude coordinate
    
    Returns:
        JSON response with crop recommendation and confidence score
    """
    return {"crop": "Maize", "confidence": 0.9}
