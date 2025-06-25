"""
NDVI (Normalized Difference Vegetation Index)
What it tells you:
How much green, healthy vegetation is present in an area.

High NDVI (~0.6 to 1.0): Dense vegetation (e.g., forests, crops)
Low NDVI (~0 to 0.2): Bare soil, roads, buildings
Negative NDVI: Water or clouds

Formula: NDVI = (NIR - Red) / (NIR + Red)
Because plants reflect NIR and absorb red (photosynthesis)

NDBI (Normalized Difference Built-up Index)
What it tells you:
How much built-up / urban / concrete structure exists.

High NDBI (~0.3+): Concrete, rooftops, roads
Low NDBI (~-0.3): Vegetation or water

Formula: NDBI = (SWIR - NIR) / (SWIR + NIR)
Because concrete reflects SWIR more than NIR.
"""



import numpy as np
import rasterio
import matplotlib.pyplot as plt

# Define file paths
jan_2020_path = "polygon_swir_nir/sector14_2020-01-30.tif"
jan_2025_path = "polygon_swir_nir/sector14_2025-01-28.tif"

# Function to compute NDBI
def compute_ndbi(tif_path):
    with rasterio.open(tif_path) as src:
        swir = src.read(1).astype("float32")  # Band 1 = SWIR (B11)
        nir = src.read(2).astype("float32")   # Band 2 = NIR  (B8)

    denom = swir + nir
    denom[denom == 0] = 0.0001  # avoid division by zero
    return (swir - nir) / denom

# Compute NDBI for both dates
ndbi_jan_2020 = compute_ndbi(jan_2020_path)
ndbi_jan_2025 = compute_ndbi(jan_2025_path)

print("Average NDBI - Jan 2020:", round(ndbi_jan_2020.mean(), 4))
print("Average NDBI - Jan 2025:", round(ndbi_jan_2025.mean(), 4))
print("Change:", round(ndbi_jan_2025.mean() - ndbi_jan_2020.mean(), 4))