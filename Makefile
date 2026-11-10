.PHONY: install db-up db-down migrate test lint run-backend run-frontend

install:
	cd backend && python -m pip install -e ".[dev]"
	cd simulator && python -m pip install -e ".[dev]"
	cd evaluation && python -m pip install -e ".[dev]"
	cd frontend && npm install

db-up:
	docker compose up -d postgres

db-down:
	docker compose down

migrate:
	cd backend && alembic upgrade head

test:
	cd backend && pytest
	cd simulator && pytest
	cd evaluation && pytest

lint:
	cd backend && ruff check .
	cd simulator && ruff check .
	cd evaluation && ruff check .

run-backend:
	cd backend && uvicorn rootwise.main:create_app --factory --reload

run-frontend:
	cd frontend && npm run dev
