# syntax=docker/dockerfile:1

FROM python:3.13-slim

# Install curl
RUN apt-get update && apt-get install -y curl

WORKDIR /app

RUN useradd -ms /bin/bash gw
USER gw
WORKDIR /home/gw

COPY . .

RUN pip3 --no-cache-dir install -r requirements.txt .

ENV FLASK_APP=gitlab-webhook-flask

HEALTHCHECK CMD curl -f http://localhost:5000/health || exit 1

CMD [ "/home/gw/.local/bin/flask", "run", "--host=0.0.0.0"]
