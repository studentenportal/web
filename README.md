Studentenportal 2.0
===================

[![Build Status](https://secure.travis-ci.org/gwrtheyrn/studentenportal2.png?branch=master)](http://travis-ci.org/gwrtheyrn/studentenportal2)

Dies ist ein re-launch des [HSR Studentenportals](http://studentenportal.ch).
Es soll das alte Portal ablösen und in Sachen Ruhm und Ehre weit überholen.

![f\*ck yeah!](http://s3.amazonaws.com/kym-assets/entries/icons/original/000/001/987/fyeah.jpg)

 * Live-Instanz: http://studentenportal.ch/
 * Travis Buildserver: http://travis-ci.org/gwrtheyrn/studentenportal2


Technologie
-----------

Das neue Studentenportal wird mit Django/Python geschrieben.


Development
-----------

Um die Entwicklungsumgebung einzurichten:

 1. Repository clonen
 2. Python Virtualenv erstellen und aktivieren
 3. `psql -d template1 -c 'CREATE EXTENSION citext;'`
 4. `createuser -e -P -d -E -s studentenportal` (Passwort "studentenportal")
 5. `createdb -e -O studentenportal -U studentenportal studentenportal`
 6. `pip install -r requirements.txt`
 7. `python manage.py syncdb`
 8. `python manage.py migrate`
 9. `python manage.py runserver`


Falls die Datenbank bereits existiert:

 1. `psql -d studentenportal -c 'CREATE EXTENSION citext;'`


Um die Tests auszuführen:

 1. `python manage.py collectstatic`
 2. `python manage.py test front`


Falls ein Datenbankfehler auftritt, weil das Schema sich geändert hat:

 1. `python manage.py syncdb`
 2. `python manage.py migrate`


Features
--------

Featurevorschläge sind willkommen! Aktuell geplante Features und Featurewünsche
können auf https://studentenportal.uservoice.com/ eingesehen, erstellt und
upvoted werden.


Fragen
------

Bei Fragen wende dich an dbargen@hsr.ch oder https://twitter.com/studportal\_hsr.


Lizenz
------

Der Code wird unter der [AGPLv3](http://www.gnu.org/licenses/agpl-3.0.html) veröffentlicht.
