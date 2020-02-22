FROM nginx:1.17

ARG DEHYDRATED_VERSION=v0.6.5

# RUN apt install curl bash openssl
ADD https://raw.githubusercontent.com/dehydrated-io/dehydrated/${DEHYDRATED_VERSION}/dehydrated /usr/local/bin/
RUN chmod a+x /usr/local/bin/dehydrated && \
    mkdir -p /var/www/dehydrated /usr/local/etc/dehydrated/
ADD deploy/production/nginx/dehydrated-config /usr/local/etc/dehydrated/config
ADD deploy/production/nginx/domains.txt /usr/local/etc/dehydrated/

ADD deploy/production/nginx/default.conf /etc/nginx/conf.d/
ADD https://ssl-config.mozilla.org/ffdhe2048.txt /etc/nginx/dhparam.pem

VOLUME [ "/etc/nginx/sites" ]
VOLUME [ "/etc/dehydrated" ]
