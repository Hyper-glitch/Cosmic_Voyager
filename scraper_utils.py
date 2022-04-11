import asyncio
import os
import pathlib

import aiohttp


def make_images_dir(dir_path):
    pathlib.Path(dir_path).mkdir(parents=True, exist_ok=True)


def save_images(dir_path, images_content, image_name):
    for index, image_content in enumerate(images_content):
        filename = f"{image_name}{index}{image_content['image_extension']}"
        save_path = os.path.join(dir_path, filename)

        with open(save_path, 'wb') as image:
            image.write(image_content['content'])


async def fetch(image_url, session, params=None):
    image_content = {}
    async with session.get(image_url, params=params) as response:
        response.raise_for_status()
        content = await response.read()
        image_extension = get_image_extension(response.url.name)
        image_content.update({'content': content, 'image_extension': image_extension})
        return image_content


async def get_images_content(image_urls, params=None):
    tasks = []
    async with aiohttp.ClientSession() as session:
        for image_url in image_urls:
            tasks.append(asyncio.create_task(fetch(image_url, session, params)))
        images_content = asyncio.gather(*tasks)
        return await images_content


def get_image_extension(url):
    return os.path.splitext(url)[1]
