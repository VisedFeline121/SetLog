.PHONY: run seed test bench stop clean help lint lint-fix ci-lint ci-test security ci-security reset-db reset-full setup-db verify-db

# Default target
help:
	@echo "Available commands:"
	@echo "  run     - Start all services"
	@echo "  seed    - Load demo data"
	@echo "  test    - Run tests"
	@echo "  bench   - Run performance benchmarks"
	@echo "  stop    - Stop all services"
	@echo "  reset-db - Reset database schema (keep container)"
	@echo "  reset-full - Full reset (remove volumes, rebuild everything)"
	@echo "  setup-db - Setup database roles and permissions"
	@echo "  verify - Verify populated data"
	@echo "  clean   - Stop and remove volumes"
	@echo "  lint    - Run pre-commit hooks (modifies code)"
	@echo "  lint-fix - Run pre-commit hooks manually"
	@echo "  ci-lint - Run linters in check mode (CI safe)"
	@echo "  test    - Run tests in Docker"
	@echo "  ci-test - Run tests directly (CI safe)"
	@echo "  security - Run security checks locally"
	@echo "  ci-security - Run security checks (CI safe)"

# Start all services (API, PostgreSQL, Redis) in detached mode
run:
	docker compose up -d --build

# Load demo data into the database (requires services to be running)
seed:
	docker compose exec api python -m scripts.db_scripts.db_population.populate_database

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

# Run tests directly without Docker (faster for CI)
ci-test:
	pytest

# Run security checks locally (requires dev dependencies)
security:
	pip-audit --format=json --output=pip-audit-report.json || true
	@echo "Security check completed. Check pip-audit-report.json for details."

# Run security checks in CI mode (assumes tools are already installed)
ci-security:
	pip-audit --format=json --output=pip-audit-report.json || true

# Reset database schema (keep container, just drop/recreate tables)
reset-db:
	@echo "Resetting database schema..."
	docker compose exec api alembic downgrade base || true
	docker compose exec api alembic upgrade head
	@echo "Database schema reset complete!"

# Full reset (remove volumes, rebuild everything)
reset-full:
	@echo "Performing full reset (this will delete all data)..."
	docker compose down -v
	docker volume rm setlog_db_data || true
	docker compose up -d --build
	@echo "Full reset complete!"

# Setup database roles and permissions
setup-db:
	docker compose exec api python -m scripts.db_scripts.setup_database

# Verify populated data
verify:
	docker compose exec api python -m scripts.db_scripts.db_population.verify_data