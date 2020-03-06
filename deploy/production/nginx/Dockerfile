FROM nginx:1.17

ARG DEHYDRATED_VERSION=v0.6.5

RUN apt-get update && apt-get install -y apt-utils

RUN apt-get install -y curl bash openssl
ADD https://raw.githubusercontent.com/dehydrated-io/dehydrated/${DEHYDRATED_VERSION}/dehydrated /usr/local/bin/
ADD deploy/production/nginx/dehydrated/config /etc/dehydrated/
ADD deploy/production/nginx/dehydrated/domains.txt /etc/dehydrated/
ADD deploy/production/nginx/dehydrated/hook.sh /etc/dehydrated/
RUN chmod a+x /usr/local/bin/dehydrated \
              /etc/dehydrated/hook.sh && \
    mkdir -p /var/www/dehydrated \
             /etc/dehydrated/certs/studentenportal.ch

ADD deploy/production/nginx/default.conf /etc/nginx/conf.d/
ADD deploy/production/nginx/nginx.conf /etc/nginx/
ADD https://ssl-config.mozilla.org/ffdhe2048.txt /etc/nginx/dhparam.pem

# Set up self-signed snakeoil certificate which later gets replaced by the real
# one.
RUN apt-get install -y ssl-cert
RUN ln -s /etc/ssl/certs/ssl-cert-snakeoil.pem \
    /etc/dehydrated/certs/studentenportal.ch/fullchain.pem
RUN ln -s /etc/ssl/private/ssl-cert-snakeoil.key \
    /etc/dehydrated/certs/studentenportal.ch/privkey.pem

VOLUME [ "/etc/dehydrated" ]
