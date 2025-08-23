.PHONY: dev build test lint format clean install migrate seed

# Development
dev:
	docker-compose up --build

dev-detached:
	docker-compose up -d --build

dev-api:
	cd apps/api && python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

dev-web:
	cd apps/web && npm run dev

dev-worker:
	cd worker && python -m celery worker -A main:app --loglevel=info

# Build
build:
	npm run build

build-images:
	docker-compose build

# Database
migrate:
	cd apps/api && alembic upgrade head

migration:
	@read -p "Enter migration message: " msg; \
	cd apps/api && alembic revision --autogenerate -m "$$msg"

seed:
	cd apps/api && python -m scripts.seed_data

# Testing
test:
	npm run test

test-api:
	cd apps/api && python -m pytest

test-web:
	cd apps/web && npm run test

# Linting and formatting
lint:
	npm run lint

format:
	npm run format

typecheck:
	npm run typecheck

# Installation
install:
	npm install
	cd apps/web && npm install
	cd apps/api && pip install -r requirements.txt
	cd worker && pip install -r requirements.txt

# Cleanup
clean:
	docker-compose down -v
	docker system prune -f
	rm -rf node_modules */node_modules
	find . -name "__pycache__" -exec rm -rf {} +
	find . -name "*.pyc" -delete

# CI helpers
ci-install:
	npm ci
	cd apps/web && npm ci

ci-test:
	npm run typecheck
	npm run lint
	npm run test

# Agent build (Windows)
build-agent:
	cd agent-win && dotnet build -c Release

# Documentation
docs-serve:
	cd docs && python -m http.server 8080