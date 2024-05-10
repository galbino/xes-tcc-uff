FROM python:3.11-slim as builder

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_VERSION=1.8.2 \
    POETRY_HOME="/opt/poetry" \
    POETRY_NO_INTERACTION=1 \
    PATH="/opt/poetry/bin:$PATH"

RUN export DEBIAN_FRONTEND=noninteractive && \
    apt-get update && \
    apt-get -y upgrade && \
    apt-get install --no-install-recommends -y \
        curl

RUN curl -sSL https://install.python-poetry.org | python -

WORKDIR /app
COPY poetry.lock pyproject.toml ./
RUN poetry install --only main --no-root

COPY . /app
RUN poetry install --only main

FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PORT=8080 \
    PATH="/app/.venv/bin:$PATH"

USER nobody:nogroup
WORKDIR /app

COPY --from=builder /app /app

ENV GUNICORN_WORKERS=1

CMD gunicorn --bind :$PORT --workers $GUNICORN_WORKERS --threads 1 --timeout 0 --worker-class=uvicorn.workers.UvicornWorker --worker-tmp-dir=/dev/shm api.asgi:app