# Entwickeln

## Einrichten der Entwicklungsumgebung

Die Entwicklungsumgebung hat zwei Abhängigkeiten:

- Docker & docker-compose
- make

Sofern du diese installiert hast, kannst du wie folgt vorgehen:

1. `git clone https://github.com/studentenportal/web.git studentenportal`
2. `cd studentenportal`
3. `make start-dev`
4. Das Studentenportal ist jetzt unter http://localhost:8000 verfügbar.
5. Bei Änderungen am Code, kannst du das Studentenportal mit `make restart-dev` neu starten.
6. Tests mit `make tests` ausführen

Beenden kannst du die Entwicklungsumgebung mit `make stop-dev`.


## Spezialfälle
### Änderungen an der `Dockerfile-base`

Bei Änderungen an der `Dockerfile-base` muss vor dem Starten zuerst das Baseimage neu gebaut werden:

```bash
make Dockerfile-base
```

### Update 
Falls ein Datenbankfehler auftritt, weil das Schema sich geändert hat:

1. `python manage.py syncdb`
2. `python manage.py migrate`

### Twitter
Wenn du die Twitter Einbindung nutzen willst, musst du im Twitter Developer Center eine
App erstellen und folgende Umgebungsvariablen setzen:

- `TWITTER_CONSUMER_KEY`
- `TWITTER_CONSUMER_SECRET`
- `TWITTER_ACCESS_KEY`
- `TWITTER_ACCESS_SECRET`

