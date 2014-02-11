# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

import os
import sys

from django.core.management.base import NoArgsCommand

import tweepy

from apps.front.mixins import CommandOutputMixin


class Command(CommandOutputMixin, NoArgsCommand):
    help = 'Fetch ACCESS_KEY and ACCESS_SECRET from Twitter API.'

    def handle_noargs(self, **options):
        consumer_token = os.environ.get('TWITTER_CONSUMER_KEY')
        consumer_secret = os.environ.get('TWITTER_CONSUMER_SECRET')

        if not (consumer_token and consumer_secret):
            self.printE('You need to set TWITTER_CONSUMER_KEY and TWITTER_CONSUMER_SECRET first!')
            sys.exit(1)

        access_key = os.environ.get('TWITTER_ACCESS_KEY')
        access_secret = os.environ.get('TWITTER_ACCESS_SECRET')

        if access_key and access_secret:
            self.printO('TWITTER_ACCESS_KEY and TWITTER_ACCESS_SECRET ' +
                        'are already in your env variables!')
            return

        auth = tweepy.OAuthHandler(consumer_token, consumer_secret)

        try:
            redirect_url = auth.get_authorization_url()
        except tweepy.TweepError:
            self.printE('Error! Failed to get request token.')
            sys.exit(1)

        self.printO('Please visit {0} in your browser.'.format(redirect_url))
        verifier = raw_input('Enter PIN: ')

        try:
            auth.get_access_token(verifier)
        except tweepy.TweepError:
            self.printE('Error! Failed to get access token.')
            sys.exit(1)

        print('TWITTER_ACCESS_KEY: {}'.format(auth.access_token.key))
        print('TWITTER_ACCESS_SECRET: {}'.format(auth.access_token.secret))
