# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

import os
from datetime import datetime

from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.template.defaultfilters import slugify
from django.utils.safestring import mark_safe

from model_utils import Choices

from apps.front import fields
from apps.lecturers import models as lecturer_models


class DocumentCategory(models.Model):
    """Categories (usually subjects) for the documents.
    A document can have several categories.
    """
    name = fields.CaseInsensitiveSlugField('Kürzel', max_length=32, unique=True,
            help_text='z.B. "CompT1" oder "Prog3"')
    description = models.CharField('Voller Name', max_length=255,
            help_text='z.B. "Computertechnik 1" oder "Programmieren 3"')
    courses = models.ManyToManyField(lecturer_models.Course, blank=True)
    lecturers = models.ManyToManyField(lecturer_models.Lecturer, blank=True)

    @property
    def summary_count(self):
        return self.Document.filter(dtype=Document.DTypes.SUMMARY).count()

    @property
    def exam_count(self):
        return self.Document.filter(dtype=Document.DTypes.EXAM).count()

    @property
    def other_count(self):
        excludes = [Document.DTypes.EXAM, Document.DTypes.SUMMARY]
        return self.Document.exclude(dtype__in=excludes).count()

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = 'Modul'
        ordering = ['name']


def document_file_name(instance, filename):
    """Where to put a newly uploaded document. Also, store original filename."""
    ext = os.path.splitext(filename)[1]
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    instance.original_filename = filename
    return '/'.join(['documents', slugify(instance.category.name), '%s%s' % (timestamp, ext)])


class Document(models.Model):
    """A document that can be uploaded by students.

    A document can have a description, categories, ratings, etc...

    """
    class DTypes(object):
        """Enum-style document type class."""
        SUMMARY = 1
        EXAM = 2
        SOFTWARE = 3
        LEARNING_AID = 4
        ATTESTATION = 5

    LICENSES = Choices(
        (1, 'pd', 'Public Domain'),
        (2, 'cc3_by', 'CC BY 3.0'),
        (3, 'cc3_by_sa', 'CC BY-SA 3.0'),
        (4, 'cc3_by_nc', 'CC BY-NC 3.0'),
        (5, 'cc3_by_nc_sa', 'CC BY-NC-SA 3.0'),
    )

    name = models.CharField('Titel', max_length=100)
    description = models.CharField('Beschreibung', blank=True, max_length=500,
        help_text='(Max. 500 Zeichen)')
    url = models.URLField('URL', null=True, blank=True,
        help_text='z.B. Link zu Github Repository')
    category = models.ForeignKey(DocumentCategory, verbose_name='Modul', related_name='Document',
            null=True, on_delete=models.PROTECT)
    dtype = models.PositiveSmallIntegerField('Typ', choices=(
                (DTypes.SUMMARY, 'Zusammenfassung'),
                (DTypes.EXAM, 'Prüfung'),
                (DTypes.SOFTWARE, 'Software'),
                (DTypes.LEARNING_AID, 'Lernhilfe'),
                (DTypes.ATTESTATION, 'Testat'),
            ))
    document = models.FileField('Datei', upload_to=document_file_name, help_text='(Max. 20MB)')
    original_filename = models.CharField('Originaler Dateiname', max_length=255, blank=True)
    uploader = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='Document', null=True,
            on_delete=models.SET_NULL)
    upload_date = models.DateTimeField('Uploaddatum', auto_now_add=True)
    change_date = models.DateTimeField('Letztes Änderungsdatum')
    license = models.PositiveSmallIntegerField('Lizenz', choices=LICENSES, null=True, blank=True,
        help_text=mark_safe('Lizenz, siehe <a href="http://creativecommons.org/choose/?lang=de">' +
            'http://creativecommons.org/choose/?lang=de</a> um eine passende Lizenz auszuwählen.' +
            '<br>Empfohlen: CC BY-SA-NC 3.0'))
    public = models.BooleanField('Öffentlich', default=True,
        help_text='Soll man dieses Dokument ohne Login downloaden können?')
    flattr_disabled = models.BooleanField('Flattr deaktivieren', default=False,
        help_text='Soll Flattr für dieses Dokument deaktiviert werden?')

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

    def thumbnail(self):
        """Check wether current document can have a thumbnail by checking
        wether the file extension is a PDF."""
        return self.fileext() == ".pdf"

    def github(self):
        """Check whether the url is associated with github by simply checking if "github"
        is contained in the link. This means that any URL with "github" in the name will
        be associated to github."""
        return self.url and "github" in self.url

    def downloadcount(self):
        """Return the download count."""
        return self.DocumentDownload.count()

    def license_details(self):
        """Return the URL to the license and the appropriate license icon."""
        CC_LICENSES = {2: 'by', 3: 'by-sa', 4: 'by-nc', 5: 'by-nc-sa'}
        if self.license in CC_LICENSES.keys():
            url_template = 'http://creativecommons.org/licenses/{0}/3.0/deed.de'
            icon_template = 'http://i.creativecommons.org/l/{0}/3.0/80x15.png'
            url = url_template.format(CC_LICENSES.get(self.license))
            icon = icon_template.format(CC_LICENSES.get(self.license))
        elif self.license == 1:
            url = 'http://creativecommons.org/publicdomain/zero/1.0/deed.de'
            icon = 'http://i.creativecommons.org/p/zero/1.0/80x15.png'
        else:
            url = icon = None
        return {'url': url, 'icon': icon, 'name': self.get_license_display()}

    def save(self, *args, **kwargs):
        """Override save method to automatically set change_date at creation."""
        if not self.change_date:
            self.change_date = datetime.now()
        return super(Document, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ('-change_date',)
        get_latest_by = 'change_date'


class DocumentDownload(models.Model):
    """Tracks a download of a document."""
    document = models.ForeignKey(Document, related_name='DocumentDownload', db_index=True)
    timestamp = models.DateTimeField(auto_now_add=True, editable=False)
    ip = models.GenericIPAddressField(unpack_ipv4=True, editable=False, db_index=True)

    class Meta:
        index_together = [
            ('document', 'timestamp', 'ip'),
        ]


class DocumentRating(models.Model):
    """Rating for a document.

    Valid values are integers between 1 and 5.

    """
    RATING_VALIDATORS = [MaxValueValidator(10), MinValueValidator(1)]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='DocumentRating')
    document = models.ForeignKey(Document, related_name='DocumentRating')
    rating = models.PositiveSmallIntegerField(validators=RATING_VALIDATORS)

    # Custom model validation
    def clean(self):
        if self.user == self.document.uploader:
            raise ValidationError('A user cannot rate his own uploads.')

    def __unicode__(self):
        fmt_args = self.user.username, self.document.name, self.rating
        return 'User %s Document %s Rating %u' % fmt_args

    class Meta:
        unique_together = ('user', 'document')
