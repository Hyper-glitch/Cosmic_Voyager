import os.path
import urllib.parse as urllib

import requests


# add ABC class here, we don't need implement get_json twice or more
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

    def get_json(self, endpoint, params=None) -> dict:
        url = urllib.urljoin(self.base_url, endpoint)
        response = self.session.get(url=url, params=params)
        response.raise_for_status()
        return response.json()

    def get_apod(self, count):
        """
        APOD it's an Astronomy Picture of the Day
        :return:
        """
        endpoint = 'apod'
        images = self.get_json(endpoint=endpoint, params={'count': count})

        image_urls = []
        for image in images:
            hd_image_url = image.get('hdurl')
            if hd_image_url:
                image_urls.append(hd_image_url)
        return image_urls
