# This file create a "studentenportal" image for the production deployment
#  of the studentenportal.
# Images have the same versioning as the studentenportal itself,
#  and are uploaded to dockerhub.
FROM studentenportal/base:2.7-1
ARG UID=1000
ARG GID=1000

RUN groupadd -g $GID studentenportal
RUN useradd --home /home/studentenportal -u $UID -g $GID -M studentenportal

COPY requirements/ /tmp/requirements/
RUN pip install -r /tmp/requirements/base.txt -r /tmp/requirements/production.txt && rm -r /tm/requirements

RUN mkdir -p /srv/www/studentenportal
WORKDIR /srv/www/studentenportal

# We only add a minimal set of files needed for production.
RUN mkdir media static
# TODO: Does this copy the contents of apps into ...portal/ or the whole folder?
COPY apps config LICENSE.txt manage.py setup.py deploy/production/start.sh /srv/www/studentenportal/
RUN chown -R studentenportal:studentenportal /srv/www/studentenportal/

VOLUME ["/srv/www/studentenportal/media"]
VOLUME ["/srv/www/studentenportal/static"]

ENV PATH /usr/local/bin/:$PATH
USER studentenportal
CMD ["./start.sh"]
