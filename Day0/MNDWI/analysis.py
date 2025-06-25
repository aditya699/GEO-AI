"""
🔍 What is MNDWI?
MNDWI is a satellite-based index that helps us detect water bodies (like ponds, lakes, rivers, or waterlogged areas) in satellite images.

🧪 Formula:
MNDWI = (Green - SWIR) / (Green + SWIR)

Where:
Green = Band B3
SWIR = Shortwave Infrared = Band B11

🧠 Why this works:
Light Band	Behavior Over Water
Green (B3)	Water reflects green light well
SWIR (B11)	Water absorbs SWIR (so reflectance is low)

That means:
If an area reflects green but not SWIR → it's probably water.
MNDWI becomes high (closer to 1) for water.
For land or built-up areas → MNDWI will be low or negative.

🎯 How to Use It:
MNDWI > 0.3 → Likely water
MNDWI ≈ 0 → Uncertain (could be wet soil or shadow)
MNDWI < 0 → Definitely non-water (e.g., buildings, dry land)
"""



import numpy as np
import rasterio
import matplotlib.pyplot as plt

# Define file paths
jan_2020_path = "polygon/sector14_2020-01-30.tif"
jan_2025_path = "polygon/sector14_2025-01-28.tif"

# Function to compute MNDWI
def compute_mndwi(tif_path):
    with rasterio.open(tif_path) as src:
        green = src.read(1).astype("float32")  # Band 1 = Green (B3)
        swir = src.read(2).astype("float32")   # Band 2 = SWIR  (B11)

    denom = green + swir
    denom[denom == 0] = 0.0001  # avoid division by zero
    return (green - swir) / denom

# Compute MNDWI for both dates
mndwi_jan_2020 = compute_mndwi(jan_2020_path)
mndwi_jan_2025 = compute_mndwi(jan_2025_path)

print("Average MNDWI - Jan 2020:", round(mndwi_jan_2020.mean(), 4))
print("Average MNDWI - Jan 2025:", round(mndwi_jan_2025.mean(), 4))
print("Change:", round(mndwi_jan_2025.mean() - mndwi_jan_2020.mean(), 4))