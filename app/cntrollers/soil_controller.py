import ee
import json
import pandas as pd
import numpy as np
from fastapi import Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.schemas.soil_schema import SoilAnalysisRecord
from app.core.config import settings
from app.ml.scalers import load_scalers
from app.ml.report_on_recommended_crop import generate_farmer_report
import shap

# SATELLITE_BANDS = [
#     'B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B8A', 'B9', 'B11', 'B12', 
#     'elevation', 'slope'
# ]
MODEL_A_BANDS = ['B2', 'B3', 'B4', 'B8']

def extract_soil_features(lat, lon):
    infor=json.loads(settings.GEE_SERVICE_ACCOUNT_JSON)
    infor["private_key"] = infor["private_key"].replace("\\n", "\n")
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
        scale=10 #20
    ).getInfo() 
    
    if not sample:
        raise Exception(f"No satellite data found for coordinates: {lat}, {lon}. Check if the date range has imagery.")
        
    return sample

def recommend_crop(scalers,nutrients):
    feature_names = ['ph', 'nitrogen', 'phosphorus', 'potassium', 'latitude', 'longitude']
    raw_nutrients = pd.DataFrame([nutrients], columns=feature_names)
    scaled_nutrients=scalers["scaler_b_crops"].transform(raw_nutrients)
    predicted_crop = scalers["crop_recommendation_model"].predict(scaled_nutrients)
    recommended_crop = scalers["crop_encoder"].inverse_transform([predicted_crop])[0]
    feature_names = ['pH', 'Nitrogen', 'Phosphorus', 'Potassium', 'Latitude', 'Longitude']

    explainer = shap.TreeExplainer(scalers["crop_recommendation_model"])
    shap_values = explainer.shap_values(scaled_nutrients)
    if isinstance(shap_values, list):
        # Older SHAP returns list of arrays
        current_shap = shap_values[predicted_crop[0]][0]
    elif hasattr(shap_values, "values"):
        # SHAP Explanation object - extract raw values
        # Shape: (samples, features, classes)
        current_shap = shap_values.values[0, :, predicted_crop[0]]
    else:
        # Standard Numpy Array
        current_shap = shap_values[0, :, predicted_crop[0]]

    report=generate_farmer_report(recommended_crop, nutrients, current_shap)
    print(f"report: {report}")
    return recommended_crop, report

def run_full_analysis( lat: float, lon: float,db: Session):
    # lat=-13.969802255525753
    # lon=33.73717904090882
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
            nutrients_list = [{
                "pH": float(existing_record.actual_ph),
                "Nitrogen": float(existing_record.actual_nitrogen),
                "Phosphorus":float(existing_record.actual_phosphorus),
                "Potassium": float(existing_record.actual_potassium)
                }]
            return {
                "source": "ground_truth",
                "confidence": float(existing_record.confidence_score),
                "nutrients": nutrients_list,
                "crop": str(existing_record.actual_recommended_crop),
}
        
        # If no ground truth, but a prediction exists
        print("Cache Hit! Returning previous AI prediction.")
        nutrients_list = [{
        "pH": float(existing_record.ph),
        "Nitrogen":  float(existing_record.nitrogen),
        "Phosphorus": float(existing_record.phosphorus),
        "Potassium":  float(existing_record.potassium)
         }]
        return {
            "source": "prediction_cache", # or "ground_truth" / "new_prediction"
            "confidence": float(existing_record.ai_confidence), 
            "nutrients":nutrients_list,
            "crop": str(existing_record.recommended_crop),
            # "report": str(report)
        }
                        
    print(f"lati {lat},long {lon}")
    print("🛰️ Cache Miss. Fetching new data from Google Earth Engine...")
    # raw_features = extract_soil_features(lat, lon)
    # ordered_features = {band: raw_features.get(band, 0) for band in SATELLITE_BANDS}
    raw_bands = extract_soil_features(lat, lon)
    input_data = [
    raw_bands['B2'], # Blue
    raw_bands['B3'], # Green
    raw_bands['B4'], # Red
    raw_bands['B8'], # NIR
    lat,
    lon
]
    scalers = load_scalers()
    # # IMPORTANT: Ensure the order matches your training CSV (B1, B2... Elevation)
    # feature_vector = np.array([list(ordered_features.values())], dtype=np.float32)
    # scaled_features = scalers["scaler_X"].transform(feature_vector)
    # # 2. Stage 1: Predict Soil Chemistry (placeholder - needs model)
    feature_names = ['band_blue', 'band_green', 'band_red', 'band_nir', 'latitude', 'longitude']
    feature_vector=pd.DataFrame([input_data], columns=feature_names)
    scaled_features = scalers["scaler_x"].transform(feature_vector)
    # Model A predicts scaled nutrients (0 to 1)
    preds_scaled = scalers["nutrient_model"].predict(scaled_features)
    # Inverse scale to get real soil values [pH, N, P, K]
    preds_real = scalers["scaler_y"].inverse_transform(preds_scaled)[0]
    confidence = 0.85
        
    nutrients =[
        float(preds_real[0]),
        float(preds_real[1]),
        float(preds_real[2]),
        float(preds_real[3]),
        lat,
        lon
    ]
    nutrients_dict={
                "pH": float(preds_real[0]),
                "Nitrogen": float(preds_real[1]),
                "Phosphorus": float(preds_real[2]),
                "Potassium": float(preds_real[3])
            },
    # 3. Stage 2: Agronomic Decision (Crop Recommendation)
    recommended_crop,report = recommend_crop(scalers,nutrients)
    #adding to the database 
    new_record = SoilAnalysisRecord(
        latitude=lat,
        longitude=lon,
        ph=nutrients[0],
        nitrogen=nutrients[1],
        phosphorus=nutrients[2],
        potassium=nutrients[3],
        recommended_crop=recommended_crop,
        ai_confidence=confidence,
        raw_satellite_data=raw_bands # This saves all 13 bands as a JSON blob
    )
    # Save to database 
    db.add(new_record)
    db.commit()
    db.refresh(new_record)
    print("pass3")
    return {
    "source": "new_prediction", 
    "confidence": float(confidence),
    "nutrients": nutrients_dict,
    "crop": str(recommended_crop),
    "report": report
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