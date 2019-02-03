# This file create a "studentenportal" image for the dev environment.
# Additional packages for dev are added here.
FROM studentenportal/base:2.7-1
ARG UID=1000
ARG GID=1000

RUN groupadd -g $GID studentenportal
RUN useradd --home /home/studentenportal -u $UID -g $GID -M studentenportal

COPY requirements/ /tmp/requirements/
RUN pip --quiet install -U pip
RUN pip --quiet install -r /tmp/requirements/base.txt -r /tmp/requirements/local.txt -r /tmp/requirements/testing.txt

RUN mkdir -p /srv/www/studentenportal
WORKDIR /srv/www/studentenportal

RUN mkdir -p /srv/www/studentenportal/media && chown -R studentenportal:studentenportal /srv/www/studentenportal
VOLUME ["/srv/www/studentenportal/media"]
VOLUME ["/srv/www/studentenportal/"]

ENV PATH /usr/local/bin/:$PATH
USER studentenportal
CMD ["./deploy/dev/start.sh"]
