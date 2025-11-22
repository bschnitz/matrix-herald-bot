FROM python:3.14-slim

ENV POETRY_VERSION=2.2.0 \
    POETRY_HOME="/opt/poetry"

RUN pip install --no-cache-dir "poetry==${POETRY_VERSION}"

RUN apt-get update && apt-get install -y --no-install-recommends \
    supervisor \
    && rm -rf /var/lib/apt/lists/*

COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf
