server:
	poetry run uvicorn --host=0.0.0.0 --port 8080 --reload --reload-dir=src api.asgi:app

format:
	poetry run ruff format src
	poetry run ruff check src --fix

lint:
	poetry check --lock
	poetry run ruff check src
	poetry run mypy --config-file=mypy.ini src

.PHONY: server format lint