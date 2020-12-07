# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import re
import sys
from optparse import make_option

import requests
from bs4 import BeautifulSoup
from django.core.management.base import NoArgsCommand

from apps.documents.models import DocumentCategory
from apps.front.mixins import CommandOutputMixin
from apps.lecturers import models as lecturer_models

blacklist = [
    "3D-Vis",
    "DigT1",
    "DigT2",
    "MaTechM1",
    "MaTechM2",
    "ElMasch",
    "StReiseR",
    "SE2P",
    "MathSem" "AdpaFw",
    "AdpaFwUe",
    "ChallP",
    "ChallP1",
    "ChallP2",
    "CEng_MT",
    "CEng_PJ1",
    "CEng_PJ2",
    "CM_Block",
    "ZeiWo",
    "WibS",
]

course_specialisations = {
    "Energy and Environment",
    "Spatial Development & Landscape Architecture",
    "Civil Engineering & Building Technology",
    "Industrial Technologies",
    "Information and Communication Technologies",
    "Automation und Robotik",
    "Public Planning, Construction and Building Technology",
    "Simulationstechnik",
    "Application Design - Cloud Solutions",
    "Software Engineering",
    "Betrieb- und Instandhaltung",
    "Maschinenbau-Informatik",
    "Produktentwicklung",
    "Kunststofftechnik",
    "Network, Security & Cloud-Infrastructure" "Planung und Entwurf urbaner Freiräume",
    "Landschaftsbau- und Management",
    "Landschaftsentwicklung und Gestaltung",
}


class Command(CommandOutputMixin, NoArgsCommand):
    help = "Fetch module descriptions and write them to the database."
    option_list = NoArgsCommand.option_list + (
        make_option(
            "--update",
            action="store_true",
            dest="update",
            default=False,
            help="Update existing modules",
        ),
    )

    def parse_module_detail_page(self, url):
        """
        Parse a module detail page and return its extracted properties.
        """
        try:
            r = requests.get(url)
            soup = BeautifulSoup(r.content)

            def get_course(row):
                return re.match("(.*)\(", row.find("strong").text).group(1).strip()

            table = soup.find("tbody", id=re.compile("^modul"))
            course_table = soup.find("tbody", id=re.compile("^kategorieZuordnungen"))
            course_rows = course_table.find_all("div", {"class": "katZuordnung"})
            courses = {get_course(row) for row in course_rows}

            ects_points_row = table.find("tr", id=re.compile("^Kreditpunkte"))
            objectives_row = table.find("tr", id=re.compile("^Lernziele"))
            lecturer_row = table.find("tr", id=re.compile("^dozent"))

            return {
                "ects_points": int(ects_points_row.find_all("td")[1].text),
                "objectives": objectives_row.find_all("td")[1].string,
                "lecturer": lecturer_row.find_all("td")[1].text,
                "courses": {c for c in courses if c not in course_specialisations}
                # Skip all courses that are only specialications and not real courses
            }
        except KeyboardInterrupt:
            self.stderr.write("Abort.")
            sys.exit(1)
        except:
            self.stderr.write("Could not parse {0}: {1}".format(url, sys.exc_info()[0]))

    def parse_modules(self, url):
        """
        Parse all modules in the table and their corresponding detail page.
        Returns a dictionary containing all extracted data.
        """
        try:
            r = requests.get(url)
            soup = BeautifulSoup(r.content)
            table = soup.find("table")
            rows = table.find_all("tr", recursive=False)

            for row in rows[1:]:  # Skip heading row
                cols = row.find_all("td", recursive=False)

                yield {
                    "url": cols[0].a["href"].strip(),
                    "description": cols[0].text.strip(),
                    "full_name": cols[1].text.strip(),
                    "name": cols[1].text.split("_", 1)[1].strip(),
                    "dates": cols[2].text.strip(),
                    "detail": self.parse_module_detail_page(cols[0].a["href"].strip()),
                }
        except KeyboardInterrupt:
            self.stderr.write("Abort.")
            sys.exit(1)
        except:
            self.stderr.write("Could not parse {0}: {1}".format(url, sys.exc_info()[0]))

    def update_document_category(self, module):
        """Update courses and lecturers of an existing DocumentCategory.
        This is used to add the related courses and lecturers to all the existing modules.
        """
        try:
            category = DocumentCategory.objects.get(name=module["name"])
            self.add_courses_to_document_category(category, module)
            self.add_lecturer_to_document_category(category, module)
            category.save()
        except DocumentCategory.DoesNotExist:
            self.stderr.write(
                "Could not find category {0}: {1}".format(
                    module["name"], sys.exc_info()[0]
                )
            )

    def add_lecturer_to_document_category(self, category, module):
        """Searches for the main lecturer and adds it to the DocumentCategory if he exists"""
        full_name = module["detail"]["lecturer"]
        match = re.match("(.*) (.*)", full_name)
        if match:
            first_name = match.group(1)
            last_name = match.group(2)
            try:
                lecturer = lecturer_models.Lecturer.objects.get(
                    first_name=first_name, last_name=last_name
                )
                category.lecturers.add(lecturer)
            except lecturer_models.Lecturer.DoesNotExist:
                self.stderr.write(
                    "Could not find lecturer {0} {1}: {2}".format(
                        first_name, last_name, sys.exc_info()[0]
                    )
                )
        else:
            self.stderr.write(
                "First and last name of module {0} with lecturer {1} cannot be read".format(
                    module["name"], full_name
                )
            )

    def add_courses_to_document_category(self, category, module):
        """
        Add all courses that are defined in the module to the document category if
        they already exist.
        """
        for course_name in module["detail"]["courses"]:
            try:
                course = lecturer_models.Course.objects.get(name=course_name)
                category.courses.add(course)
            except lecturer_models.Course.DoesNotExist:
                self.stderr.write("Could not find course {0}".format(course_name))

    def create_document_category(self, module):
        """
        Create a DocumentCategory in the database if it does not yet exist.
        Returns True if a DocumentCategory was created.
        """
        try:
            DocumentCategory.objects.get(name=module["name"])
            return False
        except DocumentCategory.DoesNotExist:
            category = DocumentCategory.objects.create(
                name=module["name"], description=module["description"]
            )
            self.add_lecturer_to_document_category(category, module)
            self.add_courses_to_document_category(category, module)
            category.save()
            return True

    def handle_noargs(self, **options):
        # Initialize counters
        parsed_count = 0
        existing_count = 0
        invalid_count = 0
        blacklisted_count = 0
        added_count = 0
        update_count = 0

        for module in self.parse_modules("http://studien.hsr.ch/"):
            # Skip conditions
            if module["name"] in blacklist:
                self.stdout.write("Skipping %s (blacklisted)" % module["name"])
                blacklisted_count += 1
                continue
            if not module["full_name"].startswith("M_"):
                self.stdout.write("Skipping %s (invalid module name)" % module["name"])
                invalid_count += 1
                continue
            if "nicht durchgeführt" in module["dates"]:
                self.stdout.write("Skipping %s (no valid dates)" % module["name"])
                invalid_count += 1
                continue
            if (
                "Seminar" in module["description"]
                or module["description"].startswith("Bachelor-Arbeit")
                or module["description"].startswith("Studienarbeit")
                or module["description"].startswith("Projektarbeit")
                or module["description"].startswith("Masterarbeit")
                or module["description"].startswith("Diplomarbeit")
            ):
                self.stdout.write("Skipping %s (project or seminary)" % module["name"])
                invalid_count += 1
                continue

            parsed_count += 1

            if self.create_document_category(module):
                self.stdout.write("Added %s" % module["name"])
                added_count += 1
            else:
                if options["update"]:
                    self.update_document_category(module)
                    self.stdout.write("Updated %s" % module["name"])
                    update_count += 1
                else:
                    self.stdout.write("Skipping %s (already exists)" % module["name"])
                    existing_count += 1

        self.stdout.write("\nParsed %u modules." % parsed_count)
        self.stdout.write("Added %u modules." % added_count)
        self.stdout.write("Updated %u modules." % update_count)
        self.stdout.write("Skipped %u modules (already exist)." % existing_count)
        self.stdout.write("Skipped %u modules (blacklist)." % blacklisted_count)
        self.stdout.write("Skipped %u modules (invalid)." % invalid_count)
