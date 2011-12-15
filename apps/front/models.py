import os
import random
from django.conf import settings
from django.db import models

class Lecturer(models.Model):
    name = models.CharField(max_length=255, primary_key=True)
    abbreviation = models.CharField(max_length=10, unique=True)
    subjects = models.CharField(max_length=50, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    
    def photo(self):
        path = os.path.join(settings.MEDIA_ROOT, 'lecturers', '%s.jpg' % self.abbreviation.lower())
        if os.path.exists(path):
            return settings.MEDIA_URL + 'lecturers/%s.jpg' % self.abbreviation.lower()
        return None

    def avg_rating_d(self):
        return '%u.%u' % (random.randint(1, 5), random.randint(0, 9))

    def avg_rating_m(self):
        return '%u.%u' % (random.randint(1, 5), random.randint(0, 9))

    def avg_rating_f(self):
        return '%u.%u' % (random.randint(1, 5), random.randint(0, 9))

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ['name']
