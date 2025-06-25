"""
NDMI (Normalized Difference Moisture Index)
What it tells you:
How much moisture is present in vegetation and soil.

High NDMI (~0.4 to 1.0): High moisture content (wet vegetation, irrigated areas)
Low NDMI (~-0.5 to 0.2): Low moisture content (dry vegetation, bare soil)
Negative NDMI: Very dry areas or water bodies

Formula: NDMI = (NIR - SWIR) / (NIR + SWIR)
Because water absorbs SWIR strongly but reflects NIR, so wet areas have higher NIR than SWIR

NDVI (Normalized Difference Vegetation Index)
What it tells you:
How much green, healthy vegetation is present in an area.

High NDVI (~0.6 to 1.0): Dense vegetation (e.g., forests, crops)
Low NDVI (~0 to 0.2): Bare soil, roads, buildings
Negative NDVI: Water or clouds

Formula: NDVI = (NIR - Red) / (NIR + Red)
Because plants reflect NIR and absorb red (photosynthesis)
"""



import numpy as np
import rasterio
import matplotlib.pyplot as plt

# Define file paths
dec_path = "polygon_swir_nir/sector14_2020-01-30.tif"
june_path = "polygon_swir_nir/sector14_2025-01-28.tif"

# Function to compute NDMI
def compute_ndmi(tif_path):
    with rasterio.open(tif_path) as src:
        swir = src.read(1).astype("float32")  # Band 1 = SWIR (B11)
        nir = src.read(2).astype("float32")   # Band 2 = NIR  (B8)

    denom = nir + swir
    denom[denom == 0] = 0.0001  # avoid division by zero
    return (nir - swir) / denom

# Compute NDMI for both dates
ndmi_jan_2020 = compute_ndmi(dec_path)
ndmi_jan_2025 = compute_ndmi(june_path)

print("Average NDMI - Jan 2020:", round(ndmi_jan_2020.mean(), 4))
print("Average NDMI - Jan 2025:", round(ndmi_jan_2025.mean(), 4))
print("Change:", round(ndmi_jan_2025.mean() - ndmi_jan_2020.mean(), 4))