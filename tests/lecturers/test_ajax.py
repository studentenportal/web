# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

import json
import urllib

from django.test import TestCase

from model_mommy import mommy

from apps.lecturers import models
from apps.front import models as front_models


class VoteQuoteTest(TestCase):
    """Test whether adding, changing or removing a vote via AJAX works."""

    def sendRequest(self, payload):
        """Send a dajaxice request with the specified payload. Return response."""
        url = '/dajaxice/apps.lecturers.vote_quote/'
        data = {'argv': json.dumps(payload)}
        return self.client.post(url,
            data=urllib.urlencode(data),
            content_type='application/x-www-form-urlencoded',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')

    def testVoting(self):
        quote = mommy.make(models.Quote)
        front_models.User.objects.create_user('fakename', 'fake@example.com', 'fakepwd')

        self.client.login(username='fakename', password='fakepwd')

        response = self.sendRequest({'vote': 'down', 'quote_pk': quote.pk})
        assert response.status_code == 200
        assert response.content != 'DAJAXICE_EXCEPTION', 'Dajaxice exception occured.'
        assert models.QuoteVote.objects.count() == 1
        assert quote.vote_sum() == -1

        response = self.sendRequest({'vote': 'up', 'quote_pk': quote.pk})
        assert response.status_code == 200
        assert response.content != 'DAJAXICE_EXCEPTION', 'Dajaxice exception occured.'
        assert models.QuoteVote.objects.count() == 1
        assert quote.vote_sum() == 1

        response = self.sendRequest({'vote': 'remove', 'quote_pk': quote.pk})
        assert response.status_code == 200
        assert response.content != 'DAJAXICE_EXCEPTION', 'Dajaxice exception occured.'
        assert models.QuoteVote.objects.count() == 0
        assert quote.vote_sum() == 0
