import requests
import sys
from BeautifulSoup import BeautifulSoup
from django.core.management.base import NoArgsCommand
from apps.front.models import DocumentCategory


blacklist = ['3D-Vis', 'DigT1', 'DigT2', 'MaTechM1',
             'MaTechM2', 'ElMasch', 'StReiseR', 'SE2P']

class Command(NoArgsCommand):
    help = 'Fetch module descriptions and write them to the database.'
    
    def printO(self, msg, newline=True):
        """Print to stdout. This expects unicode strings!"""
        encoding = self.stdout.encoding or sys.getdefaultencoding()
        self.stdout.write(msg.encode(encoding, 'replace'))
        if newline:
            self.stdout.write('\n')

    def printE(self, msg, newline=True):
        """Print to stderr. This expects unicode strings!"""
        encoding = self.stderr.encoding or sys.getdefaultencoding()
        self.stderr.write(msg.encode(encoding, 'replace'))
        if newline:
            self.stdout.write('\n')

    def handle_noargs(self, **options):
        # Initialize counters
        parsed_count = 0
        existing_count = 0
        blacklisted_count = 0
        added_count = 0

        r = requests.get('https://unterricht.hsr.ch/staticWeb/Ba_Modulabkuerzungen.html')
        soup = BeautifulSoup(r.content)
        table = soup.find('table')
        rows = table.findAll('tr', recursive=False)
        for row in rows:
            cols = row.findAll('td', recursive=False)
            if len(cols):
                full_name = cols[0].text
                name = full_name.split('_', 1)[1]
                if not full_name.startswith('M_'):
                        self.printO('Skipping %s (blacklist)' % name)
                        blacklisted_count += 1
                description = cols[1].text
                parsed_count += 1

                try:
                    DocumentCategory.objects.get(name=name)
                except DocumentCategory.DoesNotExist:
                    if name in blacklist:
                        self.printO('Skipping %s (blacklist)' % name)
                        blacklisted_count += 1
                    else:
                        self.printO('Adding %s' % name)
                        DocumentCategory.objects.create(name=name, description=description)
                        added_count += 1
                else:
                    self.printO('Skipping %s (already exists)' % name)
                    existing_count += 1

        self.printO(u'\nParsed %u modules.' % parsed_count)
        self.printO(u'Added %u modules.' % added_count)
        self.printO(u'Skipped %u modules (already exist).' % existing_count)
        self.printO(u'Skipped %u modules (blacklist).' % blacklisted_count)
