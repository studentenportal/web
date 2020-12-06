FROM unicon/shibboleth-sp:3.0.4

ADD ./shibboleth-sp/ /etc/shibboleth/

RUN /etc/shibboleth/keygen.sh -f -u shibd -h localhost -y 3 -e https://localhost/shibboleth -o /etc/shibboleth