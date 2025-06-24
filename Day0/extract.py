"""
NOTE:
1.We will using Google Earth Engine API to extract the images of sector 14, Gurugram.
"""


import ee
from dotenv import load_dotenv
import os
load_dotenv()

# Initialize Earth Engine with your project ID
ee.Initialize(project=os.getenv('PROJECT_ID'))

# Define the bounding box for Sector 14, Gurugram
sector14_bbox = ee.Geometry.Rectangle([77.015, 28.455, 77.035, 28.472])

print("Searching for Sentinel-2 images using updated collection...")

# Use the new Sentinel-2 collection (non-deprecated)
collection = (
    ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")  # Updated collection
    .filterBounds(sector14_bbox)
    .filterDate("2024-01-01", "2024-01-31")
    .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 30))
)

print(f"Number of images found: {collection.size().getInfo()}")

# Get the best image (least cloudy)
sentinel_jan = collection.sort("CLOUDY_PIXEL_PERCENTAGE").first()

# Check if we found any images
image_info = sentinel_jan.getInfo()
if image_info is None:
    print("No images found! Trying with more lenient filters...")
    
    # Try with wider date range and more lenient cloud filter
    collection_backup = (
        ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
        .filterBounds(sector14_bbox)
        .filterDate("2023-12-01", "2024-02-29")
        .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 50))
    )
    
    print(f"Backup search found: {collection_backup.size().getInfo()} images")
    sentinel_jan = collection_backup.sort("CLOUDY_PIXEL_PERCENTAGE").first()

# Verify we have an image before proceeding
image_check = sentinel_jan.getInfo()
if image_check is None:
    print("ERROR: Still no images found. Check your coordinates and date range.")
    exit()

# Convert timestamp to readable date
import datetime
timestamp_ms = image_check['properties']['system:time_start']
date_used = datetime.datetime.fromtimestamp(timestamp_ms/1000).strftime('%Y-%m-%d')

print(f"Using image from: {date_used}")
print(f"Cloud coverage: {image_check['properties']['CLOUDY_PIXEL_PERCENTAGE']}%")

# Select RGB bands and clip to bounding box
rgb_jan = (
    sentinel_jan
    .select(['B4', 'B3', 'B2'])   # RGB bands
    .clip(sector14_bbox)
)

# Apply scaling for better visualization
rgb_jan_scaled = rgb_jan.multiply(0.0001).multiply(255).uint8()

# Export image to Google Drive
task = ee.batch.Export.image.toDrive(
    image=rgb_jan_scaled,
    description='sector14_updated_collection',
    folder='earth_engine',
    fileNamePrefix=f'sector14_{date_used}',
    scale=10,
    region=sector14_bbox,
    fileFormat='GeoTIFF',
    maxPixels=1e9
)

print("Starting export task...")
task.start()
print(f"Task started with ID: {task.id}")
print("Check your Google Drive 'earth_engine' folder for the exported image.")

# Monitor task status
import time
print("Monitoring task status...")
while task.active():
    status = task.status()['state']
    print(f"Task status: {status}")
    if status in ['COMPLETED', 'FAILED']:
        break
    time.sleep(5)

final_status = task.status()
print(f"Final task status: {final_status['state']}")
if final_status['state'] == 'COMPLETED':
    print("✅ Export completed successfully!")
    if 'destination_uris' in final_status:
        print(f"📁 Google Drive link: {final_status['destination_uris'][0]}")
elif final_status['state'] == 'FAILED':
    print("❌ Export failed!")
    if 'error_message' in final_status:
        print(f"Error: {final_status['error_message']}")