.PHONY: Dockerfile-base Dockerfile-dev start start-dev

Dockerfile: Dockerfile-dev
Dockerfile-base:
	docker build -t studentenportal/studentenportal-base -f Dockerfile-base .

Dockerfile-dev: Dockerfile-base
	docker build -t studentenportal/studentenportal-dev -f Dockerfile-dev .

start: start-dev
start-dev:
	docker run --interactive --tty --rm --publish 8000:8000 \
		--volume="$(shell pwd):/srv/www/studentenportal" \
		--name studentenportal-dev studentenportal/studentenportal-dev
