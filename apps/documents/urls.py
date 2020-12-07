# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from django.conf.urls import url
from django.contrib import admin

from . import views

admin.autodiscover()

app_name = "documents"

# Dynamic pages
urlpatterns = [
    url(r"^$", views.DocumentcategoryList.as_view(), name="documentcategory_list"),
    url(r"^add/$", views.DocumentcategoryAdd.as_view(), name="documentcategory_add"),
    url(r"^(?P<category>[^\/]+)/$", views.DocumentList.as_view(), name="document_list"),
    url(r"^(?P<category>[^\/]+)/rss$", views.DocumentFeed(), name="document_feed"),
    url(
        r"^(?P<category>[^\/]+)/(?P<pk>-?\d+)/$",
        views.DocumentDownload.as_view(),
        name="document_download",
    ),
    url(
        r"^(?P<category>[^\/]+)/thumbnail/(?P<pk>-?\d+)/$",
        views.DocumentThumbnail.as_view(),
        name="document_thumbnail",
    ),
    url(
        r"^(?P<category>[^\/]+)/add/$", views.DocumentAdd.as_view(), name="document_add"
    ),
    url(
        r"^(?P<category>[^\/]+)/(?P<pk>-?\d+)/edit/$",
        views.DocumentEdit.as_view(),
        name="document_edit",
    ),
    url(
        r"^(?P<category>[^\/]+)/(?P<pk>-?\d+)/delete/$",
        views.DocumentDelete.as_view(),
        name="document_delete",
    ),
    url(
        r"^(?P<category>[^\/]+)/(?P<pk>-?\d+)/rate/$",
        views.DocumentRate.as_view(),
        name="document_rate",
    ),
    url(
        r"^(?P<category>[^\/]+)/ajax_rating_block/(?P<pk>-?\d+)/$",
        views.document_rating,
        name="document_rating_ajax",
    ),
]
