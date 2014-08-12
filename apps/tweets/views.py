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

        # Search tweets
        query = '#hsr -#maglev -#transrapid -#highspeedrail -#highspeedrail' \
                '-"high-speed rail" -HSRIsLate'
        results = api.search(q=query, count=20, result_type='recent', lang='de')
        search_tweets = [r.retweeted_status if hasattr(r, 'retweeted_status') else r
                         for r in results]

        # Combine with @studportal_hsr tweets
        user_tweets = api.user_timeline('studportal_hsr', count=10)
        tweets = sorted(search_tweets + user_tweets, key=lambda t: t.created_at, reverse=True)

        return tweets[:12]

    def get_context_data(self, **kwargs):
        context = super(TweetList, self).get_context_data(**kwargs)
        context['tweets'] = self.get_tweets()
        return context
