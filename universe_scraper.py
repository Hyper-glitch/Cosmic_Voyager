import requests


def save_image(image_url, file_name):
    response = requests.get(url=image_url)
    response.raise_for_status()

    with open(file_name, 'wb') as image:
        image.write(response.content)


if __name__ == '__main__':
    image_url = 'https://upload.wikimedia.org/wikipedia/commons/3/3f/HST-SM4.jpeg'
    file_name = 'hubble_telescope.jpg'

    save_image(image_url=image_url, file_name=file_name)
