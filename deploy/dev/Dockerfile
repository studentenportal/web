# This file create a "studentenportal" image for the dev environment.
# Additional packages for dev are added here.

### builder ###
FROM python:3.12 AS builder

RUN apt-get update && apt-get -y install \
    build-essential gcc g++ \
    python3-dev python3-setuptools python3-pip \
    postgresql-client libpq-dev \
    libjpeg-progs graphicsmagick \
    ruby ruby-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements/ /tmp/requirements/
RUN python3 -m pip --quiet install -U pip wheel setuptools
RUN python3 -m pip --quiet install --prefix=/install \
    -r /tmp/requirements/base/requirements.txt \
    -r /tmp/requirements/local/requirements.txt \
    -r /tmp/requirements/testing/requirements.txt

### runtime ###
FROM python:3.12

ARG SASS_VERSION=1.105.1
# TODO: remove npm
RUN apt-get update && apt-get -y install --no-install-recommends \
    libpq5 postgresql-client \
    libjpeg-progs graphicsmagick \
    curl dnsutils \
    npm \
    && npm install -g sass-migrator \
    && curl -fsSL -o /tmp/dart-sass.tar.gz \
        "https://github.com/sass/dart-sass/releases/download/${SASS_VERSION}/dart-sass-${SASS_VERSION}-linux-x64.tar.gz" \
    && tar -xzf /tmp/dart-sass.tar.gz -C /usr/local \
    && ln -s /usr/local/dart-sass/sass /usr/local/bin/sass \
    && rm /tmp/dart-sass.tar.gz \
    && sass --version \
    && rm -rf /var/lib/apt/lists/*

ARG UID=1000
ARG GID=1000

RUN groupadd -g $GID studentenportal
RUN useradd --home /home/studentenportal -u $UID -g $GID -M studentenportal

COPY --from=builder /install /usr/local

RUN mkdir -p /srv/www/studentenportal
WORKDIR /srv/www/studentenportal

RUN mkdir -p /srv/www/studentenportal/media && chown -R studentenportal:studentenportal /srv/www/studentenportal
VOLUME ["/srv/www/studentenportal/media"]
VOLUME ["/srv/www/studentenportal/"]

ENV PATH=/usr/local/bin/:$PATH
USER studentenportal
CMD ["./deploy/dev/start.sh"]
