# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

from django.conf.urls import patterns, url
from django.contrib import admin

from . import views

admin.autodiscover()

# Dynamic pages
urlpatterns = patterns('',
    url(r'^$', views.TweetList.as_view(), name='tweet_list'),
)
