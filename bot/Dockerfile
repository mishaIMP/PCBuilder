FROM python:3.12

WORKDIR /bot

RUN mkdir "bot"

COPY . /bot/bot

ENV TOKEN=<YOUR TOKEN>
ENV IP=http://localhost:5000/

RUN pip install -r bot/requirements.txt
