import ee

credentials = ee.ServiceAccountCredentials(
    "gee-soil-analyzer@digital-soil-analysis.iam.gserviceaccount.com", 
    "gee-key.json"
)
ee.Initialize(credentials, project="digital-soil-analysis")

def extract_soil_features(lat, lon):
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
    sample = combined.reduceRegion(
        reducer=ee.Reducer.first(),
        geometry=point,
        scale=20
    ).getInfo()
    
    if not sample:
        raise Exception(f"No satellite data found for coordinates: {lat}, {lon}. Check if the date range has imagery.")
        
    return sample

def run_full_analysis(self, lat: float, lon: float):
        # 1. Feature Extraction (The "Long Pixel" pierce)
        # This calls your GEE logic
        raw_features = extract_satellite_features(lat, lon)
        
        # Convert dict to a sorted list/numpy array for the tensor
        # IMPORTANT: Ensure the order matches your training CSV (B1, B2... Elevation)
        feature_vector = np.array([list(raw_features.values())], dtype=np.float32)
        input_tensor = torch.from_numpy(feature_vector)

        # 2. Stage 1: Predict Soil Chemistry
        with torch.no_grad():
            predictions = self.model(input_tensor).numpy()[0]
            
        nutrients = {
            "pH": float(predictions[0]),
            "Nitrogen": float(predictions[1]),
            "Phosphorus": float(predictions[2]),
            "Potassium": float(predictions[3])
        }

        # 3. Stage 2: Agronomic Decision (Crop Recommendation)
        # This implements the logic: Predicted Nutrients -> Best Crop
        recommended_crop = self.recommend_crop(nutrients)

        return {
            "nutrients": nutrients,
            "crop": recommended_crop,
            "raw_features": raw_features
        }

def recommend_crop(self, nutrients):
    """
    Logic for Stage 2. This could be a second PyTorch model 
    or a Random Forest logic as per your Phase 3.
    """
    # Example Decision Tree logic for Malawi context
    if nutrients["pH"] < 5.5:
        return "Groundnuts (Tolerance to acidity)"
    elif nutrients["Nitrogen"] > 0.2 and nutrients["pH"] > 6.0:
        return "Maize (Hybrid)"
    else:
        return "Soybeans"
