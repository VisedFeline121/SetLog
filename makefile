.PHONY: run seed test bench stop clean help lint lint-fix ci-lint ci-test

# Default target
help:
	@echo "Available commands:"
	@echo "  run     - Start all services"
	@echo "  seed    - Load demo data"
	@echo "  test    - Run tests"
	@echo "  bench   - Run performance benchmarks"
	@echo "  stop    - Stop all services"
	@echo "  clean   - Stop and remove volumes"
	@echo "  lint    - Run pre-commit hooks (modifies code)"
	@echo "  lint-fix - Run pre-commit hooks manually"
	@echo "  ci-lint - Run linters in check mode (CI safe)"
	@echo "  test    - Run tests in Docker"
	@echo "  ci-test - Run tests directly (CI safe)"

# Start all services (API, PostgreSQL, Redis) in detached mode
run:
	docker compose up -d --build

# Load demo data into the database (requires services to be running)
seed:
	docker compose exec api python scripts/seed_data.py

# Run tests inside Docker container (full environment)
test:
	docker compose exec api pytest

# Run performance benchmarks using k6 (requires services running)
bench:
	docker compose exec api k6 run load/post_set.js

# Stop all running services
stop:
	docker compose down

# Stop services and remove all volumes (WARNING: deletes all data)
clean:
	docker compose down -v
	docker system prune -f

# Run pre-commit hooks (formats code automatically)
lint:
	python -m pre_commit run --all-files

# Run pre-commit hooks manually (useful for testing)
lint-fix:
	python -m pre_commit run --all-files --hook-stage manual

# Run linters in check mode only (CI safe - won't modify code)
ci-lint:
	python -m black --check .
	python -m ruff check .
	python -m isort --check-only .
	python -m mypy .

# Run tests directly without Docker (faster for CI)
ci-test:
	pytest