# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

from django.core.management.base import NoArgsCommand

import requests
from bs4 import BeautifulSoup

from apps.front.models import DocumentCategory
from apps.front.mixins import CommandOutputMixin


blacklist = ['3D-Vis', 'DigT1', 'DigT2', 'MaTechM1', 'MaTechM2', 'ElMasch', 'StReiseR', 'SE2P',
             'MathSem' 'AdpaFw', 'AdpaFwUe', 'ChallP', 'ChallP1', 'ChallP2', 'CEng_MT',
             'CEng_PJ1', 'CEng_PJ2', 'CM_Block', 'ZeiWo', 'WibS']


class Command(CommandOutputMixin, NoArgsCommand):
    help = 'Fetch module descriptions and write them to the database.'

    def handle_noargs(self, **options):
        # Initialize counters
        parsed_count = 0
        existing_count = 0
        invalid_count = 0
        blacklisted_count = 0
        added_count = 0

        r = requests.get('http://studien.hsr.ch/')
        soup = BeautifulSoup(r.content)
        table = soup.find('table')
        rows = table.find_all('tr', recursive=False)
        for row in rows:
            cols = row.find_all('td', recursive=False)

            if len(cols):  # If this is not a header row...

                # Parse data
                description = cols[0].text
                full_name = cols[1].text
                name = full_name.split('_', 1)[1]
                dates = cols[2].text

                # Skip conditions
                if name in blacklist:
                    self.printO('Skipping %s (blacklisted)' % name)
                    blacklisted_count += 1
                    continue
                if not full_name.startswith('M_'):
                    self.printO('Skipping %s (invalid module name)' % name)
                    invalid_count += 1
                    continue
                if 'nicht durchgeführt' in dates:
                    self.printO('Skipping %s (no valid dates)' % name)
                    invalid_count += 1
                    continue
                if description.startswith('Seminar - ') or \
                        description.startswith('Bachelor-Arbeit ') or \
                        description.startswith('Studienarbeit ') or \
                        description.startswith('Projektarbeit ') or \
                        description.startswith('Diplomarbeit '):
                    self.printO('Skipping %s (project or seminary)' % name)
                    invalid_count += 1
                    continue

                parsed_count += 1

                # Create module if new
                try:
                    DocumentCategory.objects.get(name=name)
                except DocumentCategory.DoesNotExist:
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
        self.printO(u'Skipped %u modules (invalid).' % invalid_count)
