'''
This script will extract images of sector 14 using google earth engine.
'''
import ee

# Initialize Earth Engine with your project ID
ee.Initialize(project='chatbot-for-enterprise-445604')
# Define the bounding box for Sector 14, Gurugram
sector14_bbox = ee.Geometry.Rectangle([77.018, 28.458, 77.030, 28.469])

# Filter Sentinel-2 image for January 2024
sentinel_jan = (
    ee.ImageCollection("COPERNICUS/S2_SR")  # Sentinel-2 Level 2A surface reflectance
    .filterBounds(sector14_bbox)            # Only images that intersect Sector 14
    .filterDate("2024-01-01", "2024-01-20")  # Around mid-Jan
    .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 10))  # Only low-cloud images
    .sort("CLOUDY_PIXEL_PERCENTAGE")        # Lowest-cloud image first
    .first()                                # Get just 1 image
)
# Select RGB bands (B4=Red, B3=Green, B2=Blue) and clip to bounding box
rgb_jan = (
    sentinel_jan
    .select(['B4', 'B3', 'B2'])   # Only keep RGB bands
    .clip(sector14_bbox)         # Clip image to Sector 14 area
)
# Export image to your Google Drive as GeoTIFF
task = ee.batch.Export.image.toDrive(
    image=rgb_jan,
    description='sector14_jan_rgb',
    folder='earth_engine',          # This folder will appear in your Google Drive
    fileNamePrefix='sector14_jan',  # File will be sector14_jan.tif
    scale=10,                       # Sentinel-2 resolution = 10 meters/pixel
    region=sector14_bbox,          # Export only our bounding box
    fileFormat='GeoTIFF'
)

task.start()
