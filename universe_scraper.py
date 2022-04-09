import os.path
import pathlib
import urllib.parse as urllib
from datetime import datetime

import aiofiles
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

    def save_images(self, dir_path, image_urls):
        start = datetime.now()
        for image_url in image_urls:
            filename = urllib.urlparse(image_url).path.split('/')[2] # не смог придумать лучше реализацию, подскажи пожалуйста, если есть идеи без магической цифры
            save_path = os.path.join(dir_path, filename)

            response = self.session.get(url=image_url)
            response.raise_for_status()

            with open(save_path, 'wb') as image:
                image.write(response.content)
        print(datetime.now() - start)

    async def async_save_images(self, dir_path, image_urls):
        start = datetime.now()

        async with aiohttp.ClientSession() as session:

            for image_url in image_urls:
                async with session.get(image_url) as response:
                    filename = urllib.urlparse(image_url).path.split('/')[2]
                    save_path = os.path.join(dir_path, filename)
                    response.raise_for_status()

                    image = await aiofiles.open(save_path, 'wb')
                    await image.write(await response.read())
                    await image.close()

        print(datetime.now() - start)


def main():
    dir_path = 'images/'
    pathlib.Path(dir_path).mkdir(parents=True, exist_ok=True)
    space_x_instance = SpaceXAPI()

    latest_launch = space_x_instance.get_latest_launch()
    image_urls = latest_launch['links']['flickr']['original']

    if not image_urls:
        image_urls = space_x_instance.get_latest_launch_with_images()

    # loop = asyncio.get_event_loop()
    # loop.run_until_complete(space_x_instance.async_save_images(dir_path=dir_path, image_urls=image_urls[:100]))
    space_x_instance.save_images(dir_path=dir_path, image_urls=image_urls)


if __name__ == '__main__':
    main()
