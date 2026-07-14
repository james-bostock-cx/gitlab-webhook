# syntax=docker/dockerfile:1

# python:3.14.6-alpine3.24
FROM python@sha256:26730869004e2b9c4b9ad09cab8625e81d256d1ce97e72df5520e806b1709f92

# Install curl
RUN apk --no-cache add "curl=8.21.0-r0"

WORKDIR /app

RUN addgroup -S gw && adduser -S gw -G gw
USER gw
WORKDIR /home/gw

COPY . .

RUN pip3 --no-cache-dir install -r requirements.txt .

ENV FLASK_APP=gitlab-webhook-flask

HEALTHCHECK CMD curl -f http://localhost:5000/health || exit 1

CMD [ "/home/gw/.local/bin/flask", "run", "--host=0.0.0.0"]
