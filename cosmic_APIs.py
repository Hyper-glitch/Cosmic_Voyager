import os.path
import urllib.parse as urllib

import requests


# add ABC class here, we don't need implement get_json twice or more
from dotenv import load_dotenv


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
    def save_images(dir_path, images_content, file_extension, image_name):

        for index, image_content in enumerate(images_content):
            filename = f'{image_name}{index}{file_extension}'
            save_path = os.path.join(dir_path, filename)

            with open(save_path, 'wb') as image:
                image.write(image_content)


class NasaAPI:
    def __init__(self, token):
        self.base_url = 'https://api.nasa.gov/planetary/'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/70.0.3538.77 Safari/537.36',
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        self.session.params = {'api_key': token}

    def get_json(self, endpoint) -> dict:
        url = urllib.urljoin(self.base_url, endpoint)
        response = self.session.get(url=url)
        response.raise_for_status()
        return response.json()

    def get_apod(self):
        """
        APOD it's an Astronomy Picture of the Day
        :return:
        """
        endpoint = 'apod'
        return self.get_json(endpoint=endpoint)


if __name__ == '__main__':
    load_dotenv()
    nasa_token = os.getenv('NASA_API_KEY')

    nasa_instance = NasaAPI(token=nasa_token)
    apod = nasa_instance.get_apod()
