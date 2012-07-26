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
 3. `pip install -r requirements.txt`
 4. `python manage.py syncdb`
 5. `python manage.py migrate`
 6. `python manage.py runserver`


Um die Tests auszuführen:

 1. `python manage.py collectstatic`
 2. `python manage.py test front`


Falls ein Datenbankfehler auftritt, weil das Schema sich geändert hat:

 1. `python manage.py migrate`


Hinweis: Das Ganze sollte mit der Standard-SQLite-Datenbank funktionieren, es
ist jedoch empfehlenswert direkt eine PostgreSQL Datenbank zu verwenden, da
zwischen den beiden Systemen doch gewisse Unterschiede bestehen...


Features
--------

Featurevorschläge sind willkommen! Momentan in etwa geplant:

 * Zusammenfassungen, Formelsammlungen
 * Dozentenbewertungen
 * Dozentenzitate
 * Twitterintegration (wie genau ist noch unklar)
 * Modul-Reviews
 * Ev. eine Linksammlung


Fragen
------

Bei Fragen wende dich an dbargen@hsr.ch oder https://twitter.com/studportal\_hsr.


Lizenz
------

Der Code wird unter der [AGPLv3](http://www.gnu.org/licenses/agpl-3.0.html) veröffentlicht.
