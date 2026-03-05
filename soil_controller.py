import ee
import json
import numpy as np
import torch
from fastapi import Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.schemas.soil_schema import SoilAnalysisRecord
from app.core.config import settings
from app.ml.model import soil_nutrient_model, crop_recommendation_model


SATELLITE_BANDS = [
    'B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B8A', 'B9', 'B11', 'B12', 
    'elevation', 'slope'
]

def extract_soil_features(lat, lon):
    infor=json.loads(settings.GEE_SERVICE_ACCOUNT_JSON)
    infor["private_key"] = infor["private_key"].replace("\\n", "\n")
    print(infor)
    credentials = ee.ServiceAccountCredentials(
        infor["client_email"],
        key_data=json.dumps(infor)
    )
    ee.Initialize(credentials, project=infor["project_id"])
    point = ee.Geometry.Point([lon, lat])
    # Try 2024-2025 to ensure we have a processed 'Median' composite
    s2_data = (ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
               .filterBounds(point)
               .filterDate('2024-01-01', '2025-12-31') 
               .median())
    
    srtm = ee.Image("USGS/SRTMGL1_003")
    slope = ee.Terrain.slope(srtm)
    
    combined = s2_data.addBands(srtm).addBands(slope)
    
    # Use reduceRegion instead of sample for more reliability at a single point
    sample= combined.reduceRegion(
        reducer=ee.Reducer.first(),
        geometry=point,
        scale=20
    ).getInfo() 
    
    if not sample:
        raise Exception(f"No satellite data found for coordinates: {lat}, {lon}. Check if the date range has imagery.")
        
    return sample

def recommend_crop(nutrients):
    """
    Logic for Stage 2. This could be a second PyTorch model 
    or a Random Forest logic as per your Phase 3.
    """
    print(f"model {crop_recommendation_model}")
    # Example Decision Tree logic for Malawi context
    if nutrients["pH"] < 5.5:
        return "Groundnuts (Tolerance to acidity)"
    elif nutrients["Nitrogen"] > 0.2 and nutrients["pH"] > 6.0:
        return "Maize (Hybrid)"
    else:
        return "Soybeans"

def run_full_analysis( lat: float, lon: float,db: Session):
    # 1. Feature Extraction (The "Long Pixel" pierce)
    #Cache search for fast update
    threshold = 0.000001 
    existing_record = db.query(SoilAnalysisRecord).filter(
        func.abs(SoilAnalysisRecord.latitude - lat) < threshold,
        func.abs(SoilAnalysisRecord.longitude - lon) < threshold
    ).first()

    if existing_record:
        # Check if we have high-quality Ground Truth first
        if existing_record.is_ground_truth and existing_record.confidence_score >= 0.8:
            print("💎 Lab Data Hit! Returning verified ground truth.")
            return {
                "source": "ground_truth",
                "confidence": existing_record.confidence_score,
                "nutrients": {
                    "pH": existing_record.actual_ph,
                    "Nitrogen": existing_record.actual_nitrogen,
                    "Phosphorus": existing_record.actual_phosphorus,
                    "Potassium": existing_record.actual_potassium
                },
                "crop": existing_record.actual_recommended_crop,
                "raw_features": existing_record.raw_satellite_data
            }
        
        # If no ground truth, but a prediction exists
        print("Cache Hit! Returning previous AI prediction.")
        return {
            "source": "prediction_cache",
            "confidence": existing_record.ai_confidence,
            "nutrients": {
                "pH": existing_record.ph,
                "Nitrogen": existing_record.nitrogen,
                "Phosphorus": existing_record.phosphorus,
                "Potassium": existing_record.potassium
            },
            "crop": existing_record.recommended_crop,
            "raw_features": existing_record.raw_satellite_data
        }
    
    print("🛰️ Cache Miss. Fetching new data from Google Earth Engine...")
    # This calls your GEE logic
    print(f"model {soil_nutrient_model}")
    raw_features = extract_soil_features(lat, lon)
    ordered_features = {band: raw_features.get(band, 0) for band in SATELLITE_BANDS}

    # IMPORTANT: Ensure the order matches your training CSV (B1, B2... Elevation)
    feature_vector = np.array([list(ordered_features.values())], dtype=np.float32)
    input_tensor = torch.from_numpy(feature_vector)

    # 2. Stage 1: Predict Soil Chemistry (placeholder - needs model)
    with torch.no_grad():
        # predictions = model(input_tensor).numpy()[0]  # TODO: Load actual model
        predictions = np.array([6.5, 0.15, 0.08, 0.12])  # Placeholder: [pH, N, P, K]
        calculated_ai_confidence = 0.88
        
    nutrients = {
        "pH": float(predictions[0]),
        "Nitrogen": float(predictions[1]),
        "Phosphorus": float(predictions[2]),
        "Potassium": float(predictions[3])
    }

    # 3. Stage 2: Agronomic Decision (Crop Recommendation)
    recommended_crop = recommend_crop(nutrients)
    #adding to the database 
    new_record = SoilAnalysisRecord(
        latitude=lat,
        longitude=lon,
        ph=nutrients["pH"],
        nitrogen=nutrients["Nitrogen"],
        phosphorus=nutrients["Phosphorus"],
        potassium=nutrients["Potassium"],
        recommended_crop=recommended_crop,
        ai_confidence=calculated_ai_confidence,
        raw_satellite_data=ordered_features # This saves all 13 bands as a JSON blob
    )
    
    # Save to database
    db.add(new_record)
    db.commit()
    db.refresh(new_record)

    return {
        "source": "new_prediction",
        "confidence": calculated_ai_confidence,
        "nutrients": nutrients,
        "crop": recommended_crop,
        "raw_features": ordered_features
    }


def updating_ground_truth(
    lat: float, 
    lon: float, 
    actual_ph: float, 
    actual_nitrogen: float, 
    actual_phosphorus: float, 
    actual_potassium: float, 
    actual_recommended_crop: str, 
    confidence: float,
    db: Session
):
    # 1. Find the exact record
    record = db.query(SoilAnalysisRecord).filter(
        SoilAnalysisRecord.latitude == lat,
        SoilAnalysisRecord.longitude == lon,
        SoilAnalysisRecord.is_ground_truth == True
    ).first()

    if not record:
        raise HTTPException(
            status_code=404, 
            detail="No ground truth record found at these exact coordinates to update."
        )

    # 2. Apply the corrections
    record.actual_ph = actual_ph
    record.actual_nitrogen = actual_nitrogen
    record.actual_phosphorus = actual_phosphorus
    record.actual_potassium = actual_potassium
    record.actual_recommended_crop = actual_recommended_crop
    record.confidence_score = confidence
    
    # Update the timestamp so we know when the correction happened
    record.created_at = func.now()

    db.commit()
    db.refresh(record)
    return {"status": "Success", "message": "Ground truth record corrected."}

def deleting_ground_truth(lat: float, lon: float, db: Session):
    # 1. Find the exact record
    record = db.query(SoilAnalysisRecord).filter(
        SoilAnalysisRecord.latitude == lat,
        SoilAnalysisRecord.longitude == lon,
        SoilAnalysisRecord.is_ground_truth == True
    ).first()

    if not record:
        raise HTTPException(
            status_code=404, 
            detail="Record not found. Nothing to delete."
        )

    # 2. Remove it from the database
    db.delete(record)
    db.commit()
    
    return {"status": "Success", "message": "Ground truth record deleted successfully."}