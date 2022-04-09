import os.path
import pathlib
import urllib.parse as urllib

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

    def get_json(self, endpoint):
        url = urllib.urljoin(self.base_url, endpoint)
        response = self.session.get(url=url)
        response.raise_for_status()
        return response.json()

    def get_latest_launch(self):
        endpoint = 'launches/latest'
        return self.get_json(endpoint=endpoint)

    def get_latest_launch_with_images(self):
        endpoint = 'launches'
        return self.get_json(endpoint=endpoint)

    def save_image(self, image_url, save_path):
        response = self.session.get(url=image_url)
        response.raise_for_status()

        with open(save_path, 'wb') as image:
            image.write(response.content)


def main():
    image_url = 'https://upload.wikimedia.org/wikipedia/commons/3/3f/HST-SM4.jpeg'
    filename = 'hubble_telescope.jpg'
    dir_path = 'images/'
    save_path = os.path.join(dir_path, filename)

    pathlib.Path(dir_path).mkdir(parents=True, exist_ok=True)
    space_x_instance = SpaceXAPI()
    latest_launch = space_x_instance.get_latest_launch()
    launch_images = latest_launch['links']['flickr']['original']

    if not launch_images:
        latest_launch = space_x_instance.get_latest_launch_with_images()

    space_x_instance.save_image(image_url=image_url, save_path=save_path)


if __name__ == '__main__':
    main()
