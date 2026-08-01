# This file create a "studentenportal" image for the production deployment
#  of the studentenportal.
# Images have the same versioning as the studentenportal itself,
#  and are uploaded to dockerhub.

### builder ###
FROM python:3.14 AS builder

RUN apt-get update && apt-get -y install \
    build-essential gcc g++ \
    python3-dev python3-setuptools python3-pip \
    libjpeg-progs graphicsmagick \
    libpq-dev ruby ruby-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements/ /tmp/requirements/
RUN python3 -m pip --quiet install -U pip wheel setuptools
RUN python3 -m pip --quiet install --prefix=/install \
    -r /tmp/requirements/base/requirements.txt \
    -r /tmp/requirements/production/requirements.txt

### runtime ###
FROM python:3.14-slim

RUN apt-get update && apt-get -y install --no-install-recommends \
    libpq5 libjpeg-progs graphicsmagick curl \
    && rm -rf /var/lib/apt/lists/*

ARG UID=1001
ARG GID=1001

RUN groupadd -g $GID studentenportal
RUN useradd --home /home/studentenportal -u $UID -g $GID -M studentenportal

COPY --from=builder /install /usr/local

RUN mkdir -p /srv/www/studentenportal
WORKDIR /srv/www/studentenportal

# We only add a minimal set of files needed for production.
RUN mkdir media static
COPY LICENSE.txt manage.py setup.py deploy/production/start.sh /srv/www/studentenportal/
COPY apps /srv/www/studentenportal/apps/
COPY config /srv/www/studentenportal/config/
RUN chown -R studentenportal:studentenportal /srv/www/studentenportal/

VOLUME ["/srv/www/studentenportal/media"]
VOLUME ["/srv/www/studentenportal/static"]

ENV PATH=/usr/local/bin/:$PATH
USER studentenportal
CMD ["./start.sh"]
