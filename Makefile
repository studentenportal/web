.PHONY: Dockerfile-base Dockerfile-dev Dockerfile-production start-dev start-production restart-dev restart-production stop-dev stop-production clean-dev clean-production

Dockerfile: Dockerfile-dev
Dockerfile-base:
	docker build -t studentenportal/studentenportal-base -f Dockerfile-base .

Dockerfile-dev: Dockerfile-base
	docker build -t studentenportal/studentenportal-dev -f Dockerfile-dev .

Dockerfile-production: Dockerfile-base
	docker build -t studentenportal/studentenportal -f Dockerfile-production .

start-dev:
	docker-compose create
	docker-compose start

start-production:
	docker-compose --file docker-compose-production.yml create
	docker-compose --file docker-compose-production.yml start

restart-dev: stop-dev start-dev
restart-production stop-production start-production

stop-dev:
	docker-compose stop

stop-production:
	docker-compose --file docker-compose-production.yml stop

clean-dev: stop-dev
	docker-compose rm

clean-production: stop-production
	docker-compose --file docker-compose-production.yml rm
