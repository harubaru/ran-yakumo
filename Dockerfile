FROM python:3.9.6
ENV PYTHONUNBUFFERED 1

RUN mkdir /ran-bot
WORKDIR /ran-bot

COPY requirements.txt /ran-bot
RUN pip install -r requirements.txt

COPY . /ran-bot