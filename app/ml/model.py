# import torch
# import torch.nn as nn
# import numpy as np

# # Stage 1: Neural Network for Soil Nutrients
# class SoilNutrientNet(nn.Module):
#     def __init__(self, input_dim=14): # 13 bands + 1 elevation
#         super(SoilNutrientNet, self).__init__()
#         self.layer1 = nn.Linear(input_dim, 64)
#         self.layer2 = nn.Linear(64, 32)
#         self.output = nn.Linear(32, 4) # Outputs: [pH, N, P, K]
#         self.relu = nn.ReLU()
#         self.norm1 = nn.LayerNorm(input_dim)
#         self.norm2 = nn.LayerNorm(64)
#         self.norm3 = nn.LayerNorm(32)

#     def forward(self, x):
#         x = self.norm1(x)
#         x = self.relu(self.layer1(x))
#         x = self.norm2(x)
#         x = self.relu(self.layer2(x))
#         x = self.norm3(x)
#         return self.output(x)

# class CropRecommendationNet(nn.Module):
#     def __init__(self, input_dim=4): # 4 nutrients
#         super(CropRecommendationNet, self).__init__()
#         self.layer1 = nn.Linear(input_dim, 16)
#         self.layer2 = nn.Linear(16, 8)
#         self.output = nn.Linear(8, 3) # Outputs: [crop1, crop2, crop3]
#         self.relu = nn.ReLU()
#         self.norm1 = nn.LayerNorm(input_dim)
#         self.norm2 = nn.LayerNorm(16)
#         self.norm3 = nn.LayerNorm(8)

#     def forward(self, x):
#         x=self.norm1(x)
#         x = self.relu(self.layer1(x))
#         x = self.norm2(x)
#         x = self.relu(self.layer2(x))
#         x = self.norm3(x)
#         return self.output(x)

# soil_nutrient_model = SoilNutrientNet(13)
# crop_recommendation_model = CropRecommendationNet(4)
