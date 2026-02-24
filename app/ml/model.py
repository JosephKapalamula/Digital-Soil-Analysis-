import torch
import torch.nn as nn
import numpy as np
from app.ml.feature_eng import extract_satellite_features

# Stage 1: Neural Network for Soil Nutrients
class SoilNutrientNet(nn.Module):
    def __init__(self, input_dim=14): # 13 bands + 1 elevation
        super(SoilNutrientNet, self).__init__()
        self.layer1 = nn.Linear(input_dim, 64)
        self.layer2 = nn.Linear(64, 32)
        self.output = nn.Linear(32, 4) # Outputs: [pH, N, P, K]
        self.relu = nn.ReLU()

    def forward(self, x):
        x = self.relu(self.layer1(x))
        x = self.relu(self.layer2(x))
        return self.output(x)

