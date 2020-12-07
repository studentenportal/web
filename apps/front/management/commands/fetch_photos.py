# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

import getpass
import sys
import time
from collections import namedtuple
from optparse import make_option

import requests
from bs4 import BeautifulSoup
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand

from apps.lecturers.models import Lecturer


class UnterrichtWebsite(object):
    """Class to coordinate access to unterricht.hsr.ch."""

    base_url = "https://unterricht.hsr.ch/"
    login_url = (
        "https://adfs.hsr.ch/adfs/ls/?wa=wsignin1.0&wtrealm=https%3a%2f%2f"
        + "unterricht.hsr.ch%3a443%2f&wctx=https%3a%2f%2funterricht.hsr.ch%2f"
    )
    headers = {
        "Accept": "Accept:text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.8,de-CH;q=0.6,de;q=0.4",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.1 (KHTML, like Gecko) "
        + "Chrome/21.0.1180.89 Safari/537.1",
    }
    ClassList = namedtuple(
        "ClassList", ["organizations", "modules", "courses", "course_units", "content"]
    )

    def __init__(self):
        """Initialize requests session."""
        self.s = requests.Session()
        self.s.headers.update(self.headers)

    def logged_in(self):
        if "adfs.hsr.ch" not in self.s.cookies._cookies:
            return False
        if "/adfs/ls" not in self.s.cookies._cookies["adfs.hsr.ch"]:
            return False
        return "MSISAuthenticated" in self.s.cookies._cookies["adfs.hsr.ch"]["/adfs/ls"]

    def login(self, username, password):
        """Login to the internal part of the HSR site."""
        if self.logged_in():
            return

        # Get state data
        login_page = self.s.get(self.login_url)
        soup = BeautifulSoup(login_page.content)
        viewstate = soup.find("input", {"id": "__VIEWSTATE"})["value"]
        eventvalidation = soup.find("input", {"id": "__EVENTVALIDATION"})["value"]
        db = soup.find("input", {"name": "__db"})["value"]
        # Log in to ADFS
        data = {
            "__VIEWSTATE": viewstate,
            "__EVENTVALIDATION": eventvalidation,
            "__db": db,
            "ctl00$ContentPlaceHolder1$UsernameTextBox": username,
            "ctl00$ContentPlaceHolder1$PasswordTextBox": password,
            "ctl00$ContentPlaceHolder1$SubmitButton": "Sign In",
        }
        login_response = self.s.post(self.login_url, data=data)

        # Get state data again
        soup = BeautifulSoup(login_response.content)
        data = {
            "wa": soup.find("input", {"name": "wa"})["value"],
            "wresult": soup.find("input", {"name": "wresult"})["value"],
            "wctx": soup.find("input", {"name": "wctx"})["value"],
        }
        # POST auth data to unterricht.hsr.ch
        self.s.post(self.base_url, data=data)

    def get_person_photo(self, person_id):
        """Fetch the lecturer photos from the Klassenspiegel."""
        assert self.logged_in(), "Not logged in. Please call login()."
        r = self.s.get("https://unterricht.hsr.ch/Content/PersonImage/mkempf")
        print(r.content)
        assert False

    def get_class_list(
        self, organization_id=-1, module_id=-1, course_id=-1, course_unit_id=-1
    ):
        assert self.logged_in(), "Not logged in. Please call login()."
        url = "https://unterricht.hsr.ch/CurrentSem/Reporting/Registrations/Module?\
        organizationUnitId={}&courseUnitId={};{};{}".format(
            organization_id, module_id, course_id, course_unit_id
        )
        r = self.s.get(url)
        soup = BeautifulSoup(r.content)

        organizations = soup.find(id="Parameter_OrganizationUnitId")
        modules = soup.find(id="Parameter_ModuleId")
        courses = soup.find(id="Parameter_CourseId")
        course_units = soup.find(id="Parameter_CourseUnitId")
        content = soup.find(id="reportContent")

        return self.ClassList(organizations, modules, courses, course_units, content)


class Command(BaseCommand):
    help = "Fetch lecturers photos and write them to the file storage."
    option_list = BaseCommand.option_list + (
        make_option("--user", dest="username", help="HSR username"),
        make_option("--pass", dest="password", help="HSR password"),
    )

    def printO(self, msg, newline=True):
        """Print to stdout. This expects unicode strings!"""
        encoding = self.stdout.encoding or sys.getdefaultencoding()
        self.stdout.write(msg.encode(encoding, "replace"))
        if newline:
            self.stdout.write("\n")

    def printE(self, msg, newline=True):
        """Print to stderr. This expects unicode strings!"""
        encoding = self.stderr.encoding or sys.getdefaultencoding()
        self.stderr.write(msg.encode(encoding, "replace"))
        if newline:
            self.stdout.write("\n")

    def handle(self, **options):
        assert "username" in options, "--user argument required"
        assert options["username"], "--user argument required"

        if not ("password" in options and options["password"]):
            options["password"] = getpass.getpass("HSR Password: ").strip()

        # Initialize counters
        processed_count = 0
        added_count = 0
        skipped_count = 0
        notfound_count = 0
        updated_count = 0

        # Initialize HsrWebsite object to fetch person IDs
        hsr = UnterrichtWebsite()
        hsr.login(options["username"], options["password"])

        # Go through all lecturers, try to get photo
        lecturers = Lecturer.objects.all()
        for lecturer in lecturers:
            processed_count += 1

            # Fetch photo from webserver
            photo = hsr.get_person_photo(lecturer.id)
            if not photo:
                self.printO("NOT FOUND: %s" % lecturer.name())
                notfound_count += 1
                continue

            # Try to see if there already is a photo with the same name
            path = "lecturers/%s.jpg" % lecturer.id
            if default_storage.exists(path):
                # Compare binary data
                with default_storage.open(path) as f:
                    fcontent = f.read()
                    if fcontent == photo.getvalue():
                        self.printO("EXISTS: {} ({})".format(lecturer.name(), path))
                        skipped_count += 1
                        continue  # Identic photo already exists
                    # File will be overwritten, save a backup of it
                    bkuppath = "lecturers/old/%s/%u.jpg" % (
                        lecturer.id,
                        int(time.time()),
                    )
                    default_storage.delete(path)  # Delete old file
                    default_storage.save(
                        bkuppath, ContentFile(fcontent)
                    )  # Write to backup
                    self.printO("UPDATE: {} ({})".format(lecturer.name(), path))
                    updated_count += 1
            else:
                self.printO("ADD: {} ({})".format(lecturer.name(), path))
                added_count += 1

            # Save photo to media storage
            default_storage.save(path, ContentFile(photo.getvalue()))

        self.printO("\nProcessed %u lecturers." % processed_count)
        self.printO("Added %u photos." % added_count)
        self.printO("Updated %u photos." % updated_count)
        self.printO("Skipped %u photos (preexisting)." % skipped_count)
        self.printO("Skipped %u photos (not found)." % notfound_count)
