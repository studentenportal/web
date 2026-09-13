# TODO

## goals

- [ ] Events

  - [ ] Tutorate: Wann, wo – Weiteres nach Bedarf
    - [ ] TODO: add recurring event for "Tutorate"
  - [x] Besseres Design der Events
    - [x] fix css oopsie in event list (thumbnail positioning)
    - [ ] fix css oopsie in event list (mobile)
  - [x] Recurring events
    - [x] TODO: testing, show clearer distinction?

- [ ] Tipps & Tricks: unsere Sammlung an Links und Infos

  - [x] Verwalten von Tipps & Tricks durch Studierende
  - [x] Liken von Tipps & Tricks
  - [ ] Kommentieren
    - [ ] Liken von Kommentaren
      - [ ] Kommentieren
        - [ ] Liken von kommentierten Kommentaren
          - [ ] Kommentieren
    - https://github.com/studentenportal/web/issues/104
    - https://github.com/studentenportal/web/issues/76
    - https://github.com/studentenportal/web/issues/63

- [ ] Wünsche/Feedbackformular

- [ ] Zitat/Meme der Woche, Studentenzitate (Vorschlag Jasmin)

- [x] save email addresses in db in lowercase https://github.com/studentenportal/web/issues/678#issuecomment-5083145263

  - [x] also migrate the addresses already present

- [x] login problem

  - [x] add "send verification mail again" button

## technical

- [ ] updates/upgrades
  - [x] pg 12.2 -> 13 !!1!1
  - [x] test if gunicorn 26.0.0 works in prod
  - [x] server: ubuntu 18.04 -> 26.04
    - [x] ubuntu is a pain in my assholes
  - [ ] secure sshd config on new VM (ansible)
  - [x] fix Django deprecation warnings (FORMS_URLFIELD_ASSUME_HTTPS, index_together in DocumentDownload)
  - [ ] update pg to 18/newest
  - [ ] fix Django deprecation warnings (FORMS_URLFIELD_ASSUME_HTTPS, index_together in DocumentDownload)
  - [ ] nginx docker image update
- [x] docker image
  - [x] update python:3.10 (+ remove unnecessary deps?)
  - [x] remove base image completely from web
  - [x] remove/archive base image (github+dockerhub)
- [x] lots of duplicated code between quotes & tipps due to @omega-800 's skill issues
- [ ] svgs instead of fonts for icons
- [x] add robots.txt
- [ ] backup isn't working :((

## yeah...

- [ ] remote: GitHub found 47 vulnerabilities on studentenportal/web's default branch (4 critical, 16 high, 27 moderate). To find out more, visit:
  remote: https://github.com/studentenportal/web/security/dependabot
- [ ] Jul 27 00:03:32 studentenportal systemd\[1\]: Failed to start duply.service - Duply backup.

## testing

- [ ] Register a new user, resend activation email, verify it arrives
- [ ] Wait for key to expire, resend — verify new key works
- [ ] Submit form with unknown email — verify same success message shown
