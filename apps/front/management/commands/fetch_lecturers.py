import urllib2
from BeautifulSoup import BeautifulSoup
from django.core.management.base import NoArgsCommand
from apps.front.models import Lecturer
from django.db import IntegrityError


URL = 'https://unterricht.hsr.ch/staticWeb/Ba_Dozentenabkuerzungen.html'


class Command(NoArgsCommand):
    help = 'Fetch lecturers and write them into the database.'

    def printO(self, message):
        self.stdout.write(message + '\n')

    def printE(self, message):
        self.stderr.write(message + '\n')

    def handle_noargs(self, **options):
        # Fetch HTML
        self.printO('Fetching HTML...')
        request = urllib2.urlopen(URL)
        html = request.read()

        # Parse data
        self.printO('Parsing HTML...')
        soup = BeautifulSoup(html)
        table = soup.find('table')
        rows = table.findAll('tr')[1:]
        lecturers = [tuple(td.text for td in row.findAll('td')) for row in rows]

        # Write data into database
        self.printO('Writing to database...')
        added = 0
        for lecturer in lecturers:
            l = Lecturer()
            l.abbreviation = lecturer[0]
            l.name = lecturer[1]
            try:
                l.save()
            except IntegrityError:
                self.printE("Could not add %s." % repr(lecturer))
            else:
                self.printO("Added %s." % repr(lecturer))
                added += 1

        self.printO("\nParsed %u lecturers." % len(lecturers))
        self.printO("Added %u lecturers." % added)
