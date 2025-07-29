install:
	uv sync

build:
	./build.sh

dev:
	uv run flask --debug --app page_analyzer:app run

PORT ?= 8000
start:
	uv run gunicorn -w 5 -b 0.0.0.0:$(PORT) page_analyzer:app

render-start:
	gunicorn -w 5 -b 0.0.0.0:$(PORT) page_analyzer:app

lint:
	uv run ruff check

lint-with-fix:
	uv run ruff check --fixtest:

test:
	uv run pytest

test-coverage:
	uv run pytest --cov=gendiff --cov-report xml

check: test lint
