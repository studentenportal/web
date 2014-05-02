# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

import re
import os
from datetime import datetime

from django.conf import settings
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator

from apps.lecturers import managers


class Lecturer(models.Model):
    """A lecturer at HSR.

    If there is a photo of that lecturer, it should go into the media folder
    and the filename should be <abbreviation>.jpg.

    """
    id = models.IntegerField('HSR ID', primary_key=True)
    title = models.CharField('Titel', max_length=32, null=True, blank=True)
    last_name = models.CharField('Name', max_length=255)
    first_name = models.CharField('Vorname', max_length=255)
    abbreviation = models.CharField('Kürzel', max_length=10, unique=True)
    department = models.CharField('Abteilung', max_length=100, null=True, blank=True)
    function = models.CharField('Funktion', max_length=255, null=True, blank=True)
    main_area = models.CharField('Fachschwerpunkt', max_length=255, null=True, blank=True)
    subjects = models.CharField(max_length=50, null=True, blank=True)  # todo add to frontend
    email = models.EmailField(null=True, blank=True)
    office = models.CharField(max_length=20, null=True, blank=True)

    objects = models.Manager()
    real_objects = managers.RealLecturerManager()

    def name(self):
        parts = filter(None, [self.title, self.last_name, self.first_name])
        return ' '.join(parts)

    # TODO rename to _rating_avg
    def _avg_rating(self, category):
        """Calculate the average rating for the given category."""
        qs = self.LecturerRating.filter(category=category)
        if qs.exists():
            ratings = qs.values_list('rating', flat=True)
            return int(round(float(sum(ratings)) / len(ratings)))
        return 0

    def _rating_count(self, category):
        return self.LecturerRating.filter(category=category).count()

    def avg_rating_d(self):
        return self._avg_rating('d')

    def avg_rating_m(self):
        return self._avg_rating('m')

    def avg_rating_f(self):
        return self._avg_rating('f')

    def rating_count_d(self):
        return self._rating_count('d')

    def rating_count_m(self):
        return self._rating_count('m')

    def rating_count_f(self):
        return self._rating_count('f')

    def __unicode__(self):
        return '%s %s' % (self.last_name, self.first_name)

    class Meta:
        ordering = ['last_name']


class LecturerPhoto(models.Model):
    """A photo of a lecturer"""
    def photo_file_name(instance, filename):
        """Where to put a newly uploaded photo."""
        ext = os.path.splitext(filename)[1]
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        instance.original_filename = filename
        return os.path.join('lecturers',
                            instance.lecturer.abbreviation.lower(),
                            "{0}{1}".format(timestamp, ext))

    lecturer = models.ForeignKey(Lecturer)
    photo = models.FileField('Foto', upload_to=photo_file_name)


class LecturerRating(models.Model):
    """A lecturer rating. Max 1 per user, category and lecturer."""
    CATEGORY_CHOICES = (
        ('d', 'Didaktisch'),
        ('m', 'Menschlich'),
        ('f', 'Fachlich'))
    RATING_VALIDATORS = [MaxValueValidator(10), MinValueValidator(1)]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='LecturerRating')
    lecturer = models.ForeignKey(Lecturer, related_name='LecturerRating')
    category = models.CharField(max_length=1, choices=CATEGORY_CHOICES, db_index=True)
    rating = models.PositiveSmallIntegerField(validators=RATING_VALIDATORS, db_index=True)

    def __unicode__(self):
        return '%s %s%u' % (self.lecturer, self.category, self.rating)

    class Meta:
        unique_together = ('user', 'lecturer', 'category')


class Quote(models.Model):
    """Lecturer quotes."""
    author = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='Quote', null=True,
            on_delete=models.SET_NULL)
    lecturer = models.ForeignKey(Lecturer, verbose_name='Dozent', related_name='Quote')
    date = models.DateTimeField(auto_now_add=True)
    quote = models.TextField('Zitat')
    comment = models.TextField('Bemerkung', default='', blank=True)

    def date_available(self):
        return self.date != datetime(1970, 1, 1)

    def vote_sum(self):
        """Add up and return all votes for this quote."""
        up = self.QuoteVote.filter(vote=True).count()
        down = self.QuoteVote.filter(vote=False).count()
        return up - down

    def __unicode__(self):
        return '[%s] %s...' % (self.lecturer, self.quote[:30])

    class Meta:
        ordering = ['-date']
        get_latest_by = 'date'


class QuoteVote(models.Model):
    """Lecturer quotes."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='QuoteVote')
    quote = models.ForeignKey(Quote, related_name='QuoteVote')
    vote = models.BooleanField(help_text='True = upvote, False = downvote')

    def __unicode__(self):
        fmt_args = self.user.username, 'up' if self.vote else 'down', self.quote.pk
        return 'User %s votes %s quote %s' % fmt_args

    class Meta:
        unique_together = ('user', 'quote')


class Course(models.Model):
    """A possible degree course. At the moment only one lecturer is possible"""
    id = models.IntegerField('Studiengang ID', primary_key=True)
    abbreviation = models.CharField('Abkürzung', max_length=10, unique=True)
    name = models.CharField('Titel', max_length=32)

    def __unicode__(self):
        return '%s (%s)' % (self.name, self.abbreviation)
