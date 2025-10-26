.PHONY: help up down logs fmt lint test migrate seed clean install dev

# Default target
help:
	@echo "Available commands:"
	@echo "  up          - Start all services with docker-compose"
	@echo "  down        - Stop all services"
	@echo "  logs        - Tail logs from all services"
	@echo "  fmt         - Format code with black and isort"
	@echo "  lint        - Run linting with ruff and type checking with mypy"
	@echo "  test        - Run tests with pytest"
	@echo "  migrate     - Generate and run database migrations"
	@echo "  seed        - Load seed data"
	@echo "  clean       - Clean up containers and volumes"
	@echo "  install     - Install dependencies"
	@echo "  dev         - Start development environment"

# Docker commands
up:
	docker-compose up -d

down:
	docker-compose down

logs:
	docker-compose logs -f

clean:
	docker-compose down -v --remove-orphans
	docker system prune -f

# Development commands
install:
	poetry install

dev: install
	poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Code quality
fmt:
	poetry run black app/ tests/ scripts/
	poetry run isort app/ tests/ scripts/

lint:
	poetry run ruff check app/ tests/ scripts/
	poetry run mypy app/

# Testing
test:
	poetry run pytest tests/ -v --cov=app --cov-report=term-missing

test-fast:
	poetry run pytest tests/ -v -x

# Database
migrate:
	docker-compose run --rm migrate

seed:
	docker-compose run --rm api poetry run python scripts/seed_data.py

# CI commands
ci-test: lint test

ci-build:
	docker build -t lorebound-backend .

# Development helpers
shell:
	docker-compose exec api bash

db-shell:
	docker-compose exec db psql -U postgres -d lorebound

redis-shell:
	docker-compose exec redis redis-cli
