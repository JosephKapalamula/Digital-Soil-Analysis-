import numpy as np
def generate_farmer_report(crop, nutrients, shap_values):
    # nutrients index: 0=pH, 1=N, 2=P, 3=K, 4=Lat, 5=Lon
    # shap_values index: matches nutrients
    
    report = f"## 🌾 AI Field Analysis: {crop}\n"
    report += f"Based on satellite-derived soil data at your GPS location, **{crop}** is the most viable crop for your field.\n\n"

    # --- TOP ASSET ---
    # Find the feature with the highest positive SHAP value (excluding Lat/Lon)
    nutrient_shaps = shap_values[:4]
    best_feature_idx = np.argmax(nutrient_shaps)
    best_feature_name = ["pH Balance", "Nitrogen Level", "Phosphorus Level", "Potassium Level"][best_feature_idx]
    
    report += f"### ✅ Why {crop}?\n"
    report += f"The primary reason for this recommendation is your **{best_feature_name}**. "
    report += f"It provides a strong foundation for {crop} to thrive in this specific soil profile.\n\n"

    # --- SPECIFIC NUTRIENT BREAKDOWN ---
    report += "### 🔍 Nutrient Observations\n"

    # Nitrogen Logic
    if shap_values[1] > 0:
        report += f"* **Nitrogen ({nutrients[1]:.1f}):** High impact! Your soil has sufficient nitrogen to support healthy leaf and stalk growth.\n"
    else:
        report += f"* **Nitrogen ({nutrients[1]:.1f}):** Low impact. You may need to supplement with Urea or organic manure to see the best results.\n"

    # pH Logic
    if shap_values[0] > 0:
        report += f"* **Soil Acidity ({nutrients[0]:.1f}):** Your pH is in the 'Optimal Zone' for {crop}, ensuring nutrients are easily absorbed by roots.\n"
    else:
        report += f"* **Soil Acidity ({nutrients[0]:.1f}):** Your soil is slightly outside the ideal range. Consider a soil test for lime requirements.\n"

    # Potassium/Phosphorus Logic
    if shap_values[3] > 1.0: # Strong Potassium (as seen in your SHAP output)
        report += f"* **Potassium ({nutrients[3]:.1f}):** Exceptional! This strength will help {crop} resist disease and improve water retention.\n"

    # --- AGRONOMY ADVICE ---
    report += f"\n### 💡 Quick Advice for {crop}\n"
    if crop == 'Maize':
        report += "Ensure early weeding and top-dress with Nitrogen-rich fertilizer 3-4 weeks after planting."
    elif 'Soy' in crop or 'Bean' in crop:
        report += "Focus on Phosphorus application at planting to help with root nodule formation."
    elif 'Cassava' in crop:
        report += "Cassava is hardy, but ensure your soil has good drainage to prevent tuber rot."
    else:
        report += "Consult your local extension officer for the specific planting window in your region."

    return report