import numpy as np
import rasterio
import matplotlib.pyplot as plt

# Define file paths
dec_path = "polygon_swir_nir/sector14_2020-01-30.tif"
june_path = "polygon_swir_nir/sector14_2025-01-28.tif"

# Function to compute NDBI
def compute_ndbi(tif_path):
    with rasterio.open(tif_path) as src:
        swir = src.read(1).astype("float32")  # Band 1 = SWIR (B11)
        nir = src.read(2).astype("float32")   # Band 2 = NIR  (B8)

    denom = swir + nir
    denom[denom == 0] = 0.0001  # avoid division by zero
    return (swir - nir) / denom

# Compute NDBI for both dates
ndbi_jan_2020 = compute_ndbi(dec_path)
ndbi_jan_2025 = compute_ndbi(june_path)

# Plot side-by-side with proper colorbar positioning
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
vmin, vmax = -1, 1

im1 = ax1.imshow(ndbi_jan_2020, cmap="gray", vmin=vmin, vmax=vmax)
ax1.set_title("NDBI - Jan 2020")
ax1.axis("off")

im2 = ax2.imshow(ndbi_jan_2025, cmap="gray", vmin=vmin, vmax=vmax)
ax2.set_title("NDBI - Jan 2025")
ax2.axis("off") 

# Create colorbar with proper spacing
plt.tight_layout()
cbar = fig.colorbar(im2, ax=[ax1, ax2], shrink=0.8, aspect=20, pad=0.02)
cbar.set_label("NDBI Value", rotation=270, labelpad=15)

plt.show()