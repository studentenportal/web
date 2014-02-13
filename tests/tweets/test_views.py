# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

from datetime import datetime, timedelta
from collections import namedtuple

from django.test import TestCase
from django.core.urlresolvers import reverse

from mock import patch

import tweepy


class TweetListTest(TestCase):
    Tweet = namedtuple('Status', ['id', 'text', 'created_at', 'author'])
    Author = namedtuple('User', ['name', 'screen_name'])

    tweet1 = Tweet(id=431356619243266048,
                   text='"GeoDesign@HSR - why #Geodesign?" talk by Prof Carl Steinitz, ' +
                        'Harvard Univ., 19. Mai 2014, 17h, Aula #HSR Hochschule für ' +
                        'Technik Rapperswil',
                   created_at=datetime.now() - timedelta(hours=9),
                   author=Author(name='Stefan Keller', screen_name='sfkeller'))

    tweet2 = Tweet(id=433157201264656384,
                   text='Yay. Let\'s go for another semester #hsr',
                   created_at=datetime.now(),
                   author=Author(name='Michael Weibel', screen_name='weibelm'))

    tweet3 = Tweet(id=391948408346255360,
                   text='Ladezeit der Modul-Liste (https://studentenportal.ch/dokumente/ ) ' +
                        'von 3.8s auf 0.7s verringert :) #sql #optimierungen',
                   created_at=datetime.now(),
                   author=Author(name='VSHSRstudentenportal ', screen_name='studportal_hsr'))

    @patch.object(tweepy.API, 'search')
    @patch.object(tweepy.API, 'user_timeline')
    def test_tweet_display(self, tweepy_search, tweepy_user_timeline):
        #Arrange
        tweepy_search.return_value = [self.tweet1, self.tweet2]
        tweepy_user_timeline.return_value = [self.tweet3]

        #Act
        response = self.client.get(reverse('tweets:tweet_list'))

        #Assert
        assert len(response.context['tweets']) == 3
        self.assertContains('@weibelm', response)
        self.assertContains('@sfkeller', response)
