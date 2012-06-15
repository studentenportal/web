# encoding=utf-8
import os
import datetime
from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
from django.db.models.signals import post_save
from django.utils.safestring import mark_safe


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
    department = models.CharField(u'Abteilung', max_length=100, null=True, blank=True)
    function = models.CharField(u'Funktion', max_length=255, null=True, blank=True)
    main_area = models.CharField(u'Fachschwerpunkt', max_length=255, null=True, blank=True)
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

    def _avg_rating(self, category):
        """Calculate the average rating for the given category."""
        qs = self.LecturerRating.filter(category=category)
        if qs.exists():
            total = sum([r.rating for r in qs])
            return int(round(float(total) / qs.count()))
        return 0

    def avg_rating_d(self):
        return self._avg_rating(u'd')

    def avg_rating_m(self):
        return self._avg_rating(u'm')

    def avg_rating_f(self):
        return self._avg_rating(u'f')

    def __unicode__(self):
        return '%s %s' % (self.last_name, self.first_name)

    class Meta:
        ordering = ['last_name']


class LecturerRating(models.Model):
    """A lecturer rating. Max 1 per user, category and lecturer."""
    CATEGORY_CHOICES = (
        (u'd', 'Didaktisch'),
        (u'm', 'Menschlich'),
        (u'f', 'Fachlich'))

    user = models.ForeignKey(User, related_name=u'LecturerRating')
    lecturer = models.ForeignKey(Lecturer, related_name=u'LecturerRating')
    category = models.CharField(max_length=1, choices=CATEGORY_CHOICES, db_index=True)
    rating = models.PositiveSmallIntegerField(validators=[MaxValueValidator(10), MinValueValidator(1)], db_index=True)

    def __unicode__(self):
        return '%s %s%u' % (self.lecturer, self.category, self.rating)

    class Meta:
        unique_together = ('user', 'lecturer', 'category')


class Quote(models.Model):
    """Lecturer quotes."""
    author = models.ForeignKey(User, related_name='Quote', null=True, on_delete=models.SET_NULL)
    lecturer = models.ForeignKey(Lecturer, verbose_name=u'Dozent', related_name='Quote')
    date = models.DateTimeField(auto_now_add=True)
    quote = models.TextField(u'Zitat')
    comment = models.TextField(u'Bemerkung', default=u'', blank=True)

    def date_available(self):
        return self.date != datetime.datetime(1970, 1, 1)

    def __unicode__(self):
        return u'[%s] %s...' % (self.lecturer, self.quote[:30])

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

    @property
    def summary_count(self):
        return self.Document.filter(dtype=Document.DTypes.SUMMARY).count()

    @property
    def exam_count(self):
        return self.Document.filter(dtype=Document.DTypes.EXAM).count()

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = u'Modul'
        ordering = ['name']


class Document(models.Model):
    """A document that can be uploaded by students.

    A document can have a description, categories, ratings, etc...

    """
    class DTypes(object):
        """Enum-style document type class."""
        SUMMARY=1
        EXAM=2

    def document_file_name(instance, filename):
        """Where to put a newly uploaded document. Also, store original filename."""
        ext = os.path.splitext(filename)[1]
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        instance.original_filename = filename
        return '/'.join(['documents', slugify(instance.category.name), '%s%s' % (timestamp, ext)])

    name = models.CharField(u'Titel', max_length=100)
    description = models.CharField(u'Beschreibung', blank=True, max_length=500,
        help_text='(Max. 500 Zeichen)')
    dtype = models.PositiveSmallIntegerField(u'Typ', choices=(
        (DTypes.SUMMARY, u'Zusammenfassung'),
        (DTypes.EXAM, u'Prüfung')))
    document = models.FileField(u'Datei', upload_to=document_file_name, help_text=u'(Max. 10MB)')
    original_filename = models.CharField(u'Originaler Dateiname', max_length=255, blank=True)
    uploader = models.ForeignKey(User, related_name=u'Document', null=True, on_delete=models.SET_NULL)
    upload_date = models.DateTimeField(u'Uploaddatum', auto_now_add=True)
    category = models.ForeignKey(DocumentCategory, related_name=u'Document', null=True, on_delete=models.PROTECT)
    downloadcount = models.IntegerField(default=0)

    def rating_exact(self):
        """Return exact rating average."""
        ratings = self.DocumentRating.values_list('rating', flat=True)
        total = sum(ratings)
        if len(ratings) > 0:
            return float(total) / len(ratings)
        else:
            return 0

    def rating(self):
        """Return rounded rating average."""
        return int(round(self.rating_exact()))
        
    def filename(self):
        """Return filename of uploaded file without directories."""
        return os.path.basename(self.document.name)

    def fileext(self):
        """Return file extension by splitting at last occuring period."""
        return os.path.splitext(self.document.name)[1]

    def exists(self):
        """Return whether or not the file exists on the harddrive."""
        return os.path.exists(self.document.path)

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ('-upload_date',)
        get_latest_by = 'upload_date'


class DocumentRating(models.Model):
    """Rating for a document.

    Valid values are integers between 1 and 5.

    """
    user = models.ForeignKey(User, related_name=u'DocumentRating')
    document = models.ForeignKey(Document, related_name='DocumentRating')
    rating = models.PositiveSmallIntegerField(validators=[MaxValueValidator(10), MinValueValidator(1)])

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
    author = models.ForeignKey(User, related_name='Event', null=True, on_delete=models.SET_NULL)
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


class UserProfile(models.Model):
    """A user profile."""
    user = models.OneToOneField(User)
    twitter = models.CharField(u'Twitter Benutzername', max_length=24, blank=True)
    flattr = models.CharField(u'Flattr Benutzername', max_length=128, blank=True,
            help_text=mark_safe(u'Falls angegeben, wird bei deinen \
            Zusammenfassungen jeweils ein \
            <a href="https://flattr.com/">Flattr</a> Button angezeigt.'))

    def __unicode__(self):
        return u'Profile for %s' % self.user.username


def name(self):
    """Return either full user first and last name or the username, if no
    further data is found."""
    if self.first_name or self.last_name:
        return ' '.join(filter(None, [self.first_name, self.last_name]))
    return self.username
User.add_to_class('name', name)


def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
post_save.connect(create_user_profile, sender=User)
