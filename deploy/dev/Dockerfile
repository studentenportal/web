# This file create a "studentenportal" image for the dev environment.
# Additional packages for dev are added here.
FROM studentenportal/base:2.7-0

VOLUME ["/srv/www/studentenportal/"]

ADD requirements/local.txt /tmp/requirements/local.txt
ADD requirements/testing.txt /tmp/requirements/testing.txt

RUN pip install -r /tmp/requirements/local.txt
RUN pip install -r /tmp/requirements/testing.txt

ENV PATH /usr/local/bin/:$PATH

USER studentenportal
CMD ["./deploy/dev/start.sh"]
