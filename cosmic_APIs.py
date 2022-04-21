import asyncio
import os.path
import pathlib
import urllib.parse as urllib
from typing import List, Dict

import requests

from scraper_utils import get_images_content, save_images_content


class BaseAPI:
    """Base API class which implements with all repeatable attributes and methods."""
    def __init__(self, base_url: str, headers: Dict):
        self.base_url = base_url
        self.headers = headers
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def get_json(self, endpoint: str, params: Dict = None) -> Dict:
        """Make full url and send GET request.
        :param endpoint: - it is a point to interact with definite method to API
        :param params: - additional data for getting info from response
        :returns: response.json() - information from response in dict data structure
        """
        url = urllib.urljoin(self.base_url, endpoint)
        response = self.session.get(url=url, params=params)
        response.raise_for_status()
        return response.json()


class SpaceXAPI(BaseAPI):
    """Class to interact with SpaceX API."""
    def get_latest_launch(self) -> Dict:
        """Returns the most recent launch"""
        endpoint = 'launches/latest'
        return self.get_json(endpoint=endpoint)

    def get_latest_launch_with_images(self) -> List:
        """Gets the most recent launch just with images.
        :returns: image_urls - urls to images
        """
        endpoint = 'launches'
        launches = self.get_json(endpoint=endpoint)
        image_urls = []

        for launch in launches:
            urls = launch['links']['flickr']['original']
            if urls:
                image_urls.extend(urls)
        return image_urls


class NasaAPI(BaseAPI):
    """Class to interact with Nasa API."""
    def __init__(self, base_url, headers, params):
        super().__init__(base_url, headers)
        self.session.params = params

    def get_apod_urls(self, count) -> List:
        """Gets HD APOD image urls. APOD it's an Astronomy Picture of the Day.
        :param count: - if this is specified then count randomly chosen images will be returned
        :returns: image_urls - urls to images
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
        """Gets Retrievable Metadata of the EPIC (Earth Polychromatic Imaging Camera ) images.
        :param image_type: - image types available: full resolution (png), half-resolution (jpg), thumbnails (thumbs).
        :returns: date - year-month-day format, filenames - for example epic_1b_20161031xxxx.png
        """
        endpoint = 'EPIC/api/natural/images'
        images = self.get_json(endpoint=endpoint)
        date = images[0]['date']
        filenames = []

        for image in images:
            filename = image['image'] + f'.{image_type}'
            filenames.append(filename)
        return date, filenames

    def get_epic_urls(self, date: str, filenames: List, image_type: str) -> List:
        """Gets urls for EPIC images.
        :param date: - year-month-day format.
        :param filenames: - list of all filenames.
        :param image_type: - image types available: full resolution (png), half-resolution (jpg), thumbnails (thumbs).
        :returns: epic_urls - urls to EPIC images.
        """
        # url example https://api.nasa.gov/EPIC/archive/natural/2019/05/30/png/epic_1b_20190530011359.png?api_key=DEMO_KEY
        endpoint = 'EPIC/archive/natural/'
        parsed_date = date.split(' ')[0].replace('-', '/')  # не придумал лучшего решения, если есть, подскажи плиз
        epic_urls = []

        for filename in filenames:
            url = urllib.urljoin(self.base_url, endpoint) + parsed_date + f'/{image_type}/' + filename  # здесь тоже
            epic_urls.append(url)
        return epic_urls

    def save_images(self, dir_path: str, image_type: str, image_name: str, subdir: str):
        """Saves images to specific directory depending on the API's endpoint.
        :param dir_path: - basic path to save images.
        :param image_type: - image types available: full resolution (png), half-resolution (jpg), thumbnails (thumbs).
        :param image_name: equivalent scraper's name.
        :param subdir: equivalent API's endpoint.
        """
        if subdir == 'EPIC':
            date, filenames = self.get_epic_meta(image_type=image_type)
            urls = self.get_epic_urls(date, filenames, image_type)
        elif subdir == 'APOD':
            urls = self.get_apod_urls(count=50)

        save_path = os.path.join(dir_path, subdir)
        pathlib.Path(dir_path).mkdir(parents=True, exist_ok=True)
        content = asyncio.run(get_images_content(image_urls=urls, params=self.session.params))
        save_images_content(dir_path=save_path, images_content=content, image_name=image_name)
