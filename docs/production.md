# Installation

## Prerequisites

* Systemd (already installed in Ubuntu > 16.04)
* [Docker](https://docs.docker.com/engine/installation/linux/ubuntu/#install-docker)
* inotify `sudo apt-get install inotify-tools`
* OpenSSH Server - probably pre-installed. Otherwise install it on Ubuntu via `sudo apt-get install openssh-server`


# Configuration

```bash
git clone https://github.com/studentenportal/web /opt/studentenportal
```

## Postgres

Install and enable the systemd service:

```bash
systemctl link docs/production/systemd/studentenportal-postgres.service
systemctl enable studentenportal-postgres.service
systemctl start studentenportal-postgres.service
```

## Studentenportal

Create and edit configuration file:

```bash
cp docs/production/studentenportal.env /etc/
vim /etc/studentenportal.env
```

Replace the `###values###` in the file. For the `POSTGRES_PASSWORD` and `SECRET_KEY` field, it is best to generate a random secret, e.g.: `dd if=/dev/urandom bs=20 count=1 status=none | xxd -ps`

Create systemd service:

```bash
systemctl link docs/production/systemd/studentenportal.service
systemctl enable studentenportal.service
systemctl start studentenportal.service
```

## Nginx reverse-proxy to serve static files

On our production system, we do:
```bash
ln -s /opt/studentenportal/docs/production/nginx/ /etc/nginx
```

but as you probably want to use the system on a different domain:

```bash
cp /opt/studentenportal/docs/production/nginx /etc/
```

... and customize the configuration to your need.

Create systemd service:

```bash
systemctl link docs/production/systemd/nginx.service
systemctl enable nginx.service
systemctl start nginx.service
```

### Let's Encrypt certificates with Dehydrated

Dehydrated is a ACME client to create free Let's Encrypt TLS-certificates.

```bash
cp /opt/studentenportal/docs/production/dehydrated /etc/
```

Adjust the domainnames to your needs in the file `/etc/dehydrated/domains.txt`

Create systemd service and timer:

```bash
systemctl link docs/production/systemd/dehydrated.service
systemctl link docs/production/systemd/dehydrated.timer
systemctl enable dehydrated.timer
```

### Certificates generation on the first run or the chicken-egg problem

On the first run, nginx won't start because you don't have ssl certificates yet. This is a bit unfortunate, as a running nginx is needed to generate certificates...

For this usecase, we prepared a small nginx-configuration, that temporarly allows the generation of Let's Encrypt certificates for any domain that points to the server.

Important: This only works with a correct dehydrated configuration and service from above!

- TODO: stripped down oneshot run

# Updates

- TODO: Database changes? -> probably always apply, as we want rolling deploy on successfull tests.
- TODO: Container Dockerhub build after successfull tests
- TODO: Service restart after successfull Dockerhub update
  - Database Backup first?!
  - Graceful restart?
