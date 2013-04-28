# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

import datetime

from django.test import TestCase, TransactionTestCase
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.db import IntegrityError

from model_mommy import mommy

from apps.front import models


User = get_user_model()


class LecturerModelTest(TestCase):
    def setUp(self):
        self.lecturer = mommy.make(models.Lecturer, title='Prof. Dr.',
            first_name='David',
            last_name='Krakaduku',
        )
        mommy.make(models.LecturerRating, lecturer=self.lecturer, category='d', rating=5)
        mommy.make(models.LecturerRating, lecturer=self.lecturer, category='d', rating=8)
        mommy.make(models.LecturerRating, lecturer=self.lecturer, category='m', rating=10)

    def testRatings(self):
        """Test whether ratings are calculated correctly."""
        self.assertEqual(self.lecturer.avg_rating_d(), 7)
        self.assertEqual(self.lecturer.avg_rating_m(), 10)
        self.assertEqual(self.lecturer.avg_rating_f(), 0)

    def testName(self):
        self.assertEqual(self.lecturer.name(), 'Prof. Dr. Krakaduku David')

    def testManager(self):
        mommy.make(models.Lecturer, pk=10, function='Dozent')
        mommy.make(models.Lecturer, pk=11, department='Gebäudemanagement')
        mommy.make(models.Lecturer, pk=12, function='Projektmitarbeiterin')
        all_lecturers = models.Lecturer.objects.all()
        real_lecturers = models.Lecturer.real_objects.all()
        self.assertIn(10, all_lecturers.values_list('pk', flat=True))
        self.assertIn(11, all_lecturers.values_list('pk', flat=True))
        self.assertIn(12, all_lecturers.values_list('pk', flat=True))
        self.assertIn(10, real_lecturers.values_list('pk', flat=True))
        self.assertNotIn(11, real_lecturers.values_list('pk', flat=True))
        self.assertNotIn(12, real_lecturers.values_list('pk', flat=True))


class LecturerRatingModelTest(TestCase):
    def setUp(self):
        # setUpClass
        mommy.make(User)
        mommy.make(models.Lecturer)

    def create_default_rating(self, category=u'd', rating=5):
        """Helper function to create a default rating."""
        user = User.objects.all()[0]
        lecturer = models.Lecturer.objects.all()[0]
        lr = models.LecturerRating(
            user=user,
            lecturer=lecturer,
            category=category,
            rating=rating)
        lr.full_clean()
        lr.save()

    def testAddSimpleRating(self):
        """Test whether a simple valid rating can be added."""
        self.create_default_rating()
        self.assertEqual(models.LecturerRating.objects.count(), 1)

    def testAddInvalidCategory(self):
        """Test whether only a valid category can be added."""
        with self.assertRaises(ValidationError):
            self.create_default_rating(category=u'x')

    def testAddInvalidRating(self):
        """Test whether invalid ratings raise validation errors."""
        with self.assertRaises(ValidationError):
            self.create_default_rating(rating=11)
        with self.assertRaises(ValidationError):
            self.create_default_rating(rating=0)

    def testUniqueTogether(self):
        """Test the unique_together constraint."""
        self.create_default_rating()
        with self.assertRaises(ValidationError):
            self.create_default_rating(rating=6)


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


class QuoteModelTest(TestCase):
    def testQuote(self):
        quote = "Dies ist ein längeres Zitat, das dazu dient, zu testen " + \
            "ob man Zitate erfassen kann und ob die Länge des Zitats mehr " + \
            "als 255 Zeichen enthalten darf. Damit kann man sicherstellen, " + \
            "dass im Model kein CharField verwendet wurde. Denn wir wollen " + \
            "ja nicht, dass längere Zitate hier keinen Platz haben :)"
        before = datetime.datetime.now()
        q = models.Quote()
        q.author = mommy.make(User)
        q.lecturer = mommy.make(models.Lecturer)
        q.quote = quote
        q.comment = "Eine Bemerkung zum Kommentar"
        q.save()
        after = datetime.datetime.now()
        self.assertTrue(before < q.date < after)
        self.assertTrue(q.date_available())

    def testNullValueAuthor(self):
        q = models.Quote()
        q.lecturer = mommy.make(models.Lecturer)
        q.quote = 'spam'
        q.comment = 'ham'
        try:
            q.save()
        except IntegrityError:
            self.fail("A quote with no author should not throw an IntegrityError.")

    def test1970Quote(self):
        """Check whether a quote from 1970-1-1 is marked as date_available=False."""
        q = models.Quote()
        q.lecturer = mommy.make(models.Lecturer)
        q.author = mommy.make(User)
        q.quote = 'spam'
        q.comment = 'ham'
        q.date = datetime.datetime(1970, 1, 1)
        self.assertFalse(q.date_available())


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


class EventModelTest(TestCase):
    def testDateTimeEvent(self):
        user = mommy.make(User, username='testuser')
        event = models.Event.objects.create(
            summary='Testbar',
            description=u'This is a bar where people drink and party to \
                          test the studentenportal event feature.',
            author=user,
            start_date=datetime.date(day=1, month=9, year=2010),
            start_time=datetime.time(hour=19, minute=30),
            end_time=datetime.time(hour=23, minute=59))

        self.assertEqual(event.summary, 'Testbar')
        self.assertIsNone(event.end_date)
        self.assertEqual(event.author.username, 'testuser')
        self.assertTrue(event.is_over())
        self.assertIsNone(event.days_until())

    def testAllDayEvent(self):
        user = mommy.make(User)
        start_date = datetime.date.today() + datetime.timedelta(days=365)
        event = models.Event.objects.create(
            summary='In a year',
            description='This happens in a year from now.',
            author=user,
            start_date=start_date,
            end_date=start_date + datetime.timedelta(days=1))

        self.assertEqual(event.summary, 'In a year')
        self.assertIsNone(event.start_time)
        self.assertIsNone(event.end_time)
        self.assertFalse(event.is_over())
        self.assertTrue(event.all_day())
        self.assertEqual(event.days_until(), 365)

    def testNullValueAuthor(self):
        event = models.Event()
        event.summary = 'Testbar'
        event.description = u'Dies ist eine bar deren autor nicht mehr existiert.'
        event.author = None
        event.start_date = datetime.date(day=1, month=9, year=2010)
        event.start_time = datetime.time(hour=19, minute=30)
        event.end_time = datetime.time(hour=23, minute=59)
        try:
            event.save()
        except IntegrityError:
            self.fail("An event with no author should not throw an IntegrityError.")
