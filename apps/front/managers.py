from django.db import models

class RealLecturerManager(models.Manager):
    """A lecturer manager that tries to filter out all non-lecturers."""

    def get_query_set(self):
        excludes = ['Projektmitarbeiter', 'Projektmitarbeiterin']
        return super(RealLecturerManager, self).get_query_set().exclude(function__in=excludes)
