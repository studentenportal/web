# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

from django.conf.urls import patterns, url
from django.contrib import admin

from . import views

admin.autodiscover()

# Dynamic pages
urlpatterns = patterns('',
    url(r'^$', views.EventList.as_view(), name='event_list'),
    url(r'^add/$', views.EventAdd.as_view(), name='event_add'),
    url(r'^(?P<pk>-?\d+)/$', views.Event.as_view(), name='event_detail'),
    url(r'^(?P<pk>-?\d+)/edit/$', views.EventEdit.as_view(), name='event_edit'),
    url(r'^(?P<pk>-?\d+)/delete/$', views.EventDelete.as_view(), name='event_delete'),
    url(r'^calendar.ics$', views.EventCalendar.as_view(), name='event_calendar'),
)
