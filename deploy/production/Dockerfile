# This file create a "studentenportal" image for the production deployment
#  of the studentenportal.
# Images have the same versioning as the studentenportal itself,
#  and are uploaded to dockerhub.
FROM studentenportal/base:2.7-0

VOLUME ["srv/www/studentenportal/static"]

ADD requirements/production.txt /tmp/requirements/production.txt
RUN pip install -r /tmp/requirements/production.txt

# We only add a minimal set of files needed for production.
ADD apps config LICENSE.txt manage.py setup.py deploy/production/start.sh /srv/www/studentenportal/
RUN chown -R studentenportal:studentenportal /srv/www/studentenportal/

#TODO
WORKDIR /srv/www/studentenportal
USER studentenportal

CMD ["./start.sh"]
