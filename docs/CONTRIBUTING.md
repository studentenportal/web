# How to Contribute

We are glad you made all the way up to here, because every help is very welcome.

## Setting up Your Development Environment

### Installing Prerequisites
- [Docker](https://docs.docker.com/get-docker/)
- [docker-compose](https://docs.docker.com/compose/install/)

### Installation
```bash
git clone https://github.com/studentenportal/web.git studentenportal
```

### Run Environment
1. `cd studentenportal`
2. `docker-compose up -d`
3. Studentenportal is now available under [http://localhost:8000](http://localhost:8000)

### Logs
To show logs run the following command.
```bash
docker-compose logs
```

### Additions
#### Dockerfiles / Requirement Changes
If your Dockerfiles or requirements change you have to update the docker containers as following.
```bash
docker-compose build --no-cache
```

## Testing
### Run Tests
```bash
docker-compose run --rm studentenportal_dev ./deploy/dev/test.sh
```

### Test Users

#### Administrator
```
Username: user0
Email:    user0@localhost
Password: user0
```

### Student
```
Username: user1
Email:    user1@localhost
Password: user1
```

## Coding Guidelines
### Formatter
Our codebase is formatted by [black](https://black.readthedocs.io/en/stable/).

### Imports
To sort our imports we use [isort](https://pycqa.github.io/isort/)

