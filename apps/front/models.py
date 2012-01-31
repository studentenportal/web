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
    name = models.CharField(max_length=255, primary_key=True)
    abbreviation = models.CharField(max_length=10, unique=True)
    subjects = models.CharField(max_length=50, null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    def photo(self):
        path = os.path.join(settings.MEDIA_ROOT, 'lecturers',
                '%s.jpg' % self.abbreviation.lower())
        if os.path.exists(path):
            return settings.MEDIA_URL + 'lecturers/%s.jpg' % self.abbreviation.lower()
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
        return self.name

    class Meta:
        ordering = ['name']


class DocumentCategory(models.Model):
    """Categories (usually subjects) for the documents.

    A document can have several categories.

    """
    # TODO prevent duplicate entries http://stackoverflow.com/questions/1857822/unique-model-field-in-django-and-case-sensitivity-postgres
    name = models.CharField(max_length=32, unique=True)
    description = models.CharField(max_length=255, null=True, blank=True)

    def __unicode__(self):
        return self.name


class Document(models.Model):
    """A document that can be uploaded by students.

    A document can have a description, categories, ratings, etc...

    """
    name = models.CharField(max_length=64, unique=True)
    description = models.CharField(max_length=255, blank=True)
    document = models.FileField(upload_to='documents')
    uploader = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    upload_date = models.DateTimeField(auto_now_add=True)
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

    user = models.ForeignKey(User)
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
    
    If end_date is null, then end_date = start_date.
    
    """
    summary = models.CharField(max_length=64)
    description = models.TextField()
    author = models.ForeignKey(User, related_name='Event')
    start_date = models.DateField()
    start_time = models.TimeField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)

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
