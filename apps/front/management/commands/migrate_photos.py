# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

import re
import os
import types

from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.files.storage import default_storage
from django.core.files.base import File

from apps.lecturers.models import Lecturer, LecturerPhoto


def patch(lecturer):
        """Patches lecturer objects back to the latest version so they can be migrated"""

        def photo(self):
            """Try to see if a photo with the name <self.id>.jpg exists. If it
            does, return the corresponding URL. If it doesn't, return None."""

            path = os.path.join('lecturers', '%s.jpg' % self.id)
            fullpath = os.path.join(settings.MEDIA_ROOT, path)
            return path if os.path.exists(fullpath) else None

        def oldphotos(self):
            """Try to see whether there are more pictures in the folder
            ``lecturers/old/<self.id>/``..."""

            path = os.path.join('lecturers', 'old', str(self.id))
            fullpath = os.path.join(settings.MEDIA_ROOT, path)
            oldphotos = []
            if os.path.exists(fullpath):
                for filename in os.listdir(fullpath):
                    if re.match(r'^[0-9]+\.jpg$', filename):
                        filepath = os.path.join(path, filename)
                        oldphotos.append(filepath)
            return oldphotos

        lecturer.photo = types.MethodType(photo, lecturer)
        lecturer.oldphotos = types.MethodType(oldphotos, lecturer)


class Command(BaseCommand):
    help = 'Migrate lecturer photos to the LecturerPhoto model.'

    def handle(self, **options):
        processed_count = 0
        migrated_count = 0
        migrated_old_count = 0
        skipped_no_image_count = 0
        skipped_migrated_count = 0
        skipped_migrated_old_count = 0

        lecturers = Lecturer.objects.all()
        for lecturer in lecturers:
            processed_count += 1
            patch(lecturer)

            if not lecturer.photo() and len(lecturer.oldphotos()) == 0:
                self.stdout.write("SKIPPED (NO IMAGE): {0}".format(lecturer.name()))
                skipped_no_image_count += 1

            if lecturer.photo():
                if len(lecturer.lecturerphoto_set.all()) == 0:
                    with default_storage.open(lecturer.photo()) as file_handle:
                        lecturer_photo = LecturerPhoto(lecturer=lecturer)
                        lecturer_photo.photo.save(os.path.basename(lecturer.photo()),
                                                  File(file_handle))
                        lecturer_photo.save()
                    self.stdout.write("MIGRATED PHOTO: {0}".format(lecturer.name()))
                    migrated_count += 1
                else:
                    self.stdout.write("SKIPPED (ALREADY MIGRATED): {0}".format(lecturer.name()))
                    skipped_migrated_count += 1

            if len(lecturer.oldphotos()) > 0:
                if len(lecturer.lecturerphoto_set.all()) <= 1:
                    for photo_path in lecturer.oldphotos():
                        with default_storage.open(photo_path) as file_handle:
                            lecturer_photo = LecturerPhoto(lecturer=lecturer)
                            lecturer_photo.photo.save(os.path.basename(photo_path),
                                                      File(file_handle))
                            lecturer_photo.save()
                    self.stdout.write("MIGRATED OLD PHOTO: {0}".format(lecturer.name()))
                    migrated_old_count += 1
                else:
                    self.stdout.write("SKIPPED OLD PHOTO (ALREADY MIGRATED): {0}"
                                      .format(lecturer.name()))
                    skipped_migrated_old_count += 1

        self.stdout.write('Processed {0} lecturers.'.format(processed_count))
        self.stdout.write('Migrated {0} photos.'.format(migrated_count))
        self.stdout.write('Migrated {0} old photos.'.format(migrated_old_count))
        self.stdout.write('Skipped {0} photos (no images).'.format(skipped_no_image_count))
        self.stdout.write('Skipped {0} photos (already migrated).'.format(skipped_migrated_count))
        self.stdout.write('Skipped {0} old photos (already migrated).'
                          .format(skipped_migrated_old_count))
