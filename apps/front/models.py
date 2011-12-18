import os
import random
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
    name = models.CharField(max_length=32, unique=True)

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
    category = models.ForeignKey(DocumentCategory, null=True, on_delete=models.SET_NULL)

    def rating_exact(self):
        """Return exact rating average."""
        ratings = self.DocumentRating.values_list('rating', flat=True)
        total = sum(ratings)
        return float(total) / len(ratings)

    def rating(self):
        """Return rounded rating average."""
        return int(round(self.rating_exact()))

    def __unicode__(self):
        return self.name


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
