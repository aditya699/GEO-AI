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

dec_ndvi = compute_avg_ndvi("polygon_red_nir/sector14_2023-12-05.tif")
jun_ndvi = compute_avg_ndvi("polygon_red_nir/sector14_2024-06-12.tif")

print(f"Average NDVI - Dec 2023: {dec_ndvi:.4f}")
print(f"Average NDVI - June 2024: {jun_ndvi:.4f}")
print(f"Change: {jun_ndvi - dec_ndvi:.4f}")
