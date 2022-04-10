import asyncio
import os
import pathlib

import aiohttp
from dotenv import load_dotenv

from cosmic_APIs import SpaceXAPI, NasaAPI


async def fetch(image_url, session):
    async with session.get(image_url) as response:
        response.raise_for_status()
        content = await response.read()
        return content


async def get_images_content(image_urls):
    tasks = []
    async with aiohttp.ClientSession() as session:
        for image_url in image_urls:
            tasks.append(asyncio.create_task(fetch(image_url, session)))
        images_content = asyncio.gather(*tasks)
        return await images_content


def make_images_dir(dir_path):
    pathlib.Path(dir_path).mkdir(parents=True, exist_ok=True)


def save_images(dir_path, images_content, file_extension, image_name):
    for index, image_content in enumerate(images_content):
        filename = f'{image_name}{index}{file_extension}'
        save_path = os.path.join(dir_path, filename)

        with open(save_path, 'wb') as image:
            image.write(image_content)


def run_spacex_scraper():
    dir_path = 'images/'
    file_extension = '.jpg'
    image_name = 'spacex'

    make_images_dir(dir_path=dir_path)
    space_x_instance = SpaceXAPI()
    latest_launch = space_x_instance.get_latest_launch()
    image_urls = latest_launch['links']['flickr']['original']

    if not image_urls:
        image_urls = space_x_instance.get_latest_launch_with_images()

    images_content = asyncio.run(get_images_content(image_urls))
    save_images(dir_path=dir_path, images_content=images_content,
                file_extension=file_extension, image_name=image_name
                )


def run_nasa_scraper():
    load_dotenv()
    nasa_token = os.getenv('NASA_API_KEY')

    dir_path = 'images/'
    file_extension = '.jpg' # пока не придумал как во время асинхронного запроса забирать сразу расширение, возможно надо создавать dict
    image_name = 'nasa'

    make_images_dir(dir_path=dir_path)
    nasa_instance = NasaAPI(token=nasa_token)
    apod_image_urls = nasa_instance.get_apod(count=50)
    images_content = asyncio.run(get_images_content(image_urls=apod_image_urls))
    save_images(dir_path=dir_path, images_content=images_content,
                file_extension=file_extension, image_name=image_name
                )


if __name__ == '__main__':
    run_spacex_scraper()
    run_nasa_scraper()
