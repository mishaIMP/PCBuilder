FROM python:3.12

WORKDIR /API/

RUN mkdir "API"

COPY . /API/API

RUN pip install -r API/requirements.txt

RUN flask --app="API/run.py" db init
RUN flask --app="API/run.py" db migrate
RUN flask --app="API/run.py" db upgrade
