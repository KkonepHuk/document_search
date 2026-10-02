up:
	docker compose up -d

build:
	docker compose up -d --build

down:
	docker compose down
down-hard:
	docker compose down -v
	rm -rf pgdata esdata
restart:
	docker compose down
	docker compose up -d --build
rebuild:
	docker compose down -v
	rm -rf pgdata esdata
	docker compose up -d --build
ps:
	docker compose ps

test-run:
	python -m pytest -q tests/test_api.py