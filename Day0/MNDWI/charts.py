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

# Plot side-by-side with proper colorbar positioning
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
vmin, vmax = -1, 1

im1 = ax1.imshow(mndwi_jan_2020, cmap="gray", vmin=vmin, vmax=vmax)
ax1.set_title("MNDWI - Jan 2020")
ax1.axis("off")

im2 = ax2.imshow(mndwi_jan_2025, cmap="gray", vmin=vmin, vmax=vmax)
ax2.set_title("MNDWI - Jan 2025")
ax2.axis("off")

# Create colorbar with proper spacing
plt.tight_layout()
cbar = fig.colorbar(im2, ax=[ax1, ax2], shrink=0.8, aspect=20, pad=0.02)
cbar.set_label("MNDWI Value", rotation=270, labelpad=15)

plt.show()