# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

import re
import sys
from optparse import make_option

from django.core.management.base import BaseCommand

from apps.front.management.commands.fetch_photos import UnterrichtWebsite


class Command(BaseCommand):
    help = 'Fetch all students and lecturers from the classlist of each module.'
    option_list = BaseCommand.option_list + (
        make_option('--user', dest='username', help='HSR username'),
        make_option('--pass', dest='password', help='HSR password'),
    )

    def parse_student_table(self, table):
        for row in table.find_all('tr')[2:]:
            try:
                yield {
                    'pld': int(row.find_all('div', {'class': 'a199'})[0].text),
                    'last_name': row.find_all('a', {'class': 'a201'})[0].text,
                    'first_name': row.find_all('div', {'class': 'a207'})[0].text,
                    'email': row.find_all('a', {'class': 'a209'})[0].text,
                    'abt': row.find_all('div', {'class': 'a215'})[0].text,
                    'wl_pos': int(row.find_all('div', {'class': 'a231'})[0].text)
                }
            except:
                self.stderr.write("Could not parse student: " + sys.exc_info()[0])

    def parse_lecturers_of_course_units(self, hsr, module_id, course_id, course_units):
        """Extract the list of course units and call the site with the specific parameter
        of the course unit.
        This will list the lecturer who supervises the exercise or lection.
        We can then create a set of the lecturers to get a unique list of all lecturers
        who are associated with this module.
        :returns set of unique lecturers
        """
        lecturers = {}
        for unit in course_units.find_all('option')[1:]:
            unit_id = int(unit['value'].split(';')[2])
            try:
                course_unit_list = hsr.get_class_list(module_id=module_id,
                                                      course_id=course_id,
                                                      course_unit_id=unit_id)
                lecturer = course_unit_list.content.find_all('a', {'class': 'a58'})[0].text
                match = re.match('(.*)\((.*)\)', lecturer)

                abbr = match.groups(2)
                name = match.groups(1)

                if not abbr in lecturers:
                    lecturers[abbr] = name
            except:
                self.stderr.write("Could not parse lecturers in {0};{1};{2}: {3}"\
                                  .format(module_id, course_id, unit_id,sys.exc_info()[0]))

        return set(lecturers)

    def parse_module(self, hsr, module_id):
        """Instead of parsing the overview of the current module, we go directly to the
        course itself, which is usually simple the module_id incremented by one.
        From this overview we can extract the abbreviation, the amount of registered
        students and all of the students itself (from the table).
        The lecturers have to be aggregated from all the different course units,
        because they are not all together listed on one page.
        :returns dictionary with all the important properties of a module
        """
        try:
            course_list = hsr.get_class_list(module_id=module_id,course_id=module_id+1)
            abbr = course_list.content.find_all('a', {'class': 'a40'})[0].text
            student_count = int(course_list.content.find_all('div', {'class': 'a125'})[0].text)
            table = course_list.content.find_all('table', {'class': 'a292'})[0]
            students = self.parse_student_table(table)
            lecturers = self.parse_lecturers_of_course_units(hsr,
                                                             module_id,
                                                             module_id+1,
                                                             course_list.course_units)
            return {
                'abbr':abbr,
                'student_count': student_count,
                'students': students,
                'lecturers':lecturers
            }
        except:
            self.stderr.write("Could not parse module {0}: {1}"\
                              .format(module_id, sys.exc_info()[0]))

    def handle(self, **options):
        """Parse all modules from the select list from
        Aktuelles Semester > Module > Klassenliste and call the site again for the
        id of each module and parse it with parse_module."""
        assert 'username' in options, '--user argument required'
        assert options['username'], '--user argument required'

        if not ('password' in options and options['password']):
            options['password'] = getpass.getpass('HSR Password: ').strip()

        # Initialize HsrWebsite object to fetch person IDs
        hsr = UnterrichtWebsite()
        hsr.login(options['username'], options['password'])

        # Load the initial class list to extract modules
        initial_list = hsr.get_class_list()
        options = initial_list.modules.find_all('option')[1:]
        module_ids = [int(option['value']) for option in options]
        for module_id in module_ids:
            module = self.parse_module(hsr, module_id)
            self.stdout.write("ID: {0}\tABBR: {1}\tCOUNT:{2}"\
                              .format(module_id,
                                      module['abbr'],
                                      module['student_count']))
            self.stdout.write("STUDENTS:" + ",".join([s['email'] for s in module['students']]))
            self.stdout.write("LECTURERS:" + ",".join([str(l) for l in module['lecturers']]))
