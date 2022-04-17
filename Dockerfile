FROM python:3.9-alpine
WORKDIR cosmic_voyager/
COPY requirements.txt .
RUN apk update && pip install -r requirements.txt
COPY . .
CMD ["python", "universe_scraper.py"]