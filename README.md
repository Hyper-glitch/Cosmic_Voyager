# Cosmic_Voyager

## Basic information

***Cosmic_Voyager*** allows you to parse images asynchronously from Nasa and SpaceX API and sends them to the channel with telegram bot.

## Starting

| Environmental         | Description                                           |
|-----------------------|-------------------------------------------------------|
| `NASA_API_KEY`        | personal access token for authorization to Nasa API   |
| `TG_TOKEN`            | personal token to interact with telegram bot          |
| `CHAT_ID`             | the name of a telegram channel                        |
| `SEND_PHOTO_PERIOD`   | the period of time to sending image                   |

1. clone the repository:
```bash
git clone https://github.com/Hyper-glitch/Cosmic_Voyager.git
```
2. Create **.env** file and set the <ins>environmental variables</ins> as described above.
3. Install dependencies:
```bash
pip install -r requirements.txt
```
4. Run python script
```bash
python3 universe_scraper.py
```
5. Run with docker
```bash
docker build -t cosmic_voyager . && docker run -d --env-file .env cosmic_voyager
```
