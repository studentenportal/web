# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

import json
import urllib

import pytest

from model_mommy import mommy

from apps.lecturers import models
from apps.front import models as front_models


class TestVoteQuote:

    """Test whether adding, changing or removing a vote via AJAX works."""

    def send_request(self, client, payload):
        """Send a dajaxice request with the specified payload. Return response."""
        url = '/dajaxice/apps.lecturers.vote_quote/'
        data = {'argv': json.dumps(payload)}
        return client.post(url,
            data=urllib.urlencode(data),
            content_type='application/x-www-form-urlencoded',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')

    @pytest.mark.django_db
    def test_voting(self, client):
        quote = mommy.make(models.Quote)
        front_models.User.objects.create_user('fakename', 'fake@example.com', 'fakepwd')

        client.login(username='fakename', password='fakepwd')

        response = self.send_request(client, {'vote': 'down', 'quote_pk': quote.pk})
        assert response.status_code == 200
        assert response.content != 'DAJAXICE_EXCEPTION', 'Dajaxice exception occured.'
        assert models.QuoteVote.objects.count() == 1
        assert quote.vote_sum() == -1

        response = self.send_request(client, {'vote': 'up', 'quote_pk': quote.pk})
        assert response.status_code == 200
        assert response.content != 'DAJAXICE_EXCEPTION', 'Dajaxice exception occured.'
        assert models.QuoteVote.objects.count() == 1
        assert quote.vote_sum() == 1

        response = self.send_request(client, {'vote': 'remove', 'quote_pk': quote.pk})
        assert response.status_code == 200
        assert response.content != 'DAJAXICE_EXCEPTION', 'Dajaxice exception occured.'
        assert models.QuoteVote.objects.count() == 0
        assert quote.vote_sum() == 0
