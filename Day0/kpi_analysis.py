"""
NDVI Analysis for Satellite Imagery

This module performs Normalized Difference Vegetation Index (NDVI) analysis on satellite imagery.

What is NDVI?
    NDVI (Normalized Difference Vegetation Index) is a metric that measures vegetation health
    and density by analyzing the difference between near-infrared and red light reflectance.

Key Concepts:
    • NDVI values range from -1 to +1
    • Higher values indicate healthier, denser vegetation
    • Lower values indicate sparse vegetation, soil, or water

How NDVI Works:
    Plants have unique spectral properties:
    - Absorb red light for photosynthesis
    - Strongly reflect near-infrared (NIR) light
    
    NDVI Classification:
    - Healthy vegetation: NDVI ≈ +0.6 to +0.9 (low red + high NIR)
    - Dead plants/soil: NDVI ≈ 0 (similar red & NIR)
    - Urban areas/water: NDVI ≈ -1 to 0 (high red or low NIR)

Data Structure:
    From Earth Engine exports, .tif files contain:
    - Band 1: Red (B4) - measures red light reflectance
    - Band 2: NIR (B8) - measures near-infrared reflectance

Formula:
    NDVI = (NIR - Red) / (NIR + Red)
"""
 
import numpy as np
import rasterio
import matplotlib.pyplot as plt

def compute_ndvi(path):
    with rasterio.open(path) as src:
        red = src.read(1).astype("float32")
        nir = src.read(2).astype("float32")
    denom = nir + red
    denom[denom == 0] = 0.0001  # avoid div by zero
    return (nir - red) / denom

# Compute NDVI for both dates
ndvi_dec = compute_ndvi("polygon_red_nir/sector14_2023-12-05.tif")
ndvi_jun = compute_ndvi("polygon_red_nir/sector14_2024-06-12.tif")

# Plot side-by-side with proper colorbar positioning
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

vmin, vmax = -1, 1

axes[0].imshow(ndvi_dec, cmap="RdYlGn", vmin=vmin, vmax=vmax)
axes[0].set_title("NDVI - Dec 2023")
axes[0].axis("off")

im = axes[1].imshow(ndvi_jun, cmap="RdYlGn", vmin=vmin, vmax=vmax)
axes[1].set_title("NDVI - June 2024")
axes[1].axis("off")

# Create colorbar with proper spacing
plt.tight_layout()
cbar = fig.colorbar(im, ax=axes.ravel().tolist(), shrink=0.8, aspect=20, pad=0.02)
cbar.set_label("NDVI", rotation=270, labelpad=15)

plt.show()