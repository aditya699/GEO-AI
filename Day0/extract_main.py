"""
NOTE:
1.We will using Google Earth Engine API to extract the images of sector 14, Gurugram.

2.We used https://overpass-turbo.eu/ open source tool to find the exact coordinates of sector 14, Gurugram.
Query Used:
[out:json][timeout:25];
area[name="Gurugram"]->.searchArea;
(
  relation["name"="Sector 14"](area.searchArea);
);
out body;
>;
out skel qt;

3.What is Sentinel-2?
Sentinel-2 is a satellite mission run by ESA (European Space Agency).

It takes high-resolution images of the Earth every 5 days.

Designed for:

Land use monitoring

Urban development

Vegetation and water tracking

Has multiple bands:

RGB (like a photo)

Infrared (for vegetation/heat)

Cloud detection, moisture, etc.

4.This is starting point to we want to learn how to extarct data and start working we may be able to use 13 bands later when we will do core ai ml stuff
"""
import ee
from dotenv import load_dotenv
import os
import json
import datetime
import time

load_dotenv()

# Initialize Earth Engine with your project ID
ee.Initialize(project=os.getenv('PROJECT_ID'))

"""
NOTE : 
1.We have used this the json file to get the exact coordinates of sector 14, Gurugram.
2.For now we are using the hardcoded coordinates.Since our area of interest in sector 14, Gurugram.

# We need to find exact coordinates of sector 14, Gurugram.
# with open('sector14.geojson') as f:
#     geojson = json.load(f)

# sector14_polygon = ee.Geometry.Polygon(geojson['features'][0]['geometry']['coordinates'])
# print(sector14_polygon)
"""
sector14_geom = ee.Geometry.Polygon([
  [
    [77.0439461, 28.4684192],
    [77.0458308, 28.4697483],
    [77.0485234, 28.4707445],
    [77.0485843, 28.470762],
    [77.0492354, 28.4710512],
    [77.050005, 28.471356],
    [77.0512071, 28.4717616],
    [77.0524742, 28.4722068],
    [77.0535205, 28.4726016],
    [77.0554358, 28.4734241],
    [77.0534223, 28.4758626],
    [77.0499937, 28.4800444],
    [77.0494004, 28.4814748],
    [77.0490452, 28.4809201],
    [77.0463887, 28.4778778],
    [77.0429769, 28.47403],
    [77.0378622, 28.4683624],
    [77.033792, 28.4638508],
    [77.0369056, 28.4647495],
    [77.037865, 28.465271],
    [77.0413474, 28.467164],
    [77.0439461, 28.4684192]
  ]
])

print("Searching for Sentinel-2 images for December 2023...")

"""
NOTE:
1.We are using the Sentinel-2_SR_HARMONIZED collection to get the images., for December 2023.
2.When satellites take pictures, clouds block the view of Earth's surface.
3.Sentinel-2 stores a property called CLOUDY_PIXEL_PERCENTAGE
4.It's the % of the image that's covered by clouds.
5.Example:
5% = mostly clear
70% = very cloudy
"""

collection_dec = (
    ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
    .filterBounds(sector14_geom)
    .filterDate("2023-12-01", "2023-12-31")
    .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 30))
)

print(f"Images found: {collection_dec.size().getInfo()}")

#Pick the image with the least cloud cover
sentinel_dec = collection_dec.sort("CLOUDY_PIXEL_PERCENTAGE").first()
image_info = sentinel_dec.getInfo()

#There is a chance that no image is found. so for that we may be need to relax the filters.or reevaluate the filters.
if image_info is None:
    print("No image found. Try relaxing filters or changing dates.")
    exit()


# Get the image's timestamp (in milliseconds)
timestamp_ms = image_info['properties']['system:time_start']

# Convert to human-readable date
date_used = datetime.datetime.fromtimestamp(timestamp_ms / 1000).strftime('%Y-%m-%d')
cloud_pct = image_info['properties']['CLOUDY_PIXEL_PERCENTAGE']

print(f"Using image from: {date_used}")
print(f"Cloud coverage: {cloud_pct}%")


"""
📌 Why this step?
Sentinel-2 images contain 13 bands, including infrared, water vapor, etc.
But for human-viewable images, we only need RGB bands:

Band Name	Meaning	Resolution
B4	Red	10m
B3	Green	10m
B2	Blue	10m

We also clip the image to our polygon, so we don't download the entire tile (which may be large or include other areas).
"""
# Select RGB bands and clip to Sector 14
rgb_dec = (
    sentinel_dec
    .select(['B4', 'B3', 'B2'])  # Red, Green, Blue
    .clip(sector14_geom)        # Clip to exact boundary
)
"""
🧠 Explanation:
.multiply(0.0001) converts raw values (e.g., 5000) to ~0.5

Then .multiply(255) converts to RGB range

.uint8() ensures it's exportable as a standard image
"""
# Scale reflectance values to 0–255 for visualization
rgb_dec_scaled = rgb_dec.multiply(0.0001).multiply(255).uint8()

# Export the RGB image to Google Drive
task = ee.batch.Export.image.toDrive(
    image=rgb_dec_scaled,
    description='sector14_dec2023_export',
    folder='earth_engine',
    fileNamePrefix=f'sector14_{date_used}',
    scale=10,  # 10m per pixel
    region=sector14_geom,
    fileFormat='GeoTIFF',
    maxPixels=1e9
)

print("Starting export task...")
task.start()

#Code to tract progress of the task
print("Monitoring task status...")
while task.active():
    print(f"Task status: {task.status()['state']}")
    time.sleep(5)

final_status = task.status()
print(f"Final task status: {final_status['state']}")

if final_status['state'] == 'COMPLETED':
    print("✅ Export completed successfully!")
elif final_status['state'] == 'FAILED':
    print("❌ Export failed!")
    print(f"Error: {final_status.get('error_message', 'No error message')}")
