# Entwickeln

## Einrichten der Entwicklungsumgebung

Die Entwicklungsumgebung benötigt [Docker &
docker-compose](https://www.docker.com/).

Sofern du diese installiert hast, kannst du wie folgt vorgehen:

1. `git clone https://github.com/studentenportal/web.git studentenportal`
2. `cd studentenportal`
3. `docker-compose up -d`
4. Das Studentenportal ist jetzt unter [http://localhost:8000](http://localhost:8000) verfügbar.
5. Bei Änderungen am Code, kannst du das Studentenportal mit `docker-compose restart studentenportal` neu starten.
6. Tests mit `docker-compose run --rm studentenportal ./deploy/dev/test.sh` ausführen

Beenden kannst du die Entwicklungsumgebung mit `docker-compose stop`.

### Logs anschauen

Mit dem Kommando `docker-compose logs` kannst du dir die Logs anzeigen lassen.

## Testbenutzer

Die Registrierung von neuen Benutzern versendet in der Testumgebung keine
E-Mails. Diese werden aber in die Logs geschrieben (Siehe Absatz `Logs
anschauen`).

### Administrator

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


## Spezialfälle

### Änderungen an Dockerfiles oder requirements

Werden requirements oder Dockerfiles angepasst, müssen die Docker-Container mit
`docker-compose build` neu gebaut werden.
