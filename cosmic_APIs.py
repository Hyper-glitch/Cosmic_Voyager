import asyncio
import os.path
import urllib.parse as urllib
from datetime import datetime
from typing import List

import requests
from dotenv import load_dotenv

from scraper_utils import make_images_dir, get_images_content, save_images


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
        self.base_url = 'https://api.nasa.gov/'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/70.0.3538.77 Safari/537.36',
        }
        self.params = {'api_key': token}
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        self.session.params = self.params

    def get_json(self, endpoint, params=None) -> dict:
        url = urllib.urljoin(self.base_url, endpoint)
        response = self.session.get(url=url, params=params)
        response.raise_for_status()
        return response.json()

    def get_apod_urls(self, count) -> List:
        """
        APOD it's an Astronomy Picture of the Day
        :return:
        """
        endpoint = 'planetary/apod'
        images = self.get_json(endpoint=endpoint, params={'count': count})

        image_urls = []
        for image in images:
            hd_image_url = image.get('hdurl')
            if hd_image_url:
                image_urls.append(hd_image_url)
        return image_urls

    def get_epic_meta(self, image_type):
        endpoint = 'EPIC/api/natural/images'
        images = self.get_json(endpoint=endpoint)

        date = images[0]['date']
        filenames = []
        for image in images:
            filename = image['image'] + f'.{image_type}'
            filenames.append(filename)
        return date, filenames

    def get_epic_urls(self, date, filenames, image_type) -> List:
        # url example https://api.nasa.gov/EPIC/archive/natural/2019/05/30/png/epic_1b_20190530011359.png?api_key=DEMO_KEY
        endpoint = 'EPIC/archive/natural/'
        parsed_date = date.split(' ')[0].replace('-', '/')  # не придумал лучшего решения, если есть, подскажи плиз
        epic_urls = []

        for filename in filenames:
            url = urllib.urljoin(self.base_url, endpoint) + parsed_date + f'/{image_type}/' + filename  # здесь тоже
            epic_urls.append(url)
        return epic_urls

    def save_apod_images(self, dir_path, image_name):
        subdir = 'APOD'
        save_path = os.path.join(dir_path, subdir)

        make_images_dir(dir_path=save_path)
        apod_image_urls = self.get_apod_urls(count=50)
        images_content = asyncio.run(get_images_content(image_urls=apod_image_urls))
        save_images(dir_path=save_path, images_content=images_content, image_name=image_name)

    def save_epic_images(self, dir_path, image_type, image_name):
        subdir = 'EPIC'
        save_path = os.path.join(dir_path, subdir)

        make_images_dir(dir_path=save_path)
        date, filenames = self.get_epic_meta(image_type=image_type)
        epic_urls = self.get_epic_urls(date, filenames, image_type)
        epic_content = asyncio.run(get_images_content(image_urls=epic_urls, params=self.params))
        save_images(dir_path=save_path, images_content=epic_content, image_name=image_name)


if __name__ == '__main__':
    start = datetime.now()
    print(datetime.now() - start)
