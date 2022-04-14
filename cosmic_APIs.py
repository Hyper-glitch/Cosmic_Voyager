import asyncio
import os.path
import urllib.parse as urllib
from typing import List

import requests

from scraper_utils import make_images_dir, get_images_content, save_images


class BaseAPI:
    def __init__(self, base_url, headers):
        self.base_url = base_url
        self.headers = headers
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def get_json(self, endpoint, params=None) -> dict:
        url = urllib.urljoin(self.base_url, endpoint)
        response = self.session.get(url=url, params=params)
        response.raise_for_status()
        return response.json()


class SpaceXAPI(BaseAPI):
    def get_latest_launch(self):
        endpoint = 'launches/latest'
        return self.get_json(endpoint=endpoint)

    def get_latest_launch_with_images(self):
        endpoint = 'launches'
        launches = self.get_json(endpoint=endpoint)
        image_urls = []

        for launch in launches:
            urls = launch['links']['flickr']['original']
            if urls:
                image_urls.extend(urls)
        return image_urls


class NasaAPI(BaseAPI):
    def __init__(self, base_url, headers, params):
        super().__init__(base_url, headers)
        self.session.params = params

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

    def get_epic_meta(self, image_type) -> (str, str):
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

    def save_images(self, dir_path, image_type, image_name, subdir):

        if subdir == 'EPIC':
            date, filenames = self.get_epic_meta(image_type=image_type)
            urls = self.get_epic_urls(date, filenames, image_type)
        elif subdir == 'APOD':
            urls = self.get_apod_urls(count=50)

        save_path = os.path.join(dir_path, subdir)
        make_images_dir(dir_path=save_path)
        content = asyncio.run(get_images_content(image_urls=urls, params=self.session.params))
        save_images(dir_path=save_path, images_content=content, image_name=image_name)
