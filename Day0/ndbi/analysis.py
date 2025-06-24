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
dec_path = "polygon_swir_nir/sector14_2023-12-05.tif"
june_path = "polygon_swir_nir/sector14_2024-06-12.tif"

# Function to compute NDBI
def compute_ndbi(tif_path):
    with rasterio.open(tif_path) as src:
        swir = src.read(1).astype("float32")  # Band 1 = SWIR (B11)
        nir = src.read(2).astype("float32")   # Band 2 = NIR  (B8)

    denom = swir + nir
    denom[denom == 0] = 0.0001  # avoid division by zero
    return (swir - nir) / denom

# Compute NDBI for both dates
ndbi_dec = compute_ndbi(dec_path)
ndbi_june = compute_ndbi(june_path)

print("Average NDBI - Dec 2023:", round(ndbi_dec.mean(), 4))
print("Average NDBI - June 2024:", round(ndbi_june.mean(), 4))
print("Change:", round(ndbi_june.mean() - ndbi_dec.mean(), 4))