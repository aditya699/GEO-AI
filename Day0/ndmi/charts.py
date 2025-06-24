import numpy as np
import rasterio
import matplotlib.pyplot as plt

# Define file paths
dec_path = "polygon_swir_nir/sector14_2023-12-05.tif"
june_path = "polygon_swir_nir/sector14_2024-06-12.tif"

# Function to compute NDMI
def compute_ndmi(tif_path):
    with rasterio.open(tif_path) as src:
        swir = src.read(1).astype("float32")  # Band 1 = SWIR (B11)
        nir = src.read(2).astype("float32")   # Band 2 = NIR  (B8)

    denom = nir + swir
    denom[denom == 0] = 0.0001  # avoid division by zero
    return (nir - swir) / denom

# Compute NDMI for both dates
ndmi_dec = compute_ndmi(dec_path)
ndmi_june = compute_ndmi(june_path)

# Plot side-by-side with proper colorbar positioning
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
vmin, vmax = -1, 1

im1 = ax1.imshow(ndmi_dec, cmap="gray", vmin=vmin, vmax=vmax)
ax1.set_title("NDMI - Dec 2023")
ax1.axis("off")

im2 = ax2.imshow(ndmi_june, cmap="gray", vmin=vmin, vmax=vmax)
ax2.set_title("NDMI - June 2024")
ax2.axis("off")

# Create colorbar with proper spacing
plt.tight_layout()
cbar = fig.colorbar(im2, ax=[ax1, ax2], shrink=0.8, aspect=20, pad=0.02)
cbar.set_label("NDMI Value", rotation=270, labelpad=15)

plt.show()