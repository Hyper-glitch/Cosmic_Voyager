import asyncio
import os.path
import pathlib
import urllib.parse as urllib
from datetime import datetime

import aiohttp
import requests


class SpaceXAPI:
    def __init__(self):
        self.base_url = 'https://api.spacexdata.com/v4/'
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/70.0.3538.77 Safari/537.36",
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def get_json(self, endpoint) -> dict:
        url = urllib.urljoin(self.base_url, endpoint)
        response = self.session.get(url=url)
        response.raise_for_status()
        return response.json()

    def get_latest_launch(self):
        endpoint = 'launches/latest'
        return self.get_json(endpoint=endpoint)

    def get_latest_launch_with_images(self):
        endpoint = 'launches'
        launches = self.get_json(endpoint=endpoint)

        image_urls = []

        for launch in launches:
            images = launch['links']['flickr']['original']
            if images:
                image_urls.extend(images)
        return image_urls

    @staticmethod
    def save_images(dir_path, images_content):
        file_order = 0
        file_extension = '.jpg'
        for image_content in images_content:
            file_order += 1
            filename = str(file_order) + file_extension
            save_path = os.path.join(dir_path, filename)
            with open(save_path, 'wb') as image:
                image.write(image_content)


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


def main():
    start = datetime.now()
    dir_path = 'images/'
    pathlib.Path(dir_path).mkdir(parents=True, exist_ok=True)
    space_x_instance = SpaceXAPI()

    latest_launch = space_x_instance.get_latest_launch()
    image_urls = latest_launch['links']['flickr']['original']

    if not image_urls:
        image_urls = space_x_instance.get_latest_launch_with_images()

    images_content = asyncio.run(get_images_content(image_urls))
    space_x_instance.save_images(dir_path=dir_path, images_content=images_content)
    print(datetime.now() - start)


if __name__ == '__main__':
    main()
