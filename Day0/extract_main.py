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
import logging

# Setup logging with UTF-8 encoding to handle Unicode characters
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('earth_engine_export.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def initialize_earth_engine():
    """Initialize Earth Engine with project ID from environment variables"""
    load_dotenv()
    logger.info("Loading environment variables...")
    
    project_id = os.getenv('PROJECT_ID')
    if not project_id:
        logger.error("PROJECT_ID not found in environment variables")
        raise ValueError("PROJECT_ID not found in environment variables")
    
    logger.info(f"Initializing Earth Engine with project ID: {project_id}")
    ee.Initialize(project=project_id)
    logger.info("Earth Engine initialized successfully")

def get_sector14_geometry():
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
    logger.info("Creating Sector 14 geometry...")
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
    logger.info("Sector 14 geometry created successfully")
    return sector14_geom

def get_user_dates():
    """Get start and end dates from user input"""
    logger.info("Getting date range from user...")
    
    while True:
        try:
            start_date = input("Enter start date (YYYY-MM-DD): ").strip()
            datetime.datetime.strptime(start_date, '%Y-%m-%d')
            break
        except ValueError:
            logger.warning("Invalid start date format. Please use YYYY-MM-DD format.")
            print("Invalid date format. Please use YYYY-MM-DD format.")
    
    while True:
        try:
            end_date = input("Enter end date (YYYY-MM-DD): ").strip()
            datetime.datetime.strptime(end_date, '%Y-%m-%d')
            break
        except ValueError:
            logger.warning("Invalid end date format. Please use YYYY-MM-DD format.")
            print("Invalid date format. Please use YYYY-MM-DD format.")
    
    logger.info(f"Date range selected: {start_date} to {end_date}")
    return start_date, end_date

def search_sentinel_images(geometry, start_date, end_date):
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
    logger.info(f"Searching for Sentinel-2 images from {start_date} to {end_date}...")
    
    collection = (
        ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
        .filterBounds(geometry)
        .filterDate(start_date, end_date)
        .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 30))
    )

    image_count = collection.size().getInfo()
    logger.info(f"Images found: {image_count}")

    #Pick the image with the least cloud cover
    sentinel_image = collection.sort("CLOUDY_PIXEL_PERCENTAGE").first()
    image_info = sentinel_image.getInfo()

    #There is a chance that no image is found. so for that we may be need to relax the filters.or reevaluate the filters.
    if image_info is None:
        logger.warning("No image found. Try relaxing filters or changing dates.")
        print("No image found. Try relaxing filters or changing dates.")
        exit()

    return sentinel_image, image_info

def get_image_metadata(image_info):
    """Extract and log image metadata"""
    # Get the image's timestamp (in milliseconds)
    timestamp_ms = image_info['properties']['system:time_start']

    # Convert to human-readable date
    date_used = datetime.datetime.fromtimestamp(timestamp_ms / 1000).strftime('%Y-%m-%d')
    cloud_pct = image_info['properties']['CLOUDY_PIXEL_PERCENTAGE']

    logger.info(f"Using image from: {date_used}")
    logger.info(f"Cloud coverage: {cloud_pct}%")
    
    return date_used, cloud_pct

def process_rgb_image(sentinel_image, geometry):
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
    logger.info("Processing RGB bands...")
    
    # Select RGB bands and clip to Sector 14
    rgb_image = (
        sentinel_image
        .select(['B4', 'B3', 'B2'])  # Red, Green, Blue
        .clip(geometry)        # Clip to exact boundary
    )
    
    """
    🧠 Explanation:
    .multiply(0.0001) converts raw values (e.g., 5000) to ~0.5

    Then .multiply(255) converts to RGB range

    .uint8() ensures it's exportable as a standard image
    """
    # Scale reflectance values to 0–255 for visualization
    '''
    #  Prepare RGB image for export with brightness correction

    rgb_scaled = (
        rgb_image
        .multiply(0.0001)   # Convert raw Sentinel-2 pixel values (e.g. 5000) to reflectance scale (0.0-1.0)
        .pow(0.5)           # Gamma correction (square root) to brighten darker areas and improve visual contrast
        .multiply(255)      # Scale reflectance (0-1) to standard 8-bit image values (0-255)
        .uint8()            # Convert to unsigned 8-bit integers, required for exportable RGB image formats
    )

    '''
    rgb_scaled = rgb_image.multiply(0.0001).pow(0.5).multiply(255).uint8()
    
    logger.info("RGB image processed successfully")
    return rgb_scaled

def export_image_to_drive(image, date_used, geometry):
    """Export the processed image to Google Drive"""
    logger.info("Setting up export task...")
    
    # Export the RGB image to Google Drive
    task = ee.batch.Export.image.toDrive(
        image=image,
        description='sector14_export',
        folder='earth_engine',
        fileNamePrefix=f'sector14_{date_used}',
        scale=10,  # 10m per pixel
        region=geometry,
        fileFormat='GeoTIFF',
        maxPixels=1e9
    )

    logger.info("Starting export task...")
    task.start()
    
    return task

def monitor_export_task(task):
    """Monitor the export task progress"""
    #Code to tract progress of the task
    logger.info("Monitoring task status...")
    while task.active():
        status = task.status()['state']
        logger.info(f"Task status: {status}")
        time.sleep(5)

    final_status = task.status()
    logger.info(f"Final task status: {final_status['state']}")

    if final_status['state'] == 'COMPLETED':
        logger.info("Export completed successfully!")
        print("Export completed successfully!")
    elif final_status['state'] == 'FAILED':
        error_msg = final_status.get('error_message', 'No error message')
        logger.error(f"Export failed! Error: {error_msg}")
        print("Export failed!")
        print(f"Error: {error_msg}")

def main():
    """Main function to orchestrate the satellite image extraction process"""
    try:
        logger.info("Starting satellite image extraction process...")
        
        # Initialize Earth Engine
        initialize_earth_engine()
        
        # Get geometry for Sector 14
        sector14_geom = get_sector14_geometry()
        
        # Get date range from user
        start_date, end_date = get_user_dates()
        
        # Search for Sentinel-2 images
        sentinel_image, image_info = search_sentinel_images(sector14_geom, start_date, end_date)
        
        # Get image metadata
        date_used, cloud_pct = get_image_metadata(image_info)
        
        # Process RGB image
        rgb_scaled = process_rgb_image(sentinel_image, sector14_geom)
        
        # Export image to Google Drive
        task = export_image_to_drive(rgb_scaled, date_used, sector14_geom)
        
        # Monitor export progress
        monitor_export_task(task)
        
        logger.info("Process completed successfully!")
        
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        print(f"An error occurred: {str(e)}")
        raise

if __name__ == "__main__":
    main()
