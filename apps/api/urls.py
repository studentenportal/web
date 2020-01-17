# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url

from rest_framework.urlpatterns import format_suffix_patterns

from apps.api import views


v1_api = patterns('',
    url(r'^$', views.api_root, name='api_root'),
    url(r'^users$', views.UserList.as_view(), name='user_list'),
    url(r'^users/(?P<pk>-?\d+)$', views.UserDetail.as_view(), name='user_detail'),
    url(r'^lecturers$', views.LecturerList.as_view(), name='lecturer_list'),
    url(r'^lecturers/(?P<pk>-?\d+)$', views.LecturerDetail.as_view(), name='lecturer_detail'),
    url(r'^quotes$', views.QuoteList.as_view(), name='quote_list'),
    url(r'^quotes/(?P<pk>-?\d+)$', views.QuoteDetail.as_view(), name='quote_detail'),
    url(r'^quotes/(?P<pk>-?\d+)/vote$', views.QuoteVote.as_view(), name='quote_vote'),
)

urlpatterns = patterns('',
    url(r'^', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^v1/', include(format_suffix_patterns(v1_api))),
)
