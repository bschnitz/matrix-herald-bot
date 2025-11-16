FROM python:3.14-slim

ENV POETRY_VERSION=2.2.0 \
    POETRY_HOME="/opt/poetry"

RUN pip install --no-cache-dir "poetry==${POETRY_VERSION}"

WORKDIR /app
