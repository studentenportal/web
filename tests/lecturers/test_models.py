# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

import datetime

from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.db import IntegrityError

from model_mommy import mommy

from apps.lecturers import models
import pytest


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
        assert self.lecturer.avg_rating_d() == 7
        assert self.lecturer.avg_rating_m() == 10
        assert self.lecturer.avg_rating_f() == 0

    def testName(self):
        assert self.lecturer.name() == 'Prof. Dr. Krakaduku David'

    def testManager(self):
        mommy.make(models.Lecturer, pk=10, function='Dozent')
        mommy.make(models.Lecturer, pk=11, department='Gebäudemanagement')
        mommy.make(models.Lecturer, pk=12, function='Projektmitarbeiterin')
        all_lecturers = models.Lecturer.objects.all()
        real_lecturers = models.Lecturer.real_objects.all()
        assert 10 in all_lecturers.values_list('pk', flat=True)
        assert 11 in all_lecturers.values_list('pk', flat=True)
        assert 12 in all_lecturers.values_list('pk', flat=True)
        assert 10 in real_lecturers.values_list('pk', flat=True)
        assert 11 not in real_lecturers.values_list('pk', flat=True)
        assert 12 not in real_lecturers.values_list('pk', flat=True)


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
        assert models.LecturerRating.objects.count() == 1

    def testAddInvalidCategory(self):
        """Test whether only a valid category can be added."""
        with pytest.raises(ValidationError):
            self.create_default_rating(category=u'x')

    def testAddInvalidRating(self):
        """Test whether invalid ratings raise validation errors."""
        with pytest.raises(ValidationError):
            self.create_default_rating(rating=11)
        with pytest.raises(ValidationError):
            self.create_default_rating(rating=0)

    def testUniqueTogether(self):
        """Test the unique_together constraint."""
        self.create_default_rating()
        with pytest.raises(ValidationError):
            self.create_default_rating(rating=6)


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
        assert before < q.date < after
        assert q.date_available()

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
        assert not q.date_available()
