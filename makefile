.PHONY: run seed test bench stop clean help lint lint-fix

# Default target
help:
	@echo "Available commands:"
	@echo "  run     - Start all services"
	@echo "  seed    - Load demo data"
	@echo "  test    - Run tests"
	@echo "  bench   - Run performance benchmarks"
	@echo "  stop    - Stop all services"
	@echo "  clean   - Stop and remove volumes"

run:
	docker compose up -d --build

seed:
	docker compose exec api python scripts/seed_data.py

test:
	docker compose exec api pytest

bench:
	docker compose exec api k6 run load/post_set.js

stop:
	docker compose down

clean:
	docker compose down -v
	docker system prune -f

lint:
	python -m pre_commit run --all-files

lint-fix:
	python -m pre_commit run --all-files --hook-stage manual