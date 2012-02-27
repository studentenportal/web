# encoding=utf-8
import os
import random
import datetime
from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User


class Lecturer(models.Model):
    """A lecturer at HSR.

    If there is a photo of that lecturer, it should go into the media folder
    and the filename should be <abbreviation>.jpg.

    """
    id = models.IntegerField(u'HSR ID', primary_key=True)
    title = models.CharField(u'Titel', max_length=32, null=True, blank=True)
    last_name = models.CharField(u'Name', max_length=255)
    first_name = models.CharField(u'Vorname', max_length=255)
    abbreviation = models.CharField(u'Kürzel', max_length=10, unique=True)
    department = models.CharField(u'Abteilung', max_length=32, null=True, blank=True)
    function = models.CharField(u'Funktion', max_length=32, null=True, blank=True)
    main_area = models.CharField(u'Fachschwerpunkt', max_length=256, null=True, blank=True)
    subjects = models.CharField(max_length=50, null=True, blank=True)  # todo add to frontend
    description = models.TextField(null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    office = models.CharField(max_length=20, null=True, blank=True)

    def name(self):
        parts = filter(None, [self.title, self.last_name, self.first_name])
        return ' '.join(parts)

    def photo(self):
        """Try to see if a photo with the name <self.id>.jpg exists. If it
        does, return the corresponding URL. If it doesn't, return None."""
        path = os.path.join('lecturers', '%s.jpg' % self.id)
        fullpath = os.path.join(settings.MEDIA_ROOT, path)
        if os.path.exists(fullpath):
            return settings.MEDIA_URL + path
        return None

    def avg_rating_d(self):
        r = '%u.%u' % (random.randint(1, 5), random.randint(0, 9))
        return float(r)

    def avg_rating_m(self):
        r = '%u.%u' % (random.randint(1, 5), random.randint(0, 9))
        return float(r)

    def avg_rating_f(self):
        r = '%u.%u' % (random.randint(1, 5), random.randint(0, 9))
        return float(r)

    def __unicode__(self):
        return '%s %s' % (self.last_name, self.first_name)

    class Meta:
        ordering = ['last_name']


class Quote(models.Model):
    """Lecturer quotes."""
    author = models.ForeignKey(User, related_name='Quote')
    lecturer = models.ForeignKey(Lecturer, verbose_name=u'Dozent', related_name='Quote')
    date = models.DateTimeField(auto_now_add=True)
    quote = models.TextField(u'Zitat')
    comment = models.TextField(u'Bemerkung', default=u'', blank=True)

    class Meta:
        ordering = ['-date']


class DocumentCategory(models.Model):
    """Categories (usually subjects) for the documents.

    A document can have several categories.

    """
    # TODO prevent duplicate entries http://stackoverflow.com/questions/1857822/unique-model-field-in-django-and-case-sensitivity-postgres
    name = models.CharField(u'Kürzel', max_length=32, unique=True,
            help_text=u'z.B. "CompT1" oder "Prog3"')
    description = models.CharField(u'Voller Name', max_length=255,
            help_text=u'z.B. "Computertechnik 1" oder "Programmieren 3"')

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = u'Modul'


class Document(models.Model):
    """A document that can be uploaded by students.

    A document can have a description, categories, ratings, etc...

    """
    name = models.CharField(u'Titel', max_length=64, unique=True)
    description = models.CharField(u'Beschreibung', max_length=255, blank=True)
    document = models.FileField(u'Datei', upload_to='documents')
    uploader = models.ForeignKey(User, related_name=u'Document', null=True, on_delete=models.SET_NULL)
    upload_date = models.DateTimeField(u'Uploaddatum', auto_now_add=True)
    category = models.ForeignKey(DocumentCategory, related_name=u'Document', null=True, on_delete=models.SET_NULL)

    def rating_exact(self):
        """Return exact rating average."""
        ratings = self.DocumentRating.values_list('rating', flat=True)
        total = sum(ratings)
        return float(total) / len(ratings)

    def rating(self):
        """Return rounded rating average."""
        return int(round(self.rating_exact()))

    def filename(self):
        """Return filename of uploaded file without directories."""
        return os.path.basename(self.document.name)

    def fileext(self):
        """Return file extension by splitting at last occuring period."""
        return self.document.name.split('.')[-1]

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ('-upload_date',)


class DocumentRating(models.Model):
    """Rating for a document.

    Valid values are integers between 1 and 5.

    """
    def validate_rating(value):
        if value not in range(1, 6):
            raise ValidationError(u'Rating must be between 1 and 5, not %s.' % value)

    user = models.ForeignKey(User, related_name=u'DocumentRating')
    document = models.ForeignKey(Document, related_name='DocumentRating')
    rating = models.PositiveSmallIntegerField(validators=[validate_rating])

    # Custom model validation
    def clean(self):
        if self.user == self.document.uploader:
            raise ValidationError(u'A user cannot rate his own uploads.')

    def __unicode__(self):
        return 'User %s Document %s Rating %u' % (self.user.username, self.document.name, self.rating)

    class Meta:
        unique_together = ('user', 'document')


class Event(models.Model):
    """An event.

    If end_date is null, then assume end_date = start_date.

    """
    summary = models.CharField(u'Titel', max_length=64)
    description = models.TextField(u'Beschreibung')
    author = models.ForeignKey(User, related_name='Event')
    start_date = models.DateField(u'Startdatum',
        help_text=u'Format: dd.mm.YYYY')
    start_time = models.TimeField(u'Startzeit', null=True, blank=True,
        help_text=u'Format: hh:mm')
    end_date = models.DateField(u'Enddatum', null=True, blank=True,
        help_text=u'Format: dd.mm.YYYY')
    end_time = models.TimeField(u'Endzeit', null=True, blank=True,
        help_text=u'Format: hh:mm')

    def is_over(self):
        """Return whether the start_date has already passed or not.
        On the start_date day itself, is_over() will return False."""
        delta = self.start_date - datetime.date.today()
        return delta.days < 0

    def all_day(self):
        """Return whether the event runs all day long.
        This is the case if start_time and end_time are not set."""
        return self.start_time == self.end_time == None

    def days_until(self):
        """Return how many days are left until the day of the event."""
        delta = self.start_date - datetime.date.today()
        return delta.days if delta.days > 0 else None

    def __unicode__(self):
        return '%s %s' % (self.start_date, self.summary)


def name(self):
    """Return either full user first and last name or the username, if no
    further data is found."""
    if self.first_name or self.last_name:
        return ' '.join(filter(None, [self.first_name, self.last_name]))
    return self.username
User.add_to_class('name', name)
