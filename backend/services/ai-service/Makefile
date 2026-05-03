.PHONY: install dev ci-install lint format check test clean run docker-build

install:
	uv sync --no-dev

dev:
	uv sync

ci-install:
	uv sync --frozen

lint:
	uv run ruff check app tests

format:
	uv run ruff format app tests
	uv run ruff check app tests --fix

check:
	uv run ruff check app tests
	uv run ruff format --check app tests

test:
	uv run pytest -v

clean:
	rm -rf .venv
	rm -rf .pytest_cache
	rm -rf .ruff_cache
	find . -type d -name "__pycache__" -exec rm -rf {} +

run:
	uv run uvicorn app.main:app --host 0.0.0.0 --port 8003 --reload

docker-build:
	docker build -t aimatch-ai-service .
