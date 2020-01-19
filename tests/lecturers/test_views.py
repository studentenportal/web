# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model

from model_bakery import baker

from apps.lecturers import models

User = get_user_model()


def login(self):
    assert self.client.login(username='testuser', password='test')


class LecturerListViewTest(TestCase):
    def testLoginRequired(self):
        response = self.client.get('/dozenten/')
        self.assertRedirects(response, '/accounts/login/?next=/dozenten/')

    def testContent(self):
        baker.make_recipe('apps.front.user')
        baker.make_recipe('apps.lecturers.lecturer')
        login(self)
        response = self.client.get('/dozenten/')
        self.assertContains(response, '<h1>Unsere Dozenten</h1>')
        self.assertContains(response, 'David<br />Krakaduku')


class LecturerDetailViewTest(TestCase):
    def setUp(self):
        # setUpClass
        baker.make_recipe('apps.front.user')
        self.lecturer = baker.make_recipe('apps.lecturers.lecturer')
        self.url = reverse('lecturers:lecturer_detail', args=(self.lecturer.pk,))

    def testLoginRequired(self):
        response = self.client.get(self.url)
        self.assertRedirects(response, '/accounts/login/?next=%s' % self.url)

    def testDescription(self):
        login(self)
        response = self.client.get(self.url)
        title = (
            '<h1 class="lecturer-name" '
            'data-lecturer-pk="%s" '
            'data-rating-url="/api/v1/lecturers/%s/rate"'
            '>Prof. Dr. Krakaduku David</h1>' % (self.lecturer.pk, self.lecturer.pk)
        )
        self.assertContains(response, title)
        self.assertContains(response, 'Quantenphysik, Mathematik für Mathematiker')

    def testContact(self):
        login(self)
        response = self.client.get(self.url)
        self.assertContains(response, '1.337')
        self.assertContains(response, 'krakaduku@hsr.ch')


class QuoteAddViewTest(TestCase):
    def setUp(self):
        # setUpClass
        baker.make_recipe('apps.front.user')
        baker.make_recipe('apps.lecturers.lecturer')
        # setUp
        login(self)

    def testGenericForm(self):
        """Test the form that is shown if no lecturer is preselected."""
        response = self.client.get('/zitate/add/')
        self.assertContains(response, '<h1>Zitat hinzufügen</h1>')
        self.assertContains(response, '<option value="" selected>---------</option>')


    def testPrefilledForm(self):
        """Test the form that is shown if a lecturer is preselected."""
        response = self.client.get('/zitate/1337/add/')
        self.assertContains(response, '<h1>Zitat hinzufügen</h1>')
        self.assertContains(response, '<select name="lecturer" required id="id_lecturer">')
        self.assertContains(response, '<option value="1337" selected>Krakaduku David</option>')

    def testFormSubmission(self):
        """Test whether a quote submission gets saved correctly."""
        response = self.client.post('/zitate/add/', {
            'lecturer': '1337',
            'quote': 'ich bin der beste dozent von allen.',
            'comment': 'etwas arrogant, nicht?',
        })
        self.assertRedirects(response, '/zitate/')
        response2 = self.client.get('/zitate/')
        self.assertContains(response2, '<p>ich bin der beste dozent von allen.</p>')
        self.assertContains(response2, '<p class="comment">etwas arrogant, nicht?</p>')

    def testAutoUpvote(self):
        """Test whether the added quote was automatically upvoted."""
        self.client.post('/zitate/add/', {
            'pk': 9000,
            'lecturer': '1337',
            'quote': 'ich bin der töllscht!',
        })
        quote = models.Quote.objects.get(lecturer=1337, quote='ich bin der töllscht!')
        assert quote.vote_sum() == 1, "Quote wasn't automatically upvoted..."


class QuoteViewTest(TestCase):
    def setUp(self):
        # setUpClass
        baker.make_recipe('apps.front.user')
        # setUp
        login(self)
        self.response = self.client.get('/zitate/')

    def testTitle(self):
        self.assertContains(self.response, '<h1>Zitate</h1>')

    def testQuoteInList(self):
        """Test whether an added quote shows up in the list."""
        baker.make(models.Quote, quote='spam', comment='ham')
        response = self.client.get('/zitate/')
        self.assertContains(response, 'spam')
        self.assertContains(response, 'ham')

    def testNullValueAuthor(self):
        """Test whether a quote without an author does not raise an error."""
        baker.make(models.Quote, quote='spam', comment='ham', author=None)
        response = self.client.get('/zitate/')
        self.assertContains(response, 'spam')
        self.assertContains(response, 'ham')
