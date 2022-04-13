import os

import telegram
from dotenv import load_dotenv


def init_telegram_bot(telegram_token):
    return telegram.Bot(token=telegram_token)


if __name__ == '__main__':
    load_dotenv()

    # chat_id канала — это ссылка на него, например: @cosmic_odyssey_2022
    chat_id = os.environ.get('CHAT_ID')
    send_photo_period = os.getenv('SEND_PHOTO_PERIOD')
    telegram_token = os.getenv('TG_TOKEN')

    tg_bot = init_telegram_bot(telegram_token=telegram_token)

    dir_path = 'images/nasa/'
    dirs = os.walk(dir_path)
    while True:
        for dir in dirs:
            tg_bot.send_photo(chat_id=chat_id, photo=open(dir_path, 'rb'))
