# This file create a "studentenportal" image for the production deployment
#  of the studentenportal.
# Images have the same versioning as the studentenportal itself,
#  and are uploaded to dockerhub.
FROM studentenportal/base:3.7-0
ARG UID=1001
ARG GID=1001

RUN groupadd -g $GID studentenportal
RUN useradd --home /home/studentenportal -u $UID -g $GID -M studentenportal

COPY requirements/ /tmp/requirements/
RUN python3 -m pip --quiet install -U pip setuptools wheel
RUN python3 -m pip --quiet install -r /tmp/requirements/base/requirements.txt -r /tmp/requirements/production/requirements.txt && rm -r /tmp/requirements

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

ENV PATH /usr/local/bin/:$PATH
USER studentenportal
CMD ["./start.sh"]
