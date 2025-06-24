import rasterio
import numpy as np
import matplotlib.pyplot as plt

# File paths
dec_path = "polygon/sector14_2023-12-05.tif"
june_path = "polygon/sector14_2024-06-12.tif"

def read_rgb_image(path):
    with rasterio.open(path) as src:
        # Read the first 3 bands (RGB)
        red = src.read(1)
        green = src.read(2)
        blue = src.read(3)
        
        # Stack and normalize to 0–1 for display
        rgb = np.stack([red, green, blue], axis=-1).astype(np.float32)
        rgb /= 255.0  # scale since we exported as uint8
        return rgb

# Read both images
img_dec = read_rgb_image(dec_path)
img_june = read_rgb_image(june_path)

# Plot
fig, axes = plt.subplots(1, 2, figsize=(14, 7))
axes[0].imshow(img_dec)
axes[0].set_title("Sector 14 – Dec 2023")
axes[0].axis('off')

axes[1].imshow(img_june)
axes[1].set_title("Sector 14 – June 2024")
axes[1].axis('off')

plt.tight_layout()
plt.show()
