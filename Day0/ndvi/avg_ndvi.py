import numpy as np
import rasterio

def compute_avg_ndvi(path):
    with rasterio.open(path) as src:
        red = src.read(1).astype("float32")
        nir = src.read(2).astype("float32")

    denom = nir + red
    denom[denom == 0] = 0.0001
    ndvi = (nir - red) / denom

    # Mask invalid values (optional)
    ndvi = np.where((ndvi >= -1) & (ndvi <= 1), ndvi, np.nan)

    # Compute mean NDVI, ignoring nan
    return np.nanmean(ndvi)

# dec_ndvi = compute_avg_ndvi("polygon_red_nir/sector14_2023-12-05.tif")
# jun_ndvi = compute_avg_ndvi("polygon_red_nir/sector14_2024-06-12.tif")

jan_ndvi_2020 = compute_avg_ndvi("../ndvi_r_infred/sector14_2020-01-30.tif")
jan_ndvi_2025 = compute_avg_ndvi("../ndvi_r_infred/sector14_2025-01-28.tif")


print(f"Average NDVI - Jan 2020: {jan_ndvi_2020:.4f}")
print(f"Average NDVI - Jan 2025: {jan_ndvi_2025:.4f}")
print(f"Change: {jan_ndvi_2025 - jan_ndvi_2020:.4f}")
