from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Agri-Assistant"
    API_V1_STR: str = "/api/v1"
    
    # Database
    DATABASE_URL: str = "sqlite:///./data/agridata.sqlite"
    
    # SoilGrids API
    SOILGRIDS_API_URL: str = "https://rest.isric.org/soilgrids/v2.0/properties/query"

    class Config:
        case_sensitive = True

settings = Settings()
