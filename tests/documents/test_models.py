# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

import datetime
import collections

from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.db import IntegrityError

from model_mommy import mommy

from apps.documents import models
import pytest


User = get_user_model()


class TestDocumentModel:

    @pytest.fixture
    def john(self, db):
        return mommy.make(User, username='john')

    @pytest.fixture
    def marc(self, db):
        return mommy.make(User, username='marc')

    @pytest.fixture
    def pete(self, db):
        return mommy.make(User, username='pete')

    @pytest.fixture
    def document(self, john, marc, pete, db):
        document = models.Document.objects.create(
                name='Analysis 1 Theoriesammlung',
                dtype=models.Document.DTypes.SUMMARY,
                description='Dieses Dokument ist eine Zusammenfassung der \
                    Theorie aus dem AnI1-Skript auf 8 Seiten. Das Dokument ist \
                    in LaTeX gesetzt, Source ist hier: http://j.mp/fjtleh - \
                    Gute Ergänzungen sind erwünscht!',
                uploader=john,
                flattr_disabled=True)
        document.DocumentRating.create(user=marc, rating=5)
        document.DocumentRating.create(user=pete, rating=2)
        return document

    def test_basic_properties(self, document):
        assert document.name == 'Analysis 1 Theoriesammlung'
        assert document.description.startswith('Dieses Dokument')
        assert document.dtype == models.Document.DTypes.SUMMARY
        assert isinstance(document.uploader, User)

    def test_upload_date(self, document):
        """Check whether upload date has been set."""
        assert isinstance(document.upload_date, datetime.datetime)

    def test_rating_average(self, document):
        """Test the document rating average calculation."""
        assert document.DocumentRating.count() == 2
        assert document.rating() == 4
        assert document.rating_exact() == 3.5

    def test_rating_validation(self, document, marc):
        dr = models.DocumentRating.objects.get(document=document, user=marc)
        dr.rating = 11
        with pytest.raises(ValidationError):
            dr.full_clean()
        dr.rating = 0
        with pytest.raises(ValidationError):
            dr.full_clean()

    def test_rating_author_validation(self, document, john):
        """A user may not rate his own uploads."""
        dr = models.DocumentRating(document=document, user=john)
        with pytest.raises(ValidationError):
            dr.full_clean()

    def test_duplicate_ratings_validation(self, document, marc):
        """A user cannot rate the same document twice."""
        dr = models.DocumentRating(document=document, user=marc)
        with pytest.raises(IntegrityError):
            dr.save()

    @pytest.mark.django_db
    def test_null_value_uploader(self):
        d = models.Document()
        d.name = 'spam'
        d.description = 'ham'
        d.dtype = models.Document.DTypes.SUMMARY
        try:
            d.save()
        except IntegrityError:
            pytest.fail("A document with no uploader should not throw an IntegrityError.")

    def test_download_count(self, document):
        models.DocumentDownload.objects.create(document=document, ip='127.0.0.1')
        models.DocumentDownload.objects.create(document=document, ip='192.168.1.2')
        models.DocumentDownload.objects.create(document=document, ip='2001::8a2e:7334')
        assert 3 == document.downloadcount()

    @pytest.mark.django_db
    def test_license_details_cc(self):
        """Test the details of a CC license."""
        summary = models.Document.DTypes.SUMMARY
        doc1 = models.Document.objects.create(name='CC-BY doc', dtype=summary,
                license=models.Document.LICENSES.cc3_by)
        doc2 = models.Document.objects.create(name='CC-BY-NC-SA doc', dtype=summary,
                license=models.Document.LICENSES.cc3_by_nc_sa)
        assert 'CC BY 3.0' == doc1.get_license_display()
        assert 'CC BY-NC-SA 3.0' == doc2.get_license_display()
        details1 = doc1.license_details()
        details2 = doc2.license_details()
        assert 'http://creativecommons.org/licenses/by/3.0/deed.de' == details1['url']
        assert 'http://i.creativecommons.org/l/by/3.0/80x15.png' == details1['icon']
        assert 'http://creativecommons.org/licenses/by-nc-sa/3.0/deed.de' == details2['url']
        assert 'http://i.creativecommons.org/l/by-nc-sa/3.0/80x15.png' == details2['icon']

    @pytest.mark.django_db
    def test_license_details_pd(self):
        """Test the details of a PD (CC0) license."""
        doc = models.Document.objects.create(name='PD doc', dtype=models.Document.DTypes.SUMMARY,
                license=models.Document.LICENSES.pd)
        details = doc.license_details()
        assert 'Public Domain' == doc.get_license_display()
        assert 'http://creativecommons.org/publicdomain/zero/1.0/deed.de' == details['url']
        assert 'http://i.creativecommons.org/p/zero/1.0/80x15.png' == details['icon']

    @pytest.mark.django_db
    def test_license_details_none(self):
        """Test the details of a document without a license."""
        doc = models.Document.objects.create(name='PD doc', dtype=models.Document.DTypes.SUMMARY)
        details = doc.license_details()
        assert doc.get_license_display() is None
        assert details['url'] is None
        assert details['icon'] is None

    def test_flattr_disabled(self, document):
        assert document.flattr_disabled


@pytest.mark.django_db
def test_user_model():
    """Test whether the custom name function returns the correct string."""
    john = User.objects.create(username='john')
    marc = User.objects.create(username='marc', first_name=u'Marc')
    pete = User.objects.create(username='pete', last_name=u'Peterson')
    mike = User.objects.create(username='mike', first_name=u'Mike', last_name=u'Müller')
    assert john.name() == u'john'
    assert marc.name() == u'Marc'
    assert pete.name() == u'Peterson'
    assert mike.name() == u'Mike Müller'
