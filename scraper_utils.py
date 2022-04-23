import asyncio
import os
from typing import List, Dict

import aiohttp


def get_all_image_paths(dir_path: str) -> List:
    """Walks through all directories and files in there Collect all paths for images.
    :param dir_path: - path for creating directory.
    :returns: image_paths - all paths for images.
    """
    paths = []
    image_paths = []

    for path in os.walk(dir_path):
        paths.append(path)

    for address, folders, files in paths:
        for file in files:
            image_path = f'{address}/{file}'
            image_paths.append(image_path)
    return image_paths


def save_images_content(dir_path: str, images_content: List, image_name: str):
    """Saves images byte content into image file with extension and its name.
    :param dir_path: - path for creating directory.
    :param images_content: - content that gets from async responses.
    :param image_name: - equal the scraper's name.
    """
    for index, image_content in enumerate(images_content):
        filename = f"{image_name}{index}{image_content['image_extension']}"
        save_path = os.path.join(dir_path, filename)

        with open(save_path, 'wb') as image:
            image.write(image_content['content'])


async def fetch(image_url, session, params=None) -> Dict:
    """Sends async get requests for getting images byte content.
    :param image_url: - url for getting image.
    :param session: - session object from aiohttp package.
    :param params: - additional info for getting response if it needs.
    :returns: image_content: - dict with content and image's extension.
    """
    image_content = {}
    async with session.get(image_url, params=params) as response:
        response.raise_for_status()
        content = await response.read()
        image_extension = get_image_extension(response.url.name)
        image_content.update({'content': content, 'image_extension': image_extension})
        return image_content


async def get_images_content(image_urls: List, params: Dict = None):
    """Creates tasks for async getting image's content.
    :param image_urls: - urls for getting images.
    :param params: - additional info for getting response if it needs.
    :returns: images_content: - list of dicts with content and image's extension.
    """
    tasks = []
    async with aiohttp.ClientSession() as session:
        for image_url in image_urls:
            tasks.append(asyncio.create_task(fetch(image_url, session, params)))
        images_content = asyncio.gather(*tasks)
        return await images_content


def get_image_extension(url: str) -> str:
    """Gets image's extension from url.
    :param url: - urls for getting images.
    :returns: image extension.
    """
    return os.path.splitext(url)[1]
