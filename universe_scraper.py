import asyncio
import os
import time
from datetime import datetime

import telegram
from dotenv import load_dotenv

from cosmic_APIs import SpaceXAPI, NasaAPI
from scraper_utils import make_images_dir, save_images, get_images_content, get_all_image_paths

PATH_TO_SAVE_IMAGES = 'images/'
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/70.0.3538.77 Safari/537.36',
}


def run_spacex_scraper():

    scraper_name = 'spacex'
    base_url = 'https://api.spacexdata.com/v4/'
    dir_path = os.path.join(PATH_TO_SAVE_IMAGES, scraper_name)

    make_images_dir(dir_path=dir_path)

    space_x_instance = SpaceXAPI(base_url=base_url, headers=HEADERS)
    latest_launch = space_x_instance.get_latest_launch()
    image_urls = latest_launch['links']['flickr']['original']

    if not image_urls:
        image_urls = space_x_instance.get_latest_launch_with_images()

    images_content = asyncio.run(get_images_content(image_urls=image_urls))
    save_images(dir_path=dir_path, images_content=images_content, image_name=scraper_name)


def run_nasa_scraper():

    scraper_name = 'nasa'
    base_url = 'https://api.nasa.gov/'
    params = {'api_key': nasa_token}
    sub_dirs = ['APOD', 'EPIC']
    dir_path = os.path.join(PATH_TO_SAVE_IMAGES, scraper_name)

    nasa_instance = NasaAPI(base_url=base_url, headers=HEADERS, params=params)

    for subdir in sub_dirs:
        if subdir == 'APOD':
            image_type = None
        elif subdir == 'EPIC':
            image_type = 'png'
        nasa_instance.save_images(dir_path=dir_path, image_name=scraper_name, subdir=subdir, image_type=image_type)


def run_telegram_bot(telegram_token, send_photo_period, chat_id):

    tg_bot = telegram.Bot(token=telegram_token)
    image_paths = get_all_image_paths(dir_path=PATH_TO_SAVE_IMAGES)

    for image_path in image_paths:
        tg_bot.send_photo(chat_id=chat_id, photo=open(image_path, 'rb'))
        time.sleep(send_photo_period)


if __name__ == '__main__':
    start = datetime.now()

    load_dotenv()
    chat_id = os.environ.get('CHAT_ID')
    send_photo_period = float(os.getenv('SEND_PHOTO_PERIOD'))
    telegram_token = os.getenv('TG_TOKEN')
    nasa_token = os.getenv('NASA_API_KEY')

    run_telegram_bot(telegram_token=telegram_token, send_photo_period=send_photo_period, chat_id=chat_id)
    # run_spacex_scraper()
    # run_nasa_scraper(nasa_token)

    print(datetime.now() - start)
