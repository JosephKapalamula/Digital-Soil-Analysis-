from pydantic import BaseModel, Field

class SoilRequest(BaseModel):
    latitude: float = Field(..., ge=-18.0, le=-9.0, description="Latitude within Malawi bounds")
    longitude: float = Field(..., ge=32.0, le=36.0, description="Longitude within Malawi bounds")

class SoilResponse(BaseModel):
    latitude: float
    longitude: float
    nutrients: dict # Will contain N, P, K, pH
    recommended_crop: str
    confidence_score: float