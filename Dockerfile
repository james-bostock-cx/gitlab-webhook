# syntax=docker/dockerfile:1

FROM library/python:3.13.0-alpine3.20

# Install curl
RUN apk --no-cache add "curl=8.11.0-r2"

WORKDIR /app

RUN addgroup -S gw && adduser -S gw -G gw
USER gw
WORKDIR /home/gw

COPY . .

RUN pip3 --no-cache-dir install -r requirements.txt .

ENV FLASK_APP=gitlab-webhook-flask

HEALTHCHECK CMD curl -f http://localhost:5000/health || exit 1

CMD [ "/home/gw/.local/bin/flask", "run", "--host=0.0.0.0"]
