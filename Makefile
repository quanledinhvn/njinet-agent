-include .env
PORT ?= 8000

.PHONY: lint fmt test check dev docker-up docker-down

lint:
	uv run ruff check --fix

fmt:
	uv run ruff format

test:
	uv run pytest -v

check: lint fmt test

dev:
	PYTHONASYNCIODEBUG=1 uv run fastapi dev src/njinet_agent/main.py --port $(PORT)

docker-up:
	docker compose up -d

docker-down:
	docker compose down
