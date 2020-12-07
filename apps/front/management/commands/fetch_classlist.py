# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

import getpass
import re
import sys
import time
from optparse import make_option

from django.core.management.base import BaseCommand

from apps.documents import models as document_models
from apps.front.management.commands.fetch_photos import UnterrichtWebsite
from apps.lecturers import models as lecturer_models


class Command(BaseCommand):
    help = """Add all lecturers from classlist to modules and all students to
    the modules."""
    option_list = BaseCommand.option_list + (
        make_option("--user", dest="username", help="HSR username"),
        make_option("--pass", dest="password", help="HSR password"),
    )

    def parse_student_table(self, table):
        for row in table.find_all("tr")[2:]:
            try:
                yield {
                    "pld": int(row.find_all("div", {"class": "a199"})[0].text.strip()),
                    "last_name": row.find_all("a", {"class": "a201"})[0].text.strip(),
                    "first_name": row.find_all("div", {"class": "a207"})[
                        0
                    ].text.strip(),
                    "email": row.find_all("a", {"class": "a209"})[0].text.strip(),
                    "abt": row.find_all("div", {"class": "a215"})[0].text.strip(),
                    "wl_pos": int(
                        row.find_all("div", {"class": "a231"})[0].text.strip()
                    ),
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
        for unit in course_units.find_all("option")[1:]:
            unit_id = int(unit["value"].split(";")[2])
            try:
                course_unit_list = hsr.get_class_list(
                    module_id=module_id, course_id=course_id, course_unit_id=unit_id
                )
                lecturer = course_unit_list.content.find_all("a", {"class": "a58"})[
                    0
                ].text
                match = re.match("(.*)\((.*)\)", lecturer)

                abbr = match.groups(2)
                name = match.groups(1)

                if abbr not in lecturers:
                    lecturers[abbr] = name
            except:
                self.stderr.write(
                    "Could not parse lecturers in {0};{1};{2}: {3}".format(
                        module_id, course_id, unit_id, sys.exc_info()[0]
                    )
                )

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
            course_list = hsr.get_class_list(
                module_id=module_id, course_id=module_id + 1
            )
            abbr = course_list.content.find_all("a", {"class": "a40"})[0].text
            student_count = int(
                course_list.content.find_all("div", {"class": "a125"})[0].text
            )
            table = course_list.content.find_all("table", {"class": "a292"})[0]
            students = self.parse_student_table(table)
            lecturers = self.parse_lecturers_of_course_units(
                hsr, module_id, module_id + 1, course_list.course_units
            )
            return {
                "abbr": abbr,
                "student_count": student_count,
                "students": students,
                "lecturers": lecturers,
            }
        except:
            self.stderr.write(
                "Could not parse module {0}: {1}".format(module_id, sys.exc_info()[0])
            )

    def get_document_category(self, abbr):
        try:
            return document_models.DocumentCategory.objects.get(name=abbr)
        except document_models.DocumentCategory.DoesNotExist:
            self.stderr.write("Could not find DocumentCategory {0}".format(abbr))

    def add_lecturers_to_document_category(self, lecturers, category):
        """Try to find all the lecturers in the database and add them to the
        category if the category exists as well.
        returns: Tuple of added lecturers and failed lecturers or none if category
        does not exist
        """
        added_lecturers = []
        failed_lecturers = []

        for name, abbr in lecturers:
            try:
                lecturer = lecturer_models.Lecturer.objects.get(abbreviation=abbr)
                category.lecturers.add(lecturer)
                added_lecturers.append(name)
            except lecturer_models.Lecturer.DoesNotExist:
                failed_lecturers.append(name)
                self.stderr.write(
                    "Could not find Lecturer {0} ({1})".format(name, abbr)
                )

        category.save()
        return (added_lecturers, failed_lecturers)

    def get_module_ids(self, hsr):
        """Extract module ids from the options of the initial list"""
        initial_list = hsr.get_class_list()
        options = initial_list.modules.find_all("option")[1:]
        return [int(option["value"]) for option in options]

    def handle(self, **options):
        """Parse all modules from the select list from
        Aktuelles Semester > Module > Klassenliste and call the site again for the
        id of each module and parse it with parse_module."""
        assert "username" in options, "--user argument required"
        assert options["username"], "--user argument required"

        if not ("password" in options and options["password"]):
            options["password"] = getpass.getpass("HSR Password: ").strip()

        # Initialize counters
        added_lecturers = []
        failed_lecturers = []
        updated_categories = []
        failed_categories = []

        # Initialize HsrWebsite object to fetch person IDs
        hsr = UnterrichtWebsite()
        hsr.login(options["username"], options["password"])

        for module_id in self.get_module_ids(hsr):

            module = self.parse_module(hsr, module_id)
            category = self.get_document_category(module["abbr"])
            lecturers = module["lecturers"]
            students = module["students"]

            if category:
                lecturer_results = self.add_lecturers_to_document_category(
                    lecturers, category
                )
                added_lecturers.extend(lecturer_results[0])
                failed_lecturers.extend(lecturer_results[1])
                self.stdout.write(
                    "Added {0} lecturer to module {1} and {2} failed".format(
                        len(lecturer_results[0]),
                        module["abbr"],
                        len(lecturer_results[1]),
                    )
                )

                updated_categories.append(module["abbr"])
            else:
                failed_categories.append(module["abbr"])

        # Remove duplicates
        added_lecturers = set(added_lecturers)
        failed_lecturers = set(failed_lecturers)

        self.stdout.write(
            "Updated {0} modules: {1}".format(
                len(updated_categories), ",".join(updated_categories)
            )
        )
        self.stdout.write(
            "Failed {0} modules: {1}".format(
                len(failed_categories), ",".join(failed_categories)
            )
        )
        self.stdout.write(
            "Added {0} lecturers: {1}".format(
                len(added_lecturers), ",".join(added_lecturers)
            )
        )
        self.stdout.write(
            "Failed {0} lecturers: {1}".format(
                len(failed_lecturers), ",".join(failed_lecturers)
            )
        )

        end = time.time()
        self.stdout.write(
            "Used {0} to parse all the modules and lecturers.".format(end)
        )
