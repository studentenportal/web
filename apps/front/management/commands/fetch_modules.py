# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

import re

from django.core.management.base import NoArgsCommand

import requests
from bs4 import BeautifulSoup

from apps.documents.models import DocumentCategory
from apps.front.mixins import CommandOutputMixin


blacklist = ['3D-Vis', 'DigT1', 'DigT2', 'MaTechM1', 'MaTechM2', 'ElMasch', 'StReiseR', 'SE2P',
             'MathSem' 'AdpaFw', 'AdpaFwUe', 'ChallP', 'ChallP1', 'ChallP2', 'CEng_MT',
             'CEng_PJ1', 'CEng_PJ2', 'CM_Block', 'ZeiWo', 'WibS']


class Command(CommandOutputMixin, NoArgsCommand):
    help = 'Fetch module descriptions and write them to the database.'

    def parse_module_detail_page(self, url):
        """
        Parse a module detail page and return it's extracted properties.
        """
        try:
            r = requests.get(url)
            soup = BeautifulSoup(r.content)

            def get_course(row):
                return re.match('(.*)\(', row.find('strong').text).group(1).strip()

            table = soup.find('tbody', id=re.compile('^modul'))
            course_table = soup.find('tbody', id=re.compile('^kategorieZuordnungen'))
            course_rows = course_table.find_all('div', {'class': 'katZuordnung'})

            return {
                'ects_points': int(table.find('tr', id=re.compile('^Kreditpunkte')).find_all('td')[1].text),
                'objectives': table.find('tr', id=re.compile('^Lernziele')).find_all('td')[1].string,
                'lecturer': table.find('tr', id=re.compile('^dozent')).find_all('td')[1].text,
                'courses': {get_course(row) for row in course_rows}
            }
        except:
            self.stderr.write("Could not parse {0}: {1}", url, sys.exc_info()[0])

    def parse_modules(self, url):
        """
        Parse all modules in the table and their corresponding detail page.
        Returns a dictionary containing all extracted data.
        """
        try:
            r = requests.get(url)
            soup = BeautifulSoup(r.content)
            table = soup.find('table')
            rows = table.find_all('tr', recursive=False)

            for row in rows[1:]: #Skip heading row
                cols = row.find_all('td', recursive=False)

                yield {
                    "url": cols[0].a['href'],
                    "description": cols[0].text,
                    "full_name": cols[1].text,
                    "name": cols[1].text.split('_', 1)[1],
                    "dates": cols[2].text,
                    "detail": self.parse_module_detail_page(cols[0].a['href'])
                }
        except:
            self.stderr.write("Could not parse {0}: {1}", url, sys.exc_info()[0])

    def create_document_category(self, module):
        """
        Create a DocumentCategory in the database if it does not yet exist.
        Returns True if a DocumentCategory was created.
        """
        try:
            DocumentCategory.objects.get(name=module["name"])
            return False
        except DocumentCategory.DoesNotExist:
            DocumentCategory.objects.create(name=module["name"], description=module["description"])
            return True

    def handle_noargs(self, **options):
        # Initialize counters
        parsed_count = 0
        existing_count = 0
        invalid_count = 0
        blacklisted_count = 0
        added_count = 0

        for module in self.parse_modules('http://studien.hsr.ch/'):
            # Skip conditions
            if module["name"] in blacklist:
                self.stdout.write('Skipping %s (blacklisted)' % module["name"])
                blacklisted_count += 1
                continue
            if not module["full_name"].startswith('M_'):
                self.stdout.write('Skipping %s (invalid module name)' % module["name"])
                invalid_count += 1
                continue
            if 'nicht durchgeführt' in module["dates"]:
                self.stdout.write('Skipping %s (no valid dates)' % module["name"])
                invalid_count += 1
                continue
            if module["description"].startswith('Seminar - ') or \
                    module["description"].startswith('Bachelor-Arbeit ') or \
                    module["description"].startswith('Studienarbeit ') or \
                    module["description"].startswith('Projektarbeit ') or \
                    module["description"].startswith('Diplomarbeit '):
                self.stdout.write('Skipping %s (project or seminary)' % module["name"])
                invalid_count += 1
                continue

            parsed_count += 1

            if self.create_document_category(module):
                self.stdout.write('Added %s' % module["name"])
                added_count += 1
            else:
                self.stdout.write(u'Skipping %s (already exists)' % module["name"])
                existing_count += 1

        self.stdout.write(u'\nParsed %u modules.' % parsed_count)
        self.stdout.write(u'Added %u modules.' % added_count)
        self.stdout.write(u'Skipped %u modules (already exist).' % existing_count)
        self.stdout.write(u'Skipped %u modules (blacklist).' % blacklisted_count)
        self.stdout.write(u'Skipped %u modules (invalid).' % invalid_count)
