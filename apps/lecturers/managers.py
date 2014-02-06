# -*- coding: utf-8 -*-
from django.db import models


class RealLecturerManager(models.Manager):
    """A lecturer manager that tries to filter out all non-lecturers."""

    def get_query_set(self):
        function_excludes = ['Projektmitarbeiter', 'Projektmitarbeiterin']
        department_excludes = ['Gebäudemanagement']
        return super(RealLecturerManager, self) \
                    .get_query_set() \
                    .exclude(function__in=function_excludes) \
                    .exclude(department__in=department_excludes)
