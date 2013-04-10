Studentenportal 2.0
===================

[![Build Status](https://secure.travis-ci.org/dbrgn/studentenportal2.png?branch=master)](http://travis-ci.org/dbrgn/studentenportal2)

[![Coverage Status](https://coveralls.io/repos/dbrgn/studentenportal2/badge.png?branch=master)](https://coveralls.io/r/dbrgn/studentenportal2)

Dies ist ein re-launch des [HSR Studentenportals](http://studentenportal.ch).
Es hat das alte Portal im Frühling 2012 abgelöst und soll es in Sachen Ruhm und
Ehre weit überholen.

![f\*ck yeah!](http://s3.amazonaws.com/kym-assets/entries/icons/original/000/001/987/fyeah.jpg)

 * Live-Instanz: http://studentenportal.ch/
 * Travis Buildserver: http://travis-ci.org/dbrgn/studentenportal2


Technologie
-----------

Das neue Studentenportal wird mit Django/Python geschrieben.


Features
--------

 - Upload und Bewertung von Zusammenfassungen, alten Prüfungen etc
 - Events mit iCal Export
 - Faire Dozentenbewertungen
 - Unterrichtszitate
 - Flattr Integration

Featurevorschläge sind willkommen! Aktuell geplante Features und Featurewünsche
können auf https://github.com/gwrtheyrn/studentenportal2/issues eingesehen und
erstellt werden.


Development
-----------

Requirements:

 - Python >= 2.7
 - PostgreSQL >= 9.1
 - PostgreSQL Contrib Pakete (Debian: `postgresql-contrib-9.1`)


Um die Entwicklungsumgebung einzurichten:

 1. Repository clonen
 2. Python Virtualenv erstellen und aktivieren
 3. `psql -d template1 -c 'CREATE EXTENSION citext;'`
 4. `createuser -e -P -d -E -s studentenportal` (Passwort "studentenportal")
 5. `createdb -e -O studentenportal -U studentenportal studentenportal`
 6. `pip install -r requirements/local.txt`
 7. `python manage.py syncdb --all`
 8. `python manage.py migrate --fake`
 9. `python manage.py runserver`


Falls die Datenbank bereits existiert:

 1. `psql -d studentenportal -c 'CREATE EXTENSION citext;'`


Um die Tests auszuführen:

 1. `python manage.py collectstatic`
 2. `python manage.py test front`


Falls ein Datenbankfehler auftritt, weil das Schema sich geändert hat:

 1. `python manage.py syncdb`
 2. `python manage.py migrate`


Testdaten
---------

Testdaten können am einfachsten via django-admin
(`http://localhost:8000/admin`) angelegt werden.

Es gibt aber auch einige Files mit Testdaten im Verzeichnis
`apps/front/fixtures/`. Voraussetzung dafür sind zwei Benutzer mit den
Primärschlüsseln 1 und 2 (am besten mit `python manage.py createsuperuser`
erstellen).

 * Events: `python manage.py loaddata events`

Bei anderen Daten (zB bei den Dozenten) kann man gleich mit echten Daten
arbeiten. Die Daten werden direkt von der HSR Website bezogen. Man braucht
dafür ein funktionierendes HSR Login.

 * Dozenten: `python manage.py fetch_lecturers --user=<hsr-username> --pass=<hsr-passwd>`


Fragen
------

Bei Fragen wende dich an dbargen@hsr.ch oder https://twitter.com/studportal_hsr.


Lizenz
------

Der Code wird unter der [AGPLv3](http://www.gnu.org/licenses/agpl-3.0.html)
veröffentlicht.
