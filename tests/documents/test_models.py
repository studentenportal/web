# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

import datetime

from django.test import TransactionTestCase
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.db import IntegrityError

from model_mommy import mommy

from apps.documents import models


User = get_user_model()


class DocumentModelTest(TransactionTestCase):
    def setUp(self):
        self.john = mommy.make(User, username='john')
        self.marc = mommy.make(User, username='marc')
        self.pete = mommy.make(User, username='pete')
        self.document = models.Document.objects.create(
                name='Analysis 1 Theoriesammlung',
                dtype=models.Document.DTypes.SUMMARY,
                description='Dieses Dokument ist eine Zusammenfassung der \
                    Theorie aus dem AnI1-Skript auf 8 Seiten. Das Dokument ist \
                    in LaTeX gesetzt, Source ist hier: http://j.mp/fjtleh - \
                    Gute Ergänzungen sind erwünscht!',
                uploader=self.john)
        self.document.DocumentRating.create(user=self.marc, rating=5)
        self.document.DocumentRating.create(user=self.pete, rating=2)

    def testBasicProperties(self):
        self.assertEqual(self.document.name, 'Analysis 1 Theoriesammlung')
        self.assertTrue(self.document.description.startswith('Dieses Dokument'))
        self.assertEqual(self.document.dtype, models.Document.DTypes.SUMMARY)
        self.assertTrue(isinstance(self.document.uploader, User))

    def testUploadDate(self):
        """Check whether upload date has been set."""
        self.assertTrue(isinstance(self.document.upload_date, datetime.datetime))

    def testRatingAverage(self):
        """Test the document rating average calculation."""
        self.assertEqual(self.document.DocumentRating.count(), 2)
        self.assertEqual(self.document.rating(), 4)
        self.assertEqual(self.document.rating_exact(), 3.5)

    def testRatingValidation(self):
        dr = models.DocumentRating.objects.get(document=self.document, user=self.marc)
        dr.rating = 11
        self.assertRaises(ValidationError, dr.full_clean)
        dr.rating = 0
        self.assertRaises(ValidationError, dr.full_clean)

    def testRatingAuthorValidation(self):
        """A user may not rate his own uploads."""
        dr = models.DocumentRating(document=self.document, user=self.john)
        self.assertRaises(ValidationError, dr.full_clean)

    def testDuplicateRatingsValidation(self):
        """A user cannot rate the same document twice."""
        dr = models.DocumentRating(document=self.document, user=self.marc)
        self.assertRaises(IntegrityError, dr.save)

    def testNullValueUploader(self):
        d = models.Document()
        d.name = 'spam'
        d.description = 'ham'
        d.dtype = models.Document.DTypes.SUMMARY
        try:
            d.save()
        except IntegrityError:
            self.fail("A document with no uploader should not throw an IntegrityError.")

    def testDownloadCount(self):
        models.DocumentDownload.objects.create(document=self.document, ip='127.0.0.1')
        models.DocumentDownload.objects.create(document=self.document, ip='192.168.1.2')
        models.DocumentDownload.objects.create(document=self.document, ip='2001::8a2e:7334')
        self.assertEqual(3, self.document.downloadcount())

    def testLicenseDetailsCC(self):
        """Test the details of a CC license."""
        summary = models.Document.DTypes.SUMMARY
        doc1 = models.Document.objects.create(name='CC-BY doc', dtype=summary,
                license=models.Document.LICENSES.cc3_by)
        doc2 = models.Document.objects.create(name='CC-BY-NC-SA doc', dtype=summary,
                license=models.Document.LICENSES.cc3_by_nc_sa)
        self.assertEqual('CC BY 3.0', doc1.get_license_display())
        self.assertEqual('CC BY-NC-SA 3.0', doc2.get_license_display())
        details1 = doc1.license_details()
        details2 = doc2.license_details()
        self.assertEqual('http://creativecommons.org/licenses/by/3.0/deed.de', details1['url'])
        self.assertEqual('http://i.creativecommons.org/l/by/3.0/80x15.png', details1['icon'])
        self.assertEqual('http://creativecommons.org/licenses/by-nc-sa/3.0/deed.de', details2['url'])
        self.assertEqual('http://i.creativecommons.org/l/by-nc-sa/3.0/80x15.png', details2['icon'])

    def testLicenseDetailsPD(self):
        """Test the details of a PD (CC0) license."""
        doc = models.Document.objects.create(name='PD doc', dtype=models.Document.DTypes.SUMMARY,
                license=models.Document.LICENSES.pd)
        details = doc.license_details()
        self.assertEqual('Public Domain', doc.get_license_display())
        self.assertEqual('http://creativecommons.org/publicdomain/zero/1.0/deed.de', details['url'])
        self.assertEqual('http://i.creativecommons.org/p/zero/1.0/80x15.png', details['icon'])

    def testLicenseDetailsNone(self):
        """Test the details of a document without a license."""
        doc = models.Document.objects.create(name='PD doc', dtype=models.Document.DTypes.SUMMARY)
        details = doc.license_details()
        self.assertIsNone(doc.get_license_display())
        self.assertIsNone(details['url'])
        self.assertIsNone(details['icon'])


class UserModelTest(TransactionTestCase):
    def setUp(self):
        self.john = User.objects.create(username='john')
        self.marc = User.objects.create(username='marc', first_name=u'Marc')
        self.pete = User.objects.create(username='pete', last_name=u'Peterson')
        self.mike = User.objects.create(username='mike', first_name=u'Mike', last_name=u'Müller')

    def testName(self):
        """Test whether the custom name function returns the correct string."""
        self.assertEqual(self.john.name(), u'john')
        self.assertEqual(self.marc.name(), u'Marc')
        self.assertEqual(self.pete.name(), u'Peterson')
        self.assertEqual(self.mike.name(), u'Mike Müller')
