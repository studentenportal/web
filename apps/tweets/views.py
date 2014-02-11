# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

import os
import logging

from django.contrib import messages
from django.views.generic import TemplateView

import tweepy


logger = logging.getLogger(__name__)
env = os.environ.get


class TweetList(TemplateView):
    template_name = 'tweets/tweet_list.html'

    def get_tweets(self):
        """Fetch relevant tweets from TWitter and return them."""

        # Get application tokens
        consumer_token = env('TWITTER_CONSUMER_KEY')
        consumer_secret = env('TWITTER_CONSUMER_SECRET')
        if not (consumer_token and consumer_secret):
            logger.error('You need to set TWITTER_CONSUMER_KEY and ' +
                    'TWITTER_CONSUMER_SECRET env variables!')
            messages.add_message(self.request, messages.ERROR,
                    'Could not initialize Twitter API access.')
            return []

        # Get access tokens
        access_key = env('TWITTER_ACCESS_KEY')
        access_secret = env('TWITTER_ACCESS_SECRET')
        if not (access_key and access_secret):
            logger.error('You need to set TWITTER_ACCESS_KEY and ' +
                    'TWITTER_ACCESS_SECRET env variables!')
            messages.add_message(self.request, messages.ERROR,
                    'Could not initialize Twitter API access.')
            return []

        # Authenticate
        auth = tweepy.OAuthHandler(consumer_token, consumer_secret)
        api = tweepy.API(auth)

        query = '#hsr -#maglev -#transrapid -#highspeedrail -"high-speed rail" -#highspeedrail'
        results = api.search(q=query, rpp=50, result_type='recent', lang='de')
        tweets = (r.retweeted_status if hasattr(r, 'retweeted_status') else r for r in results)
        return tweets


    def get_context_data(self, **kwargs):
        context = super(TweetList, self).get_context_data(**kwargs)
        context['tweets'] = self.get_tweets()
        return context
