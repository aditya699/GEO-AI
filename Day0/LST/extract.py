import ee
from dotenv import load_dotenv
import os
import datetime
import time
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('earth_engine_lst_export.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def initialize_earth_engine():
    load_dotenv()
    project_id = os.getenv('PROJECT_ID')
    if not project_id:
        raise ValueError("PROJECT_ID not found in environment variables")
    ee.Initialize(project=project_id)
    logger.info("Earth Engine initialized with project ID")

def get_sector14_geometry():
    return ee.Geometry.Polygon([
        [
            [77.0439461, 28.4684192], [77.0458308, 28.4697483], [77.0485234, 28.4707445],
            [77.0485843, 28.470762], [77.0492354, 28.4710512], [77.050005, 28.471356],
            [77.0512071, 28.4717616], [77.0524742, 28.4722068], [77.0535205, 28.4726016],
            [77.0554358, 28.4734241], [77.0534223, 28.4758626], [77.0499937, 28.4800444],
            [77.0494004, 28.4814748], [77.0490452, 28.4809201], [77.0463887, 28.4778778],
            [77.0429769, 28.47403], [77.0378622, 28.4683624], [77.033792, 28.4638508],
            [77.0369056, 28.4647495], [77.037865, 28.465271], [77.0413474, 28.467164],
            [77.0439461, 28.4684192]
        ]
    ])

def get_user_dates():
    while True:
        try:
            start_date = input("Enter start date (YYYY-MM-DD): ").strip()
            datetime.datetime.strptime(start_date, '%Y-%m-%d')
            break
        except ValueError:
            print("Invalid format.")
    while True:
        try:
            end_date = input("Enter end date (YYYY-MM-DD): ").strip()
            datetime.datetime.strptime(end_date, '%Y-%m-%d')
            break
        except ValueError:
            print("Invalid format.")
    return start_date, end_date

def search_landsat_images(geometry, start_date, end_date):
    collection = (
        ee.ImageCollection("LANDSAT/LC08/C02/T1_L2")
        .filterBounds(geometry)
        .filterDate(start_date, end_date)
        .filter(ee.Filter.lt("CLOUD_COVER", 30))
    )
    sentinel_image = collection.sort("CLOUD_COVER").first()
    if sentinel_image.getInfo() is None:
        print("No image found.")
        exit()
    return sentinel_image

def process_lst_image(image, geometry):
    lst_kelvin = image.select("ST_B10").clip(geometry)
    lst_celsius = lst_kelvin.subtract(273.15)
    lst_scaled = lst_celsius.multiply(10).uint16()
    return lst_scaled

def export_image_to_drive(image, date_used, geometry):
    task = ee.batch.Export.image.toDrive(
        image=image,
        description='lst_export',
        folder='earth_engine',
        fileNamePrefix=f'lst_{date_used}',
        scale=30,
        region=geometry,
        fileFormat='GeoTIFF',
        maxPixels=1e9
    )
    task.start()
    return task

def monitor_export_task(task):
    while task.active():
        print(f"Task status: {task.status()['state']}")
        time.sleep(5)
    print(f"Final status: {task.status()['state']}")

def main():
    initialize_earth_engine()
    geometry = get_sector14_geometry()
    start_date, end_date = get_user_dates()
    image = search_landsat_images(geometry, start_date, end_date)
    date_used = image.date().format("YYYY-MM-dd").getInfo()
    lst_image = process_lst_image(image, geometry)
    task = export_image_to_drive(lst_image, date_used, geometry)
    monitor_export_task(task)

if __name__ == "__main__":
    main()
