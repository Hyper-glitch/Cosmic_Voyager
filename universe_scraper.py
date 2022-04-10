import asyncio
import os
import pathlib

import aiohttp
from dotenv import load_dotenv

from cosmic_APIs import SpaceXAPI, NasaAPI, get_image_extension

PATH_TO_SAVE_IMAGES = 'images/'


async def fetch(image_url, session):
    image_content = {}
    async with session.get(image_url) as response:
        response.raise_for_status()
        content = await response.read()
        image_extension = await get_image_extension(response.url.name)
        image_content.update({'content': content, 'image_extension': image_extension})
        return image_content


async def get_images_content(image_urls):
    tasks = []
    async with aiohttp.ClientSession() as session:
        for image_url in image_urls:
            tasks.append(asyncio.create_task(fetch(image_url, session)))
        images_content = asyncio.gather(*tasks)
        return await images_content


def make_images_dir(dir_path):
    pathlib.Path(dir_path).mkdir(parents=True, exist_ok=True)


def save_images(dir_path, images_content, image_name):
    for index, image_content in enumerate(images_content):
        filename = f"{image_name}{index}{image_content['image_extension']}"
        save_path = os.path.join(dir_path, filename)

        with open(save_path, 'wb') as image:
            image.write(image_content['content'])


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
    run_spacex_scraper()
    run_nasa_scraper()
