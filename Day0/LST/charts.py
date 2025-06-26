import numpy as np
import rasterio
import matplotlib.pyplot as plt

# Define file paths for LST images
jan2022_path = "lst_2022-01-30.tif"
jan2025_path = "lst_2025-01-29.tif" 

# Function to load and debug LST image
def load_and_debug_lst_image(path):
    with rasterio.open(path) as src:
        lst_raw = src.read(1).astype("float32")
        print(f"\nDebugging {path}:")
        print(f"Raw data range: {np.min(lst_raw)} to {np.max(lst_raw)}")
        print(f"Raw data shape: {lst_raw.shape}")
        print(f"Unique values sample: {np.unique(lst_raw)[:10]}")
        print(f"Number of zero values: {np.sum(lst_raw == 0)}")
        print(f"Number of non-zero values: {np.sum(lst_raw != 0)}")
        
        # Handle no-data values (65535 is common no-data value for uint16)
        lst_celsius = lst_raw.copy()
        
        # Replace no-data values with NaN
        lst_celsius = np.where(lst_celsius == 65535, np.nan, lst_celsius)
        lst_celsius = np.where(lst_celsius == 0, np.nan, lst_celsius)
        
        # Apply scaling (divide by 10 as per your export code)
        lst_celsius = lst_celsius / 10.0
        
        # Check if we have any valid data
        valid_data = lst_celsius[~np.isnan(lst_celsius)]
        if len(valid_data) > 0:
            print(f"Applied /10 scaling and removed no-data values")
            print(f"Final temperature range: {np.nanmin(lst_celsius):.1f}°C to {np.nanmax(lst_celsius):.1f}°C")
            print(f"Valid pixels: {len(valid_data)}")
        else:
            print("WARNING: No valid temperature data found!")
            # Try different approach - maybe data is stored differently
            lst_celsius = lst_raw.copy()
            # Remove extreme values
            lst_celsius = np.where((lst_celsius == 0) | (lst_celsius >= 60000), np.nan, lst_celsius)
            lst_celsius = lst_celsius / 10.0
            valid_data = lst_celsius[~np.isnan(lst_celsius)]
            if len(valid_data) > 0:
                print(f"Alternative processing - Final range: {np.nanmin(lst_celsius):.1f}°C to {np.nanmax(lst_celsius):.1f}°C")
        
    return lst_celsius

# Load both LST images with debugging
lst_2022 = load_and_debug_lst_image(jan2022_path)
lst_2025 = load_and_debug_lst_image(jan2025_path)

# Compute temperature range for consistent color scale (excluding NaN)
vmin = min(np.nanmin(lst_2022), np.nanmin(lst_2025))
vmax = max(np.nanmax(lst_2022), np.nanmax(lst_2025))

print(f"\nCombined temperature range for visualization: {vmin:.1f}°C to {vmax:.1f}°C")

# Plot side-by-side
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

im1 = ax1.imshow(lst_2022, cmap="inferno", vmin=vmin, vmax=vmax)
ax1.set_title("LST - Jan 2022")
ax1.axis("off")

im2 = ax2.imshow(lst_2025, cmap="inferno", vmin=vmin, vmax=vmax)
ax2.set_title("LST - Jan 2025")
ax2.axis("off")

# Add colorbar with proper temperature units
plt.tight_layout()
cbar = fig.colorbar(im2, ax=[ax1, ax2], shrink=0.8, aspect=20, pad=0.02)
cbar.set_label("Temperature (°C)", rotation=270, labelpad=15)

plt.show()