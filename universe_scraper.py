import asyncio
import os
from datetime import datetime

from dotenv import load_dotenv

from cosmic_APIs import SpaceXAPI, NasaAPI
from scraper_utils import make_images_dir, save_images, get_images_content

PATH_TO_SAVE_IMAGES = 'images/'


def run_spacex_scraper():
    image_name = 'spacex'

    make_images_dir(dir_path=PATH_TO_SAVE_IMAGES)
    space_x_instance = SpaceXAPI()
    latest_launch = space_x_instance.get_latest_launch()
    image_urls = latest_launch['links']['flickr']['original']

    if not image_urls:
        image_urls = space_x_instance.get_latest_launch_with_images()

    images_content = asyncio.run(get_images_content(image_urls))
    save_images(dir_path=PATH_TO_SAVE_IMAGES, images_content=images_content, image_name=image_name)


def run_nasa_scraper():
    load_dotenv()
    nasa_token = os.getenv('NASA_API_KEY')
    image_name = 'nasa'
    make_images_dir(dir_path=PATH_TO_SAVE_IMAGES)

    nasa_instance = NasaAPI(token=nasa_token)
    apod_image_urls = nasa_instance.get_apod(count=50)
    images_content = asyncio.run(get_images_content(image_urls=apod_image_urls))
    save_images(dir_path=PATH_TO_SAVE_IMAGES, images_content=images_content, image_name=image_name)


if __name__ == '__main__':
    start = datetime.now()
    run_spacex_scraper()
    run_nasa_scraper()
    print(datetime.now() - start)
