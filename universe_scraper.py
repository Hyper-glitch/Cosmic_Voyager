import os.path
import pathlib

import requests


def save_image(image_url, save_path):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36"
    }
    response = requests.get(url=image_url, headers=headers)
    response.raise_for_status()

    with open(save_path, 'wb') as image:
        image.write(response.content)


if __name__ == '__main__':
    image_url = 'https://upload.wikimedia.org/wikipedia/commons/3/3f/HST-SM4.jpeg'
    filename = 'hubble_telescope.jpg'
    dir_path = 'images/'

    save_path = os.path.join(dir_path, filename)
    pathlib.Path(dir_path).mkdir(parents=True, exist_ok=True)
    save_image(image_url=image_url, save_path=save_path)
