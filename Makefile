.PHONY: Dockerfile-base Dockerfile-dev Dockerfile-production start-dev start-production restart-dev restart-production stop-dev stop-production clean-dev clean-production tests

Dockerfile: Dockerfile-dev
Dockerfile-base:
	docker build -t studentenportal/studentenportal-base -f Dockerfile-base .

Dockerfile-dev: Dockerfile-base
	docker build -t studentenportal/studentenportal-dev -f Dockerfile-dev .

Dockerfile-production: Dockerfile-base
	docker build -t studentenportal/studentenportal -f Dockerfile-production .

start-dev:
	docker-compose create
	docker-compose up -d

start-production:
	docker-compose --file docker-compose-production.yml create
	docker-compose --file docker-compose-production.yml start

restart-dev: stop-dev start-dev
restart-production: stop-production start-production

stop-dev:
	docker-compose stop

stop-production:
	docker-compose --file docker-compose-production.yml stop

clean-dev: stop-dev
	docker-compose rm

clean-production: stop-production
	docker-compose --file docker-compose-production.yml rm

tests:
	docker-compose run --rm studentenportal-dev ./test.sh
