FROM python:3.8-slim

RUN apt-get update && \
    apt-get install -y wget unzip xvfb libxi6 libgconf-2-4

RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
    apt install -y ./google-chrome-stable_current_amd64.deb && \
    rm google-chrome-stable_current_amd64.deb

RUN CHROME_DRIVER_VERSION=$(curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE) && \
    wget -O /tmp/chromedriver.zip http://chromedriver.storage.googleapis.com/$CHROME_DRIVER_VERSION/chromedriver_linux64.zip && \
    unzip /tmp/chromedriver.zip chromedriver -d /usr/local/bin/

RUN useradd -ms /bin/bash app
USER app
WORKDIR /app

USER root
RUN pip install pipenv
COPY Pipfile Pipfile.lock ./
RUN pipenv install --system --deploy

COPY data_extraction.py /app/
RUN mkdir -p /app/data
CMD ["python", "data_extraction.py"]
