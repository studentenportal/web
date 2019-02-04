# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

from datetime import date

from django.db import models
from django.conf import settings


def picture_file_name(instance, filename):
    """Where to put a newly uploaded picture."""
    return '/'.join(['event_pictures', str(instance.start_date.year), filename])

class Event(models.Model):
    """An event.
    If end_date is null, then assume end_date = start_date.
    """

    author = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='Event', null=True,
            on_delete=models.SET_NULL)
    summary = models.CharField('Titel', max_length=64)
    description = models.TextField('Beschreibung')
    start_date = models.DateField('Startdatum',
            help_text='Format: dd.mm.YYYY')
    start_time = models.TimeField('Startzeit', null=True, blank=True,
            help_text='Format: hh:mm')
    end_date = models.DateField('Enddatum', null=True, blank=True,
            help_text='Format: dd.mm.YYYY')
    end_time = models.TimeField('Endzeit', null=True, blank=True,
            help_text='Format: hh:mm')
    location = models.CharField('Ort', max_length=80, null=True, blank=True,
            help_text='Veranstaltungsort, zB "Gebäude 3" oder "Bären Rapperswil"')
    url = models.URLField('URL', null=True, blank=True,
            help_text='URL zu Veranstaltungs-Website')
    picture = models.ImageField('Bild/Flyer', upload_to=picture_file_name, null=True, blank=True,
            help_text='Bild oder Flyer')

    def is_over(self):
        """Return whether the start_date has already passed or not.
        On the start_date day itself, is_over() will return False."""
        delta = self.start_date - date.today()
        return delta.days < 0

    def all_day(self):
        """Return whether the event runs all day long.
        This is the case if start_time and end_time are not set."""
        return self.start_time is None and self.end_time is None

    def days_until(self):
        """Return how many days are left until the day of the event."""
        delta = self.start_date - date.today()
        return delta.days if delta.days > 0 else None

    def __unicode__(self):
        return '%s %s' % (self.start_date, self.summary)
