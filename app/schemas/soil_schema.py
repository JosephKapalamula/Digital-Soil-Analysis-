from pydantic import BaseModel, Field
from sqlalchemy import Column, Integer, Float, String, JSON, DateTime,Boolean
from sqlalchemy.sql import func
from app.db.session import Base
# from app.db.base import Base

class SoilRequest(BaseModel):
    latitude: float = Field(..., ge=-18.0, le=-9.0, description="Latitude within Malawi bounds")
    longitude: float = Field(..., ge=32.0, le=36.0, description="Longitude within Malawi bounds")

class SoilResponse(BaseModel):
    latitude: float 
    longitude: float  
    nutrients: dict # Will contain N, P, K, pH
    recommended_crop: str
    confidence_score: float
class UpdateGroundTruthRequest(BaseModel):
    latitude: float
    longitude: float 
    actual_ph: float
    actual_nitrogen: float 
    actual_phosphorus: float
    actual_potassium: float
    actual_recommended_crop: str
    confidence_score: float
class DeleteGroundTruthRequest(BaseModel):
    latitude: float
    longitude: float

class DataRequest(BaseModel):
    location: str
    latitude: float
    longitude: float
    ph: float
    nitrogen: float
    phosphorus: float
    potassium: float
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    recommended_crop: str 

class SoilAnalysisRecord(Base):
    __tablename__ = "soil_analyses"

    id = Column(Integer, primary_key=True, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    
    # Store the ML results
    ph = Column(Float,nullable=True)
    nitrogen = Column(Float,nullable=True)
    phosphorus = Column(Float,nullable=True)
    potassium = Column(Float,nullable=True)
    recommended_crop = Column(String,nullable=True)
    ai_confidence = Column(Float, nullable=True)
    #ground truth 
    location = Column(String, nullable=True) 
    actual_ph=Column(Float,nullable=True)
    actual_nitrogen=Column(Float,nullable=True)
    actual_phosphorus=Column(Float,nullable=True)
    actual_potassium=Column(Float,nullable=True)
    actual_recommended_crop=Column(String,nullable=True)
    is_ground_truth = Column(Boolean, default=False)
    confidence_score = Column(Float, nullable=True)
    raw_satellite_data = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())