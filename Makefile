.PHONY: up down migrate seed test lint shell

up:
	docker-compose up -d

down:
	docker-compose down

migrate:
	docker-compose run --rm app alembic upgrade head

seed:
	docker-compose run --rm app python -m scripts.seed_db

test:
	docker-compose run --rm app pytest --cov=app --cov-report=term-missing -v

lint:
	ruff check . && black --check .

format:
	ruff check --fix . && black .

shell:
	docker-compose run --rm app bash

logs:
	docker-compose logs -f app
