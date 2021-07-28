# syntax=docker/dockerfile:1

FROM python:3.9-slim-buster

WORKDIR /app

RUN pip3 install pipenv

COPY . .
RUN pipenv install --deploy --ignore-pipfile

ENV FLASK_APP=gitlab-webhook-flask

CMD [ "pipenv", "run", "flask", "run", "--host=0.0.0.0"]
