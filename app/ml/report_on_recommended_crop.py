import numpy as np

def generate_farmer_report(crop, nutrients, shap_values):
    """
    Generates a concise, professional soil analysis report.
    nutrients index: 0=pH, 1=N, 2=P, 3=K
    shap_values index: matches nutrients
    """
    
    report = f"## for the recommended {crop}\n"
    report += f"Based on satellite-derived soil data at your GPS location, {crop} is identified as the most viable crop for this field.\n\n"

    # --- TOP ASSET ---
    # Focus on the most positive driver for the recommendation
    nutrient_shaps = shap_values[:4]
    best_feature_idx = np.argmax(nutrient_shaps)
    best_feature_names = ["pH Balance", "Nitrogen Level", "Phosphorus Level", "Potassium Level"]
    best_feature_name = best_feature_names[best_feature_idx]
    
    report += f"### Why {crop}?\n"
    report += f"The primary driver for this recommendation is your {best_feature_name}. "
    report += f"This parameter provides the strongest foundation for {crop} development within this specific soil profile.\n\n"

    # --- NUTRIENT OBSERVATIONS ---
    report += "### Nutrient Observations\n"

    # Nitrogen (Index 1)
    if shap_values[1] > 0:
        report += f"* Nitrogen ({nutrients[1]:.1f}): Sufficient levels detected to support leaf and stalk development.\n"
    else:
        report += f"* Nitrogen ({nutrients[1]:.1f}): Sub-optimal impact. Supplemental nitrogen may be required for maximum yield.\n"

    # pH (Index 0)
    if shap_values[0] > 0:
        report += f"* Soil Acidity ({nutrients[0]:.1f}): pH is within the optimal range, facilitating efficient nutrient uptake.\n"
    else:
        report += f"* Soil Acidity ({nutrients[0]:.1f}): pH level is outside the ideal range, which may limit nutrient availability.\n"

    # Potassium (Index 3)
    if shap_values[3] > 1.0:
        report += f"* Potassium ({nutrients[3]:.1f}): Strong levels detected, contributing to disease resistance and water retention.\n"

    return report