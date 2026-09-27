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
	docker compose up -d --build
logs:
	docker compose logs -f

ps:
	docker compose ps