import os
import time

import telegram
from dotenv import load_dotenv

from scraper_utils import get_all_image_paths


def init_telegram_bot(telegram_token):
    return telegram.Bot(token=telegram_token)


if __name__ == '__main__':
    load_dotenv()

    # chat_id канала — это ссылка на него, например: @cosmic_odyssey_2022
    chat_id = os.environ.get('CHAT_ID')
    send_photo_period = float(os.getenv('SEND_PHOTO_PERIOD'))
    telegram_token = os.getenv('TG_TOKEN')

    tg_bot = init_telegram_bot(telegram_token=telegram_token)

    dir_path = 'images'
    image_paths = get_all_image_paths(dir_path=dir_path)

    for image_path in image_paths:
        tg_bot.send_photo(chat_id=chat_id, photo=open(image_path, 'rb'))
        time.sleep(send_photo_period)
