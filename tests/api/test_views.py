# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

import json
import base64

import pytest
from django.test.client import Client
from django.core.urlresolvers import reverse, NoReverseMatch
from django.contrib.auth import get_user_model

from model_mommy import mommy

from apps.lecturers.models import Quote, QuoteVote, Lecturer


User = get_user_model()


class TestAuthentication:

    def test_no_auth(self, client):
        """Test that requesting resources is not possible without auth."""
        targets = ['api_root', 'user_list', 'user_detail', 'lecturer_list',
                   'lecturer_detail', 'quote_list', 'quote_detail']
        for target in targets:
            try:
                url = reverse('api:' + target)
            except NoReverseMatch:
                url = reverse('api:' + target, args=(1,))
            resp = client.get(url)
            assert resp.status_code == 401, \
                    'Status code for %s is %d instead of 401.' % (url, resp.status_code)
            data = json.loads(resp.content)
            assert data == {
                'detail': 'Anmeldedaten fehlen.',
            }

    def test_session_auth(self, auth_client):
        url = reverse('api:quote_list')
        resp = auth_client.get(url)
        assert resp.status_code == 200

    def test_basic_auth(self, client, user, db):
        url = reverse('api:quote_list')
        auth = 'Basic ' + base64.b64encode('testuser:test')
        resp = client.get(url, HTTP_AUTHORIZATION=auth)
        assert resp.status_code == 200


class TestUserView:

    def test_status_code(self, user, auth_client):
        urls = [reverse('api:user_list'), reverse('api:user_detail', args=(user.pk,))]
        for url in urls:
            resp = auth_client.get(url)
            assert resp.status_code == 200, \
                    'Status code for %s is %d instead of 200.' % (url, resp.status_code)

    def test_list_data(self, auth_client):
        users = [mommy.make(User) for i in xrange(3)]
        url = reverse('api:user_list')
        resp = auth_client.get(url)
        data = json.loads(resp.content)
        assert len(data['results']) == data['count']
        assert data['count'] == User.objects.count()

    def test_detail_data(self, user, auth_client):
        url = reverse('api:user_detail', args=(user.pk,))
        resp = auth_client.get(url)
        data = json.loads(resp.content)
        attrs = ['id', 'username', 'first_name', 'last_name', 'email', 'flattr', 'twitter']
        for attr in attrs:
            assert data[attr] == getattr(user, attr)

    def test_list_methods(self, auth_client):
        url = reverse('api:user_list')
        resp = auth_client.head(url)
        allow = set(resp.get('Allow').split(', '))
        assert allow == set(['GET', 'HEAD', 'OPTIONS'])

    def test_detail_methods(self, user, auth_client):
        url = reverse('api:user_detail', args=(user.pk,))
        resp = auth_client.head(url)
        allow = set(resp.get('Allow').split(', '))
        assert allow == set(['GET', 'PUT', 'HEAD', 'OPTIONS', 'PATCH'])

    def test_update_permissions(self, user, auth_client):
        """It should only be possible to edit own user."""
        another_user = mommy.make(User)
        url1 = reverse('api:user_detail', args=(user.pk,))
        url2 = reverse('api:user_detail', args=(another_user.pk,))
        data1 = {'username': 'test1', 'email': 'test1@example.com'}
        data2 = {'username': 'test2', 'email': 'test2@example.com'}
        resp1 = auth_client.patch(url1, json.dumps(data1), 'application/json')
        resp2 = auth_client.patch(url2, json.dumps(data2), 'application/json')
        assert resp1.status_code == 200, resp1.content
        assert resp2.status_code == 403, resp2.content

    def test_username_change(self, user, auth_client):
        """You should not be able to change your own username."""
        url = reverse('api:user_detail', args=(user.pk,))
        data = {'username': 'a_new_username', 'email': user.email}
        resp = auth_client.patch(url, json.dumps(data), 'application/json')
        assert resp.status_code == 200
        newuser = User.objects.get(pk=user.pk)
        assert user.username == newuser.username


class TestLecturerView:

    @pytest.fixture
    def lecturer(self, db):
        return mommy.make(Lecturer)

    def test_status_code(self, lecturer, auth_client):
        urls = [reverse('api:lecturer_list'), reverse('api:lecturer_detail', args=(lecturer.pk,))]
        for url in urls:
            resp = auth_client.get(url)
            assert resp.status_code == 200, \
                    'Status code for %s is %d instead of 200.' % (url, resp.status_code)

    def test_detail_data(self, lecturer, auth_client, db):
        [mommy.make(Quote, lecturer=lecturer) for i in xrange(3)]

        url = reverse('api:lecturer_detail', args=(lecturer.pk,))
        resp = auth_client.get(url)
        data = json.loads(resp.content)

        attrs = ['id', 'title', 'last_name', 'first_name', 'abbreviation',
                 'department', 'function', 'main_area', 'subjects', 'email',
                 'office']
        for attr in attrs:
            assert data[attr] == getattr(lecturer, attr)

        assert len(data['quotes']) == lecturer.Quote.count()

    def test_list_methods(self, auth_client):
        url = reverse('api:lecturer_list')
        resp = auth_client.head(url)
        allow = set(resp.get('Allow').split(', '))
        assert allow == set(['GET', 'HEAD', 'OPTIONS'])

    def test_detail_methods(self, lecturer, auth_client):
        url = reverse('api:lecturer_detail', args=(lecturer.pk,))
        resp = auth_client.head(url)
        allow = set(resp.get('Allow').split(', '))
        assert allow == set(['GET', 'HEAD', 'OPTIONS'])


class TestQuoteView:

    @pytest.fixture
    def quote(self, db, user):
        return mommy.make(Quote, author=user)

    def test_status_code(self, auth_client, quote):
        urls = [reverse('api:quote_list'), reverse('api:quote_detail', args=(quote.pk,))]
        for url in urls:
            resp = auth_client.get(url)
            assert resp.status_code == 200, \
                    'Status code for %s is %d instead of 200.' % (url, resp.status_code)

    def test_detail_data(self, auth_client, quote):
        url = reverse('api:quote_detail', args=(quote.pk,))
        resp = auth_client.get(url)
        data = json.loads(resp.content)
        assert data['lecturer'] == quote.lecturer.pk
        assert data['lecturer_name'] == quote.lecturer.name()
        assert data['date'][:10] == quote.date.date().isoformat()
        assert data['comment'] == quote.comment

    def test_list_methods(self, auth_client):
        url = reverse('api:quote_list')
        resp = auth_client.head(url)
        allow = set(resp.get('Allow').split(', '))
        assert allow == set(['GET', 'POST', 'HEAD', 'OPTIONS'])

    def test_detail_methods(self, auth_client, quote):
        url = reverse('api:quote_detail', args=(quote.pk,))
        resp = auth_client.head(url)
        allow = set(resp.get('Allow').split(', '))
        assert allow == set(['GET', 'PUT', 'HEAD', 'OPTIONS', 'PATCH'])

    def test_auto_author_POST(self, auth_client, user):
        """Assert that the author is automatically set to the currently logged
        in user on POST."""
        # Insert two quotes
        url = reverse('api:quote_list')
        lecturer = mommy.make(Lecturer)
        other_user = mommy.make(User)
        resp = auth_client.post(url, {
            'lecturer': lecturer.pk,
            'quote': 'This is a test.',
            'comment': 'No author'
        })
        assert resp.status_code == 201
        resp = auth_client.post(url, {
            'lecturer': lecturer.pk,
            'author': other_user.pk,
            'quote': 'This is a test.',
            'comment': 'With author'
        })
        assert resp.status_code == 201
        # Assert that two quotes were created.
        quote1 = Quote.objects.filter(comment='No author')
        quote2 = Quote.objects.filter(comment='With author')
        assert quote1.exists()
        assert quote2.exists()
        # Assert that the author is the currently logged in user
        assert quote1.get().author == user
        assert quote2.get().author == user

    def test_auto_author_PUT(self, auth_client, quote, user):
        """Assert that the author is automatically set to the currently logged
        in user on PUT."""
        # Update existing quote with new comment and author
        url = reverse('api:quote_detail', args=(quote.pk,))
        other_user = mommy.make(User)
        data = {
            'lecturer': quote.lecturer.pk,
            'quote': quote.quote,
            'comment': 'newcomment',
            'author': other_user.pk,
        }
        resp = auth_client.put(url, json.dumps(data), 'application/json')
        # Assert that the PUT request was processed
        assert resp.status_code == 200
        # Comment should be changed, but not the author
        newquote = Quote.objects.get(pk=quote.pk)
        assert newquote.comment == 'newcomment'
        assert newquote.author == user

    def test_update_permissions(self, auth_client, quote):
        """It should only be possible to edit own quotes."""
        quote2 = mommy.make(Quote)
        url1 = reverse('api:quote_detail', args=(quote.pk,))
        url2 = reverse('api:quote_detail', args=(quote2.pk,))
        data = {
            'lecturer': quote.lecturer.pk,
            'quote': 'testquote',
            'comment': 'testcomment',
        }
        resp1 = auth_client.put(url1, json.dumps(data), 'application/json')
        resp2 = auth_client.put(url2, json.dumps(data), 'application/json')
        assert resp1.status_code == 200
        assert resp2.status_code == 403

    def test_author_change(self, auth_client, quote):
        """You should not be able to change the author of a quote."""
        url = reverse('api:quote_detail', args=(quote.pk,))
        another_user = mommy.make(User)
        data = {
            'lecturer': quote.lecturer.pk,
            'quote': quote.quote,
            'comment': quote.comment,
            'author': another_user.pk,
        }
        resp = auth_client.put(url, json.dumps(data), 'application/json')
        assert resp.status_code == 200, resp.content
        newquote = Quote.objects.get(pk=quote.pk)
        assert quote.author == newquote.author


class TestQuoteVote:

    @pytest.fixture
    def quote(self, db, user):
        return mommy.make(Quote, author=user)

    @pytest.fixture
    def url(self, quote):
        return reverse('api:quote_vote', args=(quote.pk,))

    def test_login_required(self, client, url):
        """It shouldn't be possible to vote on a quote without login."""
        resp = client.post(url, {'vote': 'up'})

        assert resp.status_code == 401
        data = json.loads(resp.content)
        assert data == {
            'detail': 'Anmeldedaten fehlen.',
        }

    @pytest.fixture
    def voter(self, auth_client, url, quote):
        def _check_vote(vote, vote_count, vote_sum):
            resp = auth_client.post(url, {'vote': vote})
            assert resp.status_code == 200
            assert json.loads(resp.content) == {
                'quote_pk': quote.pk,
                'vote': vote,
                'vote_count': vote_count,
                'vote_sum': vote_sum,
            }
            assert QuoteVote.objects.count() == vote_count
            assert quote.vote_sum() == vote_sum

        return _check_vote

    def test_voting(self, voter):
        voter('down', 1, -1)
        voter('up', 1, 1)
        voter('remove', 0, 0)
