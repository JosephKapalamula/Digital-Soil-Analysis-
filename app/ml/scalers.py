import joblib
import os 
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
def load_scalers():
    scaler_X = joblib.load(os.path.join(BASE_DIR, "scaler_X.pkl"))
    scaler_y = joblib.load(os.path.join(BASE_DIR, "scaler_y.pkl"))
    crop_encoder = joblib.load(os.path.join(BASE_DIR, "crop_encoder.pkl"))
    crop_recommendation_model=joblib.load(os.path.join(BASE_DIR, "crop_recommender_model.pkl"))
    nutrient_model = joblib.load(os.path.join(BASE_DIR, "nutrient_model.pkl"))
    scaler_b_crops = joblib.load(os.path.join(BASE_DIR, "scaler_B_crops.pkl"))
    return {
        "scaler_x": scaler_X,
        "scaler_y": scaler_y,
        "crop_encoder": crop_encoder,
        "crop_recommendation_model": crop_recommendation_model,
        "nutrient_model": nutrient_model,
        "scaler_b_crops": scaler_b_crops
    }


    